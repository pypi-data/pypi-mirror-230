from __future__ import annotations

import glob
import logging as log
import math
import os
import textwrap
from pathlib import Path
from typing import List, Union

import numpy as np
import torch
from rich.progress import track
from scipy.io import loadmat, savemat
from scipy.spatial import ConvexHull
from torch.utils.data import Dataset

from lidar_camera_calibration.tools import dataset
from lidar_camera_calibration.tools import general as gn
from lidar_camera_calibration.tools import image, point_cloud2, rosbag
from lidar_camera_calibration.tools.timestamp_np import TimeStamp


def expected_directory_structure(root: Path = None) -> str:
    if root is None:
        root = "."
    else:
        assert root.is_dir(), f"Expected {root} to be a directory!"
    sub_dirs = ["raw", "compressed", "results"]
    sub_notes = [
        "Raw bag file(s) and camera_params.yaml initial calibration file.",
        "(generated) Data compressed into calibration frames that have been associated in time. Data files are .mat files with img, rPLl, and intensities fields.",
        "(generated) Directory containing the results of the calibration.",
    ]
    title = f"The expected directory structure within {root} is"
    lines = []
    max_len = 0
    for dir in sub_dirs:
        max_len = max(max_len, len(dir))
    for i in range(len(sub_dirs)):
        sub_dir = sub_dirs[i]
        sub_note = sub_notes[i]
        line_start = "{val:>{len}s}: ".format(len=max_len, val=sub_dir)

        line = f"{line_start}{sub_note}"
        line_wrapped = textwrap.wrap(
            line, width=80, subsequent_indent=" " * len(line_start)
        )
        for l in line_wrapped:
            lines.append(l)
    outstr = f"{title}:\n" + "\n".join(lines)
    return outstr


def is_file_with_extension(data_path: Path, ext: str) -> bool:
    if data_path.is_file():
        if data_path.name.split(".")[-1] in ext:
            return True
    return False


def expand_bag_path(data_path: Path) -> Union[Path, List[Path]]:
    """Guess which dataloader to use in case the user didn't specify with --dataloader flag.

    TODO: Avoid having to return again the data Path. But when guessing multiple .bag files or the
    metadata.yaml file, we need to change the Path specified by the user.
    """
    if is_file_with_extension(data_path, "bag"):
        return data_path
    elif data_path.is_dir():
        bagfiles = [Path(path) for path in glob.glob(os.path.join(data_path, "*.bag"))]
        if len(bagfiles) > 0:
            return bagfiles
    else:
        raise Exception(
            f'Input argument "data" does not point to a file or a directory. Ensure {data_path} exists!'
        )


def occlusionFilterHiddenPointRemoval(
    Tlc: np.ndarray, rPLl: np.ndarray, gamma: float = 1.0
) -> np.ndarray:
    """
    Katz, S., Tal, A., & Basri, R. (2007). Direct visibility of point sets. ACM Transactions on Graphics, 26(3), 1–10. https://doi.org/10.1145/1276377.1276430
    """

    if not isinstance(Tlc, np.ndarray):
        raise TypeError("Expected Tlc to be a numpy array")
    if not isinstance(rPLl, np.ndarray):
        raise TypeError("Expected rPLl to be a numpy array")
    if rPLl.shape[0] != 3:
        raise ValueError("Expected rPLl to have three rows")
    if Tlc.shape[0] != 4:
        raise ValueError("Expected Tlc to have four rows")
    if Tlc.shape[1] != 4:
        raise ValueError("Expected Tlc to have four columns")

    Rlc = Tlc[0:3, 0:3]
    rCLl = Tlc[0:3, [3]]
    rPCc = Rlc.T @ (rPLl - rCLl)

    npoints = rPLl.shape[1]

    isFrontOfCamera = rPCc[2, :] > 0
    idxFrontOfCamera = np.arange(npoints)[isFrontOfCamera]
    npoints_red = len(idxFrontOfCamera)

    # Calculate radius
    rPCc = rPCc[:, idxFrontOfCamera]
    nrPCc = np.linalg.norm(rPCc, axis=0)
    rmax = np.max(nrPCc)

    # Sphere radius
    r = rmax * (10**gamma)

    # Spherical flipping
    rSCc = rPCc + (2 * (r - nrPCc) * rPCc / nrPCc)
    rSCcp = np.hstack((rSCc, np.zeros((3, 1))))

    # Calculate convex hull
    hull = ConvexHull(rSCcp.T, qhull_options="Qt")
    idxIsValid_red = hull.vertices
    origin_idx = idxIsValid_red[idxIsValid_red == npoints_red]
    origin = rSCcp[:, origin_idx]
    assert np.linalg.norm(origin) < 1e-6, "Expected origin to be zero"
    idxIsValid_red = idxIsValid_red[idxIsValid_red != npoints_red]
    idxIsValid = idxFrontOfCamera[idxIsValid_red]

    return idxIsValid


class CalibrationFrame:
    def __init__(
        self,
        img: np.ndarray,
        rPLl: np.ndarray,
        intensities: np.ndarray,
        from_file: str = None,
    ):
        rPLl_size_str = "x".join([f"{s}" for s in rPLl.shape])
        assert (
            rPLl.shape[0] == 3
        ), f"Expected rPLl to be a 3xN array, but it has size {rPLl_size_str}"

        intensity_size_str = "x".join(f"{s}" for s in intensities.shape)
        assert (
            intensities.shape[0] == 1
        ), f"Expected intensity to be a 1xN array, but it has size {intensity_size_str}"

        assert (
            rPLl.shape[1] == intensities.shape[1]
        ), "Expected rPLl and intensities to have the same number of columns!"

        assert not np.any(np.isnan(img)), "Expected image to not have NaNs"
        assert not np.any(np.isnan(rPLl)), "Expected rPLl to not have NaNs"
        assert not np.any(
            np.isnan(intensities)
        ), "Expected intensities to not have NaNs"

        self.img = img
        self.rPLl = rPLl
        self.intensities = intensities
        self.from_file = from_file

        self.image_intensity_max = np.max(img)
        self.image_intensity_min = np.min(img)
        self.range_max = np.max(np.linalg.norm(rPLl, axis=0))
        self.range_min = np.min(np.linalg.norm(rPLl, axis=0))
        self.lidar_intensity_max = np.max(intensities)
        self.lidar_intensity_min = np.min(intensities)

    def toMATLAB(self, file_path: Path):
        data = dict()
        data["img"] = self.img
        data["rPLl"] = self.rPLl
        data["intensities"] = self.intensities
        savemat(gn.add_extension(file_path, "mat"), data)

    @staticmethod
    def fromMATLAB(file_path: Path) -> CalibrationFrame:
        file_path = gn.add_extension(file_path, "mat")
        assert os.path.isfile(file_path), f"Expected {file_path} to be a file!"

        data = loadmat(file_path)
        img = data["img"]
        rPLl = data["rPLl"]
        intensities = data["intensities"]
        return CalibrationFrame(img, rPLl, intensities, from_file=file_path)

    def size(self) -> int:
        return self.rPLl.shape[1]

    def __repr__(self) -> str:
        out = f"CalibrationFrame(img={self.img.shape}, rPLl={self.rPLl.shape}, intensities={self.intensities.shape})\n"
        out += f"  image intensity range=[{self.image_intensity_min}, {self.image_intensity_max}]\n"
        out += f"  lidar intensity range=[{self.lidar_intensity_min}, {self.lidar_intensity_max}]\n"
        out += f"  lidar distance range=[{self.range_min}, {self.range_max}]"
        return out

    def __getitem__(self, idx):
        if isinstance(idx, np.ndarray):
            idx = idx.flatten()
            return CalibrationFrame(
                self.img,
                self.rPLl[:, idx].reshape((3, -1)),
                self.intensities[:, idx].reshape((1, -1)),
            )
        elif isinstance(idx, int):
            return CalibrationFrame(
                self.img, self.rPLl[:, [idx]], self.intensities[:, [idx]]
            )
        else:
            raise Exception(f"Invalid index type {type(idx)}")


def compressed_data_to_calibration_frames(
    compressed_data_dir: Path,
) -> List[CalibrationFrame]:
    assert (
        compressed_data_dir.is_dir()
    ), f"Expected {compressed_data_dir} to be a directory!"
    mat_files = [
        os.path.join(compressed_data_dir, f)
        for f in os.listdir(compressed_data_dir)
        if os.path.isfile(os.path.join(compressed_data_dir, f))
        and f.startswith("frame-")
        and f.endswith(".mat")
    ]
    mat_files.sort()
    print(f"Retrieving calibration data from MATLAB files in {compressed_data_dir}.")
    data_frames = []
    for mat_file in track(
        mat_files,
        description=f"Loading {len(mat_files)} files.",
    ):
        data = CalibrationFrame.fromMATLAB(mat_file)
        data_frames.append(data)

    return data_frames


def calibration_frames_to_compressed_data(
    compressed_data_dir: Path, calframes: List[CalibrationFrame]
) -> None:
    assert (
        compressed_data_dir.is_dir()
    ), f"Expected {compressed_data_dir} to be a directory!"

    print(f"Saving data into {compressed_data_dir}")
    nframes = len(calframes)
    ndigits = int(math.ceil(math.log10(nframes)))
    for i in track(
        range(nframes),
        description="Writing calibration frames to MATLAB files.",
    ):
        calframe = calframes[i]
        filename = "frame-{val:0{ndigits}d}".format(ndigits=ndigits, val=i)
        filepath = os.path.join(compressed_data_dir, filename)
        calframe.toMATLAB(filepath)


def bagfile_to_calibration_frames(
    bag_file_path: Path,
    lidar_topic: str,
    image_topic: str,
    use_per_point_timestamp: bool = False,
) -> List[CalibrationFrame]:
    bag_files = expand_bag_path(bag_file_path)

    lidar_bag_data = rosbag.RosbagDataset(
        bag_files, lidar_topic, "lidar_topic", "sensor_msgs/msg/PointCloud2"
    )
    image_bag_data = rosbag.RosbagDataset(
        bag_files, image_topic, "image_topic", "sensor_msgs/msg/Image"
    )

    lidar_dataset_points = []
    lidar_dataset_time = []
    npoints = 0
    for lidar_msg in track(
        lidar_bag_data, description="Retrieving LiDAR data from bag file."
    ):
        lidar_points, lidar_time = point_cloud2.read_point_cloud(
            lidar_msg,
            read_intensity=True,
            use_per_point_timestamp=use_per_point_timestamp,
        )
        npoints += len(lidar_points)
        lidar_dataset_points.append(lidar_points)
        lidar_dataset_time.append(lidar_time)
    if use_per_point_timestamp:
        lidar_dataset_points = np.concatenate(lidar_dataset_points, axis=0)
    n_lidar_frames = len(lidar_bag_data)

    if use_per_point_timestamp:
        sec = np.concatenate([t.sec for t in lidar_dataset_time], axis=0)
        nsec = np.concatenate([t.nsec for t in lidar_dataset_time], axis=0)
    else:
        sec = np.hstack([t.sec for t in lidar_dataset_time])
        nsec = np.hstack([t.nsec for t in lidar_dataset_time])
    lidar_dataset_time = TimeStamp(sec, nsec)

    image_dataset_images = []
    image_dataset_time = []
    for image_msg in track(
        image_bag_data, description="Retrieving image data from bag file."
    ):
        image_data, image_time = image.read_image(image_msg)
        image_dataset_images.append(image_data)
        image_dataset_time.append(image_time)

    sec = np.hstack([t.sec for t in image_dataset_time])
    nsec = np.hstack([t.nsec for t in image_dataset_time])
    image_dataset_time = TimeStamp(sec, nsec)
    nimages = image_dataset_time.size()

    if use_per_point_timestamp:
        nidx = npoints
        lidar_str = "point"
    else:
        nidx = n_lidar_frames
        lidar_str = "frame"

    lidar_dataset_image_idx = np.zeros((nidx,), dtype=np.int64)

    t0_lidar = lidar_dataset_time.min()
    t0_camera = image_dataset_time.min()
    tf_camera = image_dataset_time.max()

    min_frequency = nimages / (tf_camera - t0_camera).as_seconds()
    print(f"Camera frame rate is {min_frequency} Hz")

    t0 = min(t0_lidar, t0_camera)
    lidar_dataset_time_ = (lidar_dataset_time - t0).as_seconds()
    image_dataset_time_ = (image_dataset_time - t0).as_seconds()

    for i in track(
        range(nidx),
        description=f"Building time correlation matrix between {nidx} LiDAR {lidar_str}s and {nimages} images.",
    ):
        lidar_time = lidar_dataset_time_[i]
        tshift = image_dataset_time_ - lidar_time
        tshift_abs = np.abs(tshift)
        idx_min = np.argmin(tshift_abs)
        if tshift_abs[idx_min] < (0.25 / min_frequency):
            lidar_dataset_image_idx[i] = idx_min
        else:
            lidar_dataset_image_idx[i] = -1

    print(f"Remove all LiDAR {lidar_str}s that are not associated with an image")
    lidar_idx_keep = lidar_dataset_image_idx != -1
    lidar_dataset_image_idx_red = lidar_dataset_image_idx[lidar_idx_keep]
    lidar_dataset_time_red = lidar_dataset_time_[lidar_idx_keep]
    if use_per_point_timestamp:
        lidar_dataset_points_red = lidar_dataset_points[lidar_idx_keep]
    else:
        lidar_dataset_points_red = [
            lidar_dataset_points[i]
            for i in range(len(lidar_idx_keep))
            if lidar_idx_keep[i]
        ]
    print(f"{lidar_dataset_time_red.size} LiDAR {lidar_str}s in reduced set")

    print(f"Find images that associated with a LiDAR {lidar_str}")
    unique, unique_indices, unique_inv = np.unique(
        lidar_dataset_image_idx_red, return_index=True, return_inverse=True
    )

    data_frames = []
    for i in track(
        range(len(unique)),
        description=f"Generating {len(unique)} data frames from {lidar_dataset_time_red.size} LiDAR {lidar_str}s.",
    ):
        j = unique[i]
        isLiDARInFrame = unique_inv == i

        img = image_dataset_images[j]
        if use_per_point_timestamp:
            rPLl = lidar_dataset_points_red[isLiDARInFrame, 0:3].T
            intensities = lidar_dataset_points_red[isLiDARInFrame, [3]].reshape((1, -1))
        else:
            rPLl = lidar_dataset_points_red[i][:, 0:3].T
            intensities = lidar_dataset_points_red[i][:, [3]].reshape((1, -1))

        datai = dataset.CalibrationFrame(
            img,
            rPLl,
            intensities,
        )
        data_frames.append(datai)
    return data_frames


# Datasets
class CalibrationDataset(Dataset):
    def __init__(
        self,
        calibration_frames: List[CalibrationFrame],
        max_lidar_intensity_to_keep: float = 100,
        max_lidar_range_to_keep: float = 15,
        max_samples: int = -1,
        use_occlusion_filtering=True,
        dtype=torch.float32,
        device: str = "cpu",
    ):
        self.max_lidar_intensity_to_keep = max_lidar_intensity_to_keep
        self.max_lidar_range_to_keep = max_lidar_range_to_keep

        self.calibration_frames = calibration_frames
        for i in range(len(calibration_frames)):
            calibration_frame = calibration_frames[i]
            dist = np.linalg.norm(calibration_frame.rPLl, axis=0)
            idx_keep = (
                (0 <= calibration_frame.intensities)
                & (calibration_frame.intensities <= self.max_lidar_intensity_to_keep)
                & (dist <= self.max_lidar_range_to_keep)
            )
            self.calibration_frames[i] = calibration_frame[idx_keep]

        image_intensity_max = []
        image_intensity_min = []
        range_max = []
        range_min = []
        lidar_intensity_max = []
        lidar_intensity_min = []
        for calibration_frame in self.calibration_frames:
            image_intensity_max.append(calibration_frame.image_intensity_max)
            image_intensity_min.append(calibration_frame.image_intensity_min)
            range_max.append(calibration_frame.range_max)
            range_min.append(calibration_frame.range_min)
            lidar_intensity_max.append(calibration_frame.lidar_intensity_max)
            lidar_intensity_min.append(calibration_frame.lidar_intensity_min)

        self.image_intensity_max = max(image_intensity_max)
        self.image_intensity_min = min(image_intensity_min)
        self.lidar_intensity_max = max(lidar_intensity_max)
        self.lidar_intensity_min = min(lidar_intensity_min)
        self.range_max = max(range_max)
        self.range_min = min(range_min)
        self.Tlc = None
        self.use_occlusion_filtering = use_occlusion_filtering

        self.dtype = dtype
        self.device = device
        self.max_samples = max_samples
        if max_samples > 0:
            log.info(
                "Building training dataset where each frame has a maximum "
                + "of {} random samples from each image frame.".format(max_samples)
            )
        else:
            log.info("Building training dataset using all in each frame samples.")

    def setCurrentPose(self, Tlc: torch.Tensor):
        if not isinstance(Tlc, torch.Tensor):
            raise Exception(f"Expected Tlc to be a torch.Tensor, but got {type(Tlc)}")
        self.Tlc = Tlc.detach().cpu()

    def __len__(self) -> int:
        return len(self.calibration_frames)

    def __getitem__(self, idx):
        calibration_data = self.calibration_frames[idx]

        if self.use_occlusion_filtering:
            if self.Tlc is None:
                raise Exception("Expected Tlc to be set!")
            idxIsValid = occlusionFilterHiddenPointRemoval(
                self.Tlc.numpy(), calibration_data.rPLl, gamma=1.0
            )
            calibration_data = calibration_data[idxIsValid]

        if self.max_samples > 0 and calibration_data.size() > self.max_samples:
            nValid = calibration_data.size()
            idx_choose = np.random.choice(nValid, self.max_samples)
            calibration_data = calibration_data[idx_choose]

        img = torch.from_numpy(calibration_data.img).to(
            device=self.device, dtype=self.dtype
        )
        rPLl = torch.from_numpy(calibration_data.rPLl).to(
            device=self.device, dtype=self.dtype
        )
        intensities = torch.from_numpy(calibration_data.intensities).to(
            device=self.device, dtype=self.dtype
        )

        data = dict()
        data["img"] = img
        data["rPLl"] = rPLl
        data["intensities"] = intensities
        return data


def my_collate(batch) -> List:
    data = []
    for packet in batch:
        data.append(packet)
    return data

import json
import logging
import math
import os
import sys
from datetime import datetime
from typing import Callable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.optim as optim
import yaml
from rich.progress import Progress
from scipy.io import savemat
from torch.utils.data import DataLoader

from lidar_camera_calibration.tools import dataset
from lidar_camera_calibration.tools import general as gn
from lidar_camera_calibration.tools import model as camLiDARMI
from lidar_camera_calibration.tools import plot
from lidar_camera_calibration.tools import rotations as rot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

log = logging.getLogger(__name__)


def convert_numpy_to_list(data):
    if isinstance(data, dict):
        return {key: convert_numpy_to_list(value) for key, value in data.items()}
    elif isinstance(data, (list, tuple)):
        return [convert_numpy_to_list(item) for item in data]
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data


def convert_numpy_to_yaml_dict(x: np.ndarray) -> dict:
    assert len(x.shape) == 2, "Expected numpy object to be 2d!"
    data = dict()
    data["rows"] = x.shape[0]
    data["cols"] = x.shape[1]
    data["data"] = x.flatten().tolist()
    return data


class LiDARCameraCalibrationResults:
    def __init__(
        self,
        Tlc: torch.Tensor,
        camera_matrix: torch.Tensor,
        distortion_coefficients: torch.Tensor,
        is_camera_learned: bool,
        is_using_Lie_group: bool,
        num_epochs: int,
        learning_rate: float,
        calibration_data_dir: str,
        image_width: int,
        image_height: int,
        generator_file: str = sys._getframe(1).f_code.co_name,
        git_id: str = gn.get_git_revision_short_hash(),
    ):
        # Set attributes
        self.Tlc = Tlc.detach().cpu()
        self.camera_matrix = camera_matrix.detach().cpu()
        self.distortion_coefficients = distortion_coefficients.detach().cpu()
        self.is_camera_learned = bool(is_camera_learned)
        self.is_using_Lie_group = bool(is_using_Lie_group)
        self.num_epochs = int(num_epochs)
        self.learning_rate = float(learning_rate)
        self.calibration_data_dir = str(calibration_data_dir)
        self.image_width = int(image_width)
        self.image_height = int(image_height)

        # Optionally set attributes
        self.generator_file = str(generator_file)
        self.git_id = str(git_id)

        # Internally set attributes
        self.date_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    def toNumpyDict(self) -> dict:
        toSave = dict()
        # Set attributes
        toSave["Tlc"] = self.Tlc.numpy()
        toSave["camera_matrix"] = self.camera_matrix.numpy()
        toSave["distortion_coefficients"] = self.distortion_coefficients.numpy()
        toSave["is_camera_learned"] = self.is_camera_learned
        toSave["is_using_Lie_group"] = self.is_using_Lie_group
        toSave["num_epochs"] = self.num_epochs
        toSave["learning_rate"] = self.learning_rate
        toSave["calibration_data_dir"] = self.calibration_data_dir
        toSave["image_width"] = self.image_width
        toSave["image_height"] = self.image_height

        # Optionally set attributes
        toSave["git_id"] = self.git_id
        toSave["generator_file"] = self.generator_file

        # Internally set attributes
        toSave["date_time"] = self.date_time
        return toSave

    def toOpenCVCameraIntrinsicsYAML(
        self, filepath: str, camera_name: str = "camera_0"
    ):
        filepath = gn.add_extension(filepath, "yaml")

        if self.is_camera_learned:
            outstr = "# Automatically generated intrinsics from joint calibration\n"
        else:
            outstr = "# Automatically copied intrinsics from camera intrinsics calibration, located in {}\n".format(
                os.path.join(self.calibration_data_dir, "raw")
            )
        outstr = outstr + "#%12s: %s \n" % ("by", self.generator_file)
        outstr = outstr + "#%12s: %s \n" % ("on", self.date_time)
        outstr = outstr + "#%12s: %s \n" % ("git-id", self.git_id)
        outstr = outstr + "#%12s: %s \n" % ("calib. data", self.calibration_data_dir)
        names = [
            "camera_matrix",
            "distortion_coefficients",
        ]
        intrinics = dict()
        tosave = self.toNumpyDict()
        intrinics["image_width"] = self.image_width
        intrinics["image_height"] = self.image_height
        intrinics["camera_name"] = camera_name

        for name in names:
            intrinics[name] = convert_numpy_to_yaml_dict(tosave[name])

        intrinics_str = yaml.dump(intrinics, default_flow_style=None, sort_keys=False)
        content = outstr + "\n\n" + intrinics_str
        with open(filepath, "w") as file:
            file.write(content)

    def toYAML(self, filepath: str):
        filepath = gn.add_extension(filepath, "yaml")
        data = self.toNumpyDict()
        data = convert_numpy_to_list(data)
        with open(filepath, "w") as file:
            yaml.dump(data, file, default_flow_style=None, sort_keys=False)

    def toJSON(self, filepath: str):
        filepath = gn.add_extension(filepath, "json")
        data = self.toNumpyDict()
        data = convert_numpy_to_list(data)
        with open(filepath, "w") as file:
            json.dump(data, file)

    def toMATLAB(self, filepath: str):
        filepath = gn.add_extension(filepath, "mat")
        savemat(filepath, self.toNumpyDict())


def get_factors(x: int) -> List[int]:
    factors_ = []
    for i in range(1, x + 1):
        if x % i == 0:
            factors_.append(i)
    return factors_


def calibrate(
    calibration_frames: List[dataset.CalibrationFrame],
    calibration_data_dir: str,
    eta0: torch.Tensor,
    max_samples: int = 5000,
    num_epochs: int = 300,
    plot_iter: bool = False,
    plot_correlation: bool = True,
    learn_camera: bool = True,
    learning_rate: float = 1e-3,
    max_lidar_range: float = 15,
    entropy_approx: str = "trapz",
    compile_cost_func_model: bool = False,
    device: str = "cpu",
    dtype=torch.float64,
) -> Tuple[
    LiDARCameraCalibrationResults, camLiDARMI.CameraLiDARMutualInformation, DataLoader
]:
    """_summary_

    Args:
        calibration_data_dir (str): Directory that contains calibration data folders:
            calibration_data_dir/raw directory with
            calibration_data_dir/compressed
            calibration_data_dir/results
        eta0 (torch.Tensor): Initial pose [rCLl; Thetalc], where rCLl ∈ ℝ^3 is the translational vector and
            Thetalc ∈ ℝ^3 is the Euler angles that define the relative rotation
        max_samples (int, optional): _description_. Defaults to 5000.
        num_epochs (int, optional): _description_. Defaults to 300.
        plot_iter (bool, optional): _description_. Defaults to False.
        plot_correlation (bool, optional): _description_. Defaults to True.
        learn_camera (bool, optional): _description_. Defaults to True.
        learning_rate (float, optional): _description_. Defaults to 1e-3.
        max_lidar_range (float, optional): _description_. Defaults to 15.
        device (str, optional): _description_. Defaults to "cpu".
        dtype (_type_, optional): _description_. Defaults to torch.float64.

    Returns:
        Tuple[ LiDARCameraCalibrationResults, camLiDARMI.CameraLiDARMutualInformation, DataLoader ]: _description_
    """

    assert os.path.isdir(calibration_data_dir), "Expected {} to be a directory.".format(
        calibration_data_dir
    )
    raw_data_dir = os.path.join(calibration_data_dir, "raw")
    matlab_compressed_data_dir = os.path.join(calibration_data_dir, "compressed")
    calibration_results_dir = os.path.join(calibration_data_dir, "results")

    assert os.path.isdir(raw_data_dir), (
        "Expected " "raw" " to be a directory within {}".format(calibration_data_dir)
    )
    assert os.path.isdir(matlab_compressed_data_dir), (
        "Expected "
        "compressed"
        " to be a directory within {}".format(matlab_compressed_data_dir)
    )

    if not os.path.isdir(calibration_results_dir):
        os.mkdir(calibration_results_dir)

    train_data = dataset.CalibrationDataset(
        calibration_frames,
        max_samples=max_samples,
        max_lidar_range_to_keep=max_lidar_range,
    )

    ndata = len(train_data)
    factors = get_factors(ndata)
    j = 0
    while len(factors) == 2:
        j += 1
        factors = get_factors(ndata + 1)

    factors_oi = [f for f in factors if f < 16]
    batch_size_train = max(factors_oi)

    train_loader = DataLoader(
        train_data,
        batch_size=batch_size_train,
        shuffle=True,
        collate_fn=dataset.my_collate,
    )

    # Load intrinsics
    camera_params_name = "camera_params.yaml"

    camera_params_file = os.path.join(raw_data_dir, camera_params_name)
    assert os.path.isfile(
        camera_params_file
    ), "Expected {} to be a file containing the camera calibration parameters. Could not find the file in {}".format(
        camera_params_name, raw_data_dir
    )

    Tlc0 = rot.getTransformationMatrixFromVector(eta0)
    Rlc0 = Tlc0[0:3, 0:3]
    rCLl0 = Tlc0[0:3, [3]]
    train_data.setCurrentPose(Tlc0)

    model = camLiDARMI.CameraLiDARMutualInformation(
        rCLl0,
        Rlc0,
        camera_params_file,
        use_Lie_group=False,
        learn_camera=learn_camera,
        max_range=max_lidar_range,
        entropy_approx=entropy_approx,
        device=device,
        dtype=dtype,
        image_intensity_max=train_data.image_intensity_max,
        image_intensity_min=train_data.image_intensity_min,
        lidar_intensity_max=train_data.lidar_intensity_max,
        lidar_intensity_min=train_data.lidar_intensity_min,
    )
    if compile_cost_func_model:
        fname = "cost function model"
        log.info(f"Compiling {fname}")
        try:
            model = torch.compile(model, mode="reduce-overhead")
            log.info(f"Compiled {fname}")
        except Exception as e:
            log.error(f"Failed to compile {fname}: {e}")

    if plot_correlation:
        plot.showLiDARCameraCorrelation(1, train_loader, model, "pre-calibration")
        plt.pause(0.01)

    Kc, dist_theta = model.getCamera()

    train_iter_loss = []
    train_iter_counter = []
    train_epoch_loss = []
    train_epoch_counter = []

    num_batchs = len(train_loader)
    num_frames = len(train_loader.dataset)
    batch_size = train_loader.batch_size
    ndigits_epoch = math.ceil(math.log10(num_epochs))
    ndigits_frames = math.ceil(math.log10(num_frames))

    # Calibration
    def train(epoch: int, iterAdvance: Callable):
        ndisp = 10
        nmod = math.ceil(len(train_loader) / float(ndisp))

        epoch_cost = 0
        npoints = 0
        npoints_batch = 0

        train_data.setCurrentPose(model.getRelativePose().detach().cpu())
        for batch_idx, data in enumerate(train_loader):
            optimizer.zero_grad()
            Il, Ii = model.forward(data)
            loss = model.cost(Il, Ii)

            Tlc_pre = model.getRelativePose().detach().cpu()
            assert (
                not Tlc_pre.isnan().any()
            ), "Relative pose is nan before optimisation step"

            loss.backward()
            loss_eval = loss.item()

            train_data.setCurrentPose(model.getRelativePose().detach().cpu())

            Tlc_post = model.getRelativePose().detach().cpu()
            assert (
                not Tlc_post.isnan().any()
            ), "Relative pose is nan after optimisation step"

            optimizer.step()
            npoints_batch = len(Il)
            npoints = npoints + npoints_batch

            if batch_idx % nmod == 0:
                res_line = "Train Epoch: {epoch:{ndigits_epoch}d} of {num_epoch} [{batch_num:{ndigits_frames}d}/{num_frames:{ndigits_frames}d} ({percent_batchs:3.0f}%)] Loss: {loss:.6g}".format(
                    ndigits_epoch=ndigits_epoch,
                    ndigits_frames=ndigits_frames,
                    epoch=epoch,
                    num_epoch=num_epochs,
                    num_frames=num_frames,
                    batch_num=batch_idx * batch_size,
                    percent_batchs=100.0 * batch_idx / num_batchs,
                    loss=loss_eval,
                )
                print(res_line)

            train_iter_loss.append(loss_eval)
            epoch_cost += npoints_batch * loss_eval
            epoch_val = (
                1.0 * (batch_idx * batch_size_train)
                + ((epoch - 1) * len(train_loader.dataset))
            ) / len(train_loader.dataset)
            train_iter_counter.append(epoch_val)

            iterAdvance()

        epoch_cost = epoch_cost / npoints
        train_epoch_loss.append(epoch_cost)
        train_epoch_counter.append(epoch)

    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)

    if plot_iter:
        fig, ax = plt.subplots()  # Create figure and axes

        (line_iter,) = ax.plot(
            train_iter_counter, -np.array(train_iter_loss), "r-", label="Train iter MI"
        )
        (line_epoch,) = ax.plot(
            train_epoch_counter, -np.array(train_epoch_loss), "b-x", label="Train MI"
        )
        ax.set_ylabel("Mutual Information")
        ax.set_xlabel("No. of epochs")
        ax.legend()
        pose_plot = plot.PlotLidarCameraPose(3, Tlc0.detach().cpu().numpy())

    with Progress(transient=False) as progress:
        task = progress.add_task("Training model", total=num_epochs * num_batchs)

        def iterAdvance():
            progress.advance(task)

        for epoch in range(1, 1 + num_epochs):
            train(epoch, iterAdvance)
            if plot_iter:
                line_iter.set_data(train_iter_counter, -np.array(train_iter_loss))

                line_epoch.set_data(train_epoch_counter, -np.array(train_epoch_loss))
                ax.relim()  # Recalculate the data limits
                ax.autoscale_view()  # Auto-scale the axes
                fig.canvas.draw()  # Redraw the figure
                pose_plot.updateBasisPlot(
                    model.getRelativePose().detach().cpu().numpy()
                )

                plt.pause(0.01)

    # Post Calibration
    Tlc_final = model.getRelativePose().detach().cpu()

    Kc, dist_theta = model.getCamera()

    res = LiDARCameraCalibrationResults(
        Tlc_final,
        Kc,
        dist_theta,
        model.learn_camera,
        model.use_Lie_group,
        epoch,
        learning_rate,
        calibration_data_dir,
        model.cam_param["image_width"],
        model.cam_param["image_height"],
        generator_file=__file__,
    )

    parameterisation = "Lie" if model.use_Lie_group else "Euler"
    calibration_type = "joint" if model.learn_camera else "pose"
    output_file_name = "calibration_{}_{}_{}".format(
        calibration_type, parameterisation, epoch
    ).lower()
    output_file = os.path.join(calibration_results_dir, output_file_name)
    res.toMATLAB(output_file)
    res.toYAML(output_file)

    # Output OpenCV data
    output_file_name = f"camera_params_{epoch}"
    output_file = os.path.join(calibration_results_dir, output_file_name)
    res.toOpenCVCameraIntrinsicsYAML(output_file)

    if plot_correlation:
        plot.showLiDARCameraCorrelation(4, train_loader, model, "post-calibration")

    if plot_correlation or plot_iter:
        # Keep displaying all figures until the user closes them
        plt.show(block=True)

    return res, model, train_loader

from __future__ import annotations

import math
from typing import Tuple

import torch

from lidar_camera_calibration.tools import general as gn
from lidar_camera_calibration.tools import rotations as rot


class CameraLiDARMutualInformation(torch.nn.Module):
    def __init__(
        self,
        rCLl0: torch.Tensor,
        Rlc0: torch.Tensor,
        camera_params_file: str,
        use_occlusion_filtering: bool = True,
        nbins: int = 50,
        use_Lie_group: bool = False,
        learn_camera: bool = False,
        max_range: float = 15,
        dtype=torch.float64,
        device: str = "cpu",
        entropy_approx: str = "trapz",
        image_intensity_max: float = 255,
        image_intensity_min: float = 0,
        lidar_intensity_max: float = 255,
        lidar_intensity_min: float = 0,
    ):
        super().__init__()
        if use_Lie_group:
            self.Mlc = torch.eye(4, dtype=dtype, device=device)
            self.Mlc[0:3, 0:3] = Rlc0
            self.Mlc[0:3, [3]] = rCLl0
            self.xi = torch.nn.Parameter(
                torch.zeros((6, 1), dtype=dtype, device=device)
            )
        else:
            self.eta = torch.nn.Parameter(
                torch.vstack((rCLl0, rot.rot2vec(Rlc0))).to(dtype=dtype, device=device)
            )

        self.use_Lie_group = use_Lie_group
        self.learn_camera = learn_camera
        self.entropy_approx = entropy_approx
        self.use_occlusion_filtering = use_occlusion_filtering

        cam = gn.readCameraIntrinsicsFromYaml(camera_params_file)

        Kc = torch.from_numpy(cam["camera_matrix"]).to(device=device, dtype=dtype)
        dist_theta = torch.from_numpy(cam["distortion_coefficients"]).to(
            device=device, dtype=dtype
        )

        self.cam_param_file = camera_params_file
        self.cam_param = cam
        cam_fx = Kc[0, 0]
        cam_fy = Kc[1, 1]
        cam_cx = Kc[0, 2]
        cam_cy = Kc[1, 2]

        if self.learn_camera:
            self.cam_fx = torch.nn.Parameter(cam_fx)
            self.cam_fy = torch.nn.Parameter(cam_fy)
            self.cam_cx = torch.nn.Parameter(cam_cx)
            self.cam_cy = torch.nn.Parameter(cam_cy)
            self.dist_theta = torch.nn.Parameter(dist_theta)
        else:
            self.dist_theta = dist_theta
            self.cam_fx = cam_fx
            self.cam_fy = cam_fy
            self.cam_cx = cam_cx
            self.cam_cy = cam_cy

        self.max_range = max_range
        self.sigma = 2
        self.nbins = nbins
        # Integration range. Log scaling from [0,255] such that more control points are closer to 0 than to 255

        assert 0 <= lidar_intensity_min, "Invalid minimum lidar intensity"
        assert (
            lidar_intensity_min < lidar_intensity_max
        ), "Invalid lidar intensity range"
        xx = (
            torch.logspace(
                math.log10(lidar_intensity_min + 1),
                math.log10(lidar_intensity_max + 1),
                nbins,
                device=device,
                dtype=dtype,
            )
            - 1
        )

        assert 0 <= image_intensity_min, "Invalid minimum image intensity"
        assert (
            image_intensity_min < image_intensity_max
        ), "Invalid image intensity range"
        yy = (
            torch.logspace(
                math.log10(image_intensity_min + 1),
                math.log10(image_intensity_max + 1),
                nbins,
                device=device,
                dtype=dtype,
            )
            - 1
        )

        self.xx = xx
        self.yy = yy

        self.dtype = dtype
        self.device = device

    def getCamera(self) -> torch.Tensor:
        Kc = torch.eye(3, device=self.device, dtype=self.dtype)
        Kc[0, 0] = self.cam_fx
        Kc[1, 1] = self.cam_fy
        Kc[0, 2] = self.cam_cx
        Kc[1, 2] = self.cam_cy

        return Kc, self.dist_theta

    def getRelativePose(self) -> torch.Tensor:
        if self.use_Lie_group:
            Tlc = self.Mlc @ rot.expmSE3(self.xi)
        else:
            Tlc = rot.getTransformationMatrixFromVector(self.eta)
        return Tlc

    def forwardSingle(self, frame: dict) -> Tuple[torch.Tensor, torch.Tensor]:
        rPLl = frame["rPLl"].to(device=self.device, dtype=self.dtype)
        image = frame["img"].to(device=self.device, dtype=self.dtype)

        assert (
            image.shape[0] == self.cam_param["image_height"]
        ), "Expected image height({}) to be identical to the sensor height({}) from the file {}.".format(
            image.shape[0], self.cam_param["image_height"], self.cam_param_file
        )
        assert (
            image.shape[1] == self.cam_param["image_width"]
        ), "Expected image width({}) to be identical to the sensor width({}) from the file {}.".format(
            image.shape[1], self.cam_param["image_width"], self.cam_param_file
        )

        I_lidar = frame["intensities"].to(device=self.device, dtype=self.dtype)
        nrPLl = torch.norm(rPLl, dim=0)
        isConsidered = nrPLl < self.max_range

        rPLl = rPLl[:, isConsidered]
        I_lidar = I_lidar[0, isConsidered]

        Kc, dist_theta = self.getCamera()
        Tlc = self.getRelativePose()
        rQOi = gn.lidar2pix(Tlc, rPLl, Kc, dist_theta)
        isValidU = (0 <= rQOi[0, :]) & (rQOi[0, :] <= image.shape[1]).flatten()
        isValidV = (0 <= rQOi[1, :]) & (rQOi[1, :] <= image.shape[0]).flatten()
        isValid = (isValidU & isValidV).flatten()

        rQOi = rQOi[:, isValid]
        I_lidar = I_lidar[isValid]

        I_image = gn.GaussianInterpolant(image, self.sigma, rQOi)

        return I_lidar, I_image

    def forward(self, frames: list) -> Tuple[torch.Tensor, torch.Tensor]:
        I_lidar = []
        I_image = []
        for frame in frames:
            Il, Ii = self.forwardSingle(frame)
            I_lidar.append(Il.flatten())
            I_image.append(Ii.flatten())
        return torch.hstack(I_lidar), torch.hstack(I_image)

    def cost(self, I_lidar, I_image) -> torch.Tensor:
        np = I_lidar.shape[0]
        if np == 0:
            return torch.tensor([torch.inf], device=self.device, dtype=self.dtype)
        lidar_IQR = gn.interQuartileRange(I_lidar)
        camera_IQR = gn.interQuartileRange(I_image)

        lidar_STD = torch.std(I_lidar)
        camera_STD = torch.std(I_image)

        camera_K = 0.9 * torch.min(camera_STD, camera_IQR / 1.34) * np ** (-1.0 / 5)
        lidar_K = 0.9 * torch.min(lidar_STD, lidar_IQR / 1.34) * np ** (-1.0 / 5)

        S = torch.tensor(
            [[lidar_K, 0], [0, camera_K]], device=self.device, dtype=self.dtype
        )
        mu = torch.vstack((I_lidar, I_image))
        logW = -(torch.ones((1, np), device=self.device, dtype=self.dtype) * np).log()

        if self.entropy_approx == "trapz":
            # Support of lidar
            x = self.xx
            log_pxi = gn.logGaussianMixtureAtXSingleCov(
                x.reshape((1, self.nbins)),
                I_lidar.reshape((1, np)),
                lidar_K.reshape((1, 1)),
                logW,
            )

            # Support of camera
            y = self.yy
            log_pyi = gn.logGaussianMixtureAtXSingleCov(
                y.reshape((1, self.nbins)),
                I_image.reshape((1, np)),
                camera_K.reshape((1, 1)),
                logW,
            )

            [X, Y] = torch.meshgrid(x, y)
            xy = torch.vstack([X.flatten(), Y.flatten()])
            log_pxyi = gn.logGaussianMixtureAtXSingleCov(xy, mu, S, logW)
            log_pxyi = log_pxyi.reshape((self.nbins, self.nbins))

            fHX = -log_pxi * log_pxi.exp()
            fHY = -log_pyi * log_pyi.exp()
            fHXY = -log_pxyi * log_pxyi.exp()

            HX = torch.trapz(fHX, x)
            HY = torch.trapz(fHY, y)
            HXY = torch.trapz(torch.trapz(fHXY, x), y)
        elif self.entropy_approx == "upper_bound":
            HX = gn.entropyUpperBoundGaussianMixtureSingleCov(
                I_lidar.reshape((1, np)), lidar_K.reshape((1, 1)), logW
            )
            HY = gn.entropyUpperBoundGaussianMixtureSingleCov(
                I_image.reshape((1, np)), camera_K.reshape((1, 1)), logW
            )
            HXY = gn.entropyUpperBoundGaussianMixtureSingleCov(mu, S, logW)
        elif self.entropy_approx == "taylor_zeroth":
            HX = gn.entropyTaylorZerothGaussianMixtureSingleCov(
                I_lidar.reshape((1, np)), lidar_K.reshape((1, 1)), logW
            )
            HY = gn.entropyTaylorZerothGaussianMixtureSingleCov(
                I_image.reshape((1, np)), camera_K.reshape((1, 1)), logW
            )
            HXY = gn.entropyTaylorZerothGaussianMixtureSingleCov(mu, S, logW)
        else:
            assert 0, "Unknown entropy approximation " + self.entropy_approx
        MI = HX + HY - HXY

        return -MI

from typing import Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import torch


def showLiDARCameraCorrelation(fig_num: int, train_loader, model, title: str):
    I_lidar = []
    I_image = []
    for batch_idx, data in enumerate(train_loader):
        Il, Ii = model.forward(data)
        I_lidar.append(Il.flatten())
        I_image.append(Ii.flatten())

    I_lidar, I_image = (
        torch.hstack(I_lidar).detach().cpu(),
        torch.hstack(I_image).detach().cpu(),
    )

    hist_lidar = torch.histogram(I_lidar, density=True)
    hist_image = torch.histogram(I_image, density=True)

    plt.figure(fig_num)
    plt.subplot(1, 4, 1)
    x = (hist_lidar[1][0:-1] + hist_lidar[1][1:]) / 2
    plt.plot(x, hist_lidar[0])
    plt.xlabel("Intensity")
    plt.title("LiDAR")
    plt.ylim([0, hist_lidar[0].max() * 1.25])

    plt.subplot(1, 4, 2)
    x = (hist_image[1][0:-1] + hist_image[1][1:]) / 2
    plt.plot(x, hist_image[0])
    plt.xlabel("Intensity")
    plt.title("Camera")
    plt.ylim([0, hist_image[0].max() * 1.25])

    plt.subplot(1, 4, (3, 4))

    plt.hist2d(
        I_image.numpy(),
        I_lidar.numpy(),
        density=True,
        bins=100,
        cmap=mpl.colormaps["plasma"],
    )
    plt.ylabel("LiDAR Intensities")
    plt.xlabel("Camera Intensities")

    plt.suptitle(title, fontsize=14)


class PlotLidarCameraPose:
    def __init__(self, fig_num: int, Tlc0: np.ndarray):
        self.fig_num = fig_num

        if not isinstance(Tlc0, np.ndarray):
            raise TypeError("Expected Tlc0 to be a numpy array")

        self.Tlc0 = Tlc0
        self.Tlc = Tlc0
        self.fig = plt.figure(fig_num)
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.set_xlabel("$l_{1} - [m]$")
        self.ax.set_ylabel("$l_{2} - [m]$")
        self.ax.set_zlabel("$l_{3} - [m]$")

        # Plot the transformed basis vectors
        self.plot_lidar_basis, lims_base = self.generateBasisPlot(
            self.ax, "l", np.eye(4)
        )
        self.plot_camera_init_basis, lims_init = self.generateBasisPlot(
            self.ax, "c_0", self.Tlc0
        )
        self.plot_camera_basis, _ = self.generateBasisPlot(self.ax, "c", self.Tlc)
        self.ax.relim()  # Recalculate the data limits
        self.ax.autoscale_view()  # Auto-scale the axes

        self.axis_labels = ["x", "y", "z"]
        self.origin_lims = dict()
        for i in self.axis_labels:
            self.origin_lims[i] = lims_base[i] + lims_init[i]
        self.ax.set_xlim(min(self.origin_lims["x"]), max(self.origin_lims["x"]))
        self.ax.set_ylim(min(self.origin_lims["y"]), max(self.origin_lims["y"]))
        self.ax.set_zlim(min(self.origin_lims["z"]), max(self.origin_lims["z"]))

        self.ax.set_title("LiDAR-Camera Pose")
        self.fig.canvas.draw()
        plt.pause(0.01)

    @staticmethod
    def generateBasisPlot(
        ax, quiver_label: str, Tlc: np.ndarray, handles: dict = None
    ) -> Tuple[dict, dict]:
        # Plot the transformed basis vectors
        if handles is None:
            handles = dict()
        else:
            assert isinstance(handles, dict), "Expected handles to be a dictionary"

        rCLl = Tlc[0:3, [3]]
        lims = dict()
        labels = ["x", "y", "z"]
        for i in range(3):
            lims[f"{labels[i]}"] = [rCLl[i]]

        for i in range(3):
            v = np.zeros((3, 1))
            v[i] = 1
            v = Tlc[0:3, 0:3] @ v
            for j in range(3):
                lims[f"{labels[i]}"].append(rCLl[j] + v[j])
            h = ax.quiver(
                rCLl[0], rCLl[1], rCLl[2], v[0], v[1], v[2], color=["r", "g", "b"][i]
            )
            handles[f"quiver_{quiver_label}_{i+1}"] = h
        # handles[f"quiver_{quiver_label}_text"] = ax.text(
        #     x=rCLl[0], y=rCLl[1], z=rCLl[2], s="$\{" + quiver_label + "\}$", color="k"
        # )
        return handles, lims

    def updateBasisPlot(self, Tlc: np.ndarray):
        if not isinstance(Tlc, np.ndarray):
            raise TypeError("Expected Tlc to be a numpy array")
        self.Tlc = Tlc

        rCLl = Tlc[0:3, [3]]
        lims = dict()
        labels = ["x", "y", "z"]
        for i in range(3):
            lims[f"{labels[i]}"] = [rCLl[i]]

        for i in range(3):
            v = np.zeros((3, 1))
            v[i] = 1
            v = Tlc[0:3, 0:3] @ v

            self.plot_camera_basis[f"quiver_c_{i+1}"].remove()
            for j in range(3):
                lims[f"{labels[i]}"].append(rCLl[j] + v[j])

            h = self.ax.quiver(
                rCLl[0], rCLl[1], rCLl[2], v[0], v[1], v[2], color=["r", "g", "b"][i]
            )
            self.plot_camera_basis[f"quiver_c_{i+1}"] = h

        # self.plot_camera_basis["quiver_c_text"].remove()
        # self.plot_camera_basis["quiver_c_text"] = self.ax.text(
        #     rCLl[0], rCLl[1], rCLl[2], "$\{c\}$", color="k"
        # )

        for i in self.axis_labels:
            lims[i] = self.origin_lims[i] + lims[i]
        self.ax.set_xlim(min(lims["x"]), max(lims["x"]))
        self.ax.set_ylim(min(lims["y"]), max(lims["y"]))
        self.ax.set_zlim(min(lims["z"]), max(lims["z"]))
        self.ax.autoscale_view()  # Auto-scale the axes
        self.fig.canvas.draw()

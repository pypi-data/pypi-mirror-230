# lidar-camera-calibration

[TOC]

## Summary

A PyTorch LiDAR camera calibration project that maximises the mutual information between LiDAR and image intensities.

## Installation

```bash
pip install lidar_camera_calibration
```

## Usage

The `run_calibration.py` script expects a path to be passed that contains the directory with the calibration data. For a calibration dataset, the following directory structure is expected:

```bash
.
├── raw
│   ├── camera_config.yaml
│   ├── camera_params.yaml
│   ├── calibrationBagFile-0.bag (Works with single bag too)
│   ├── ...
│   └── calibrationBagFile-K.bag
├── compressed (generated)
│   ├── frame-000.mat
│   ├── ...
│   └── frame-NNN.mat
└── results (generated)
    ├── calibration_joint_euler_<nepochs>.mat
    ├── calibration_joint_euler_<nepochs>.yaml
    └── camera_params.yaml
```

## TODO

- [ ] Deal with occlusion.

## Theory

Given a calibrated camera and LiDAR, we seek to find the relative pose between both sensors.

The camera relates a point $P_{j}$ in the world to pixel locations. Each world point can be expressed with respect to the camera centre $C$ and camera coordinate system $\{c\}$ as $\mathbf{r}_{P_{j}/C}^c\in\mathbb{R}^3$ while each pixel $Q_j$ in the camera image can be expressed with respect to the image origin $O$ in the image basis $\{i\}$ as $\mathbf{r}_{Q_j/O}^{i}\in \mathbb{R}^2$. The world points can be related to image pixels through the following map:

$$
\begin{align}
\mathbf{r}_{Q_{j}/O}^{i} & =
\texttt{vec2pix}(
\mathbf{r}_{P_{j}/C}^{c}
; \mathbf{K}, \boldsymbol\theta_\text{dist.}).
\end{align}
$$

### Approximating mutual information

Mutual information measures the information that a pair of random variables, $X$ and $Y$, share: It measures how much knowing one of these variables reduces uncertainty about the other. For example, if $X$ and $Y$ are independent, then knowing $X$ does not give any information about $Y$ and vice versa, so their mutual information is zero. At the other extreme, if $X$ is a deterministic function of $Y$ and $Y$ is a deterministic function of $X$ then all information conveyed by $X$ is shared with $Y$: knowing $X$ determines the value of $Y$ and vice versa.

Mutual information can be expressed in terms of entropies of the marginal distributions $p_{X},\,p_{Y}$ and the entropy of the joint distribution $p_{XY}$. The mutual information is defined as follows:

$$
\mathcal{I}_{XY} = \mathcal{H}[p_{X}] + \mathcal{H}[p_{Y}] - \mathcal{H}[p_{XY}],
$$

where

$$
\begin{align}
\mathcal{H}[p_{X}] & = -\int_{\mathcal{X}} \log(p_{X}(x))p_{X}(x)\mathrm{d}x
\\
\mathcal{H}[p_{Y}] & = -\int_{\mathcal{Y}} \log(p_{Y}(y))p_{Y}(y)\mathrm{d}y
\\
\mathcal{H}[p_{XY}] & = -\int_{\mathcal{Y}}\int_{\mathcal{X}} \log(p_{XY}(x,y))p_{XY}(x,y)\mathrm{d}x\mathrm{d}y
\end{align}
$$

The cross-entropy ranges over the pixel ranges $[0,255)$. Therefore, we choose to integrate using a trapezoid integration scheme where:

$$
\mathcal{H}[p_{X}] \approx H[p_{X}] =
\dfrac{\Delta x}{2}
\bigg(
\log(p_{X}(x_0))p_{X}(x_0)
+ \log(p_{X}(x_N))p_{X}(x_N)
+ 2\sum_{i=1}^{N-1} \log(p_{X}(x_i))p_{X}(x_i)
\bigg)
$$

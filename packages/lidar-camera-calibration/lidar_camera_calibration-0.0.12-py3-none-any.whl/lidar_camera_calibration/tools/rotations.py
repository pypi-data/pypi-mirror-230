import torch


def hatso3(u: torch.Tensor) -> torch.Tensor:
    dtype = u.dtype
    device = u.device
    S = torch.zeros((3, 3), dtype=dtype, device=device)

    S[1, 0] = u[2]
    S[2, 0] = -u[1]

    S[0, 1] = -u[2]
    S[2, 1] = u[0]

    S[0, 2] = u[1]
    S[1, 2] = -u[0]
    return S


def expmSO3(xi: torch.Tensor) -> torch.Tensor:
    assert (xi.shape[0] == 3) & (xi.shape[1] == 1), "Expected xi to be a 3x1 vector"
    assert not xi.isnan().any(), "Expected xi not to be nan"
    dtype = xi.dtype
    device = xi.device
    mu = xi.norm()
    nxi = xi / mu
    if mu < torch.finfo(dtype).smallest_normal:
        nxi = torch.tensor([[1], [0], [0]], device=device, dtype=dtype)
    a = torch.cos(mu)
    b = torch.sin(mu)
    I = torch.eye(3, device=device, dtype=dtype)
    R = a * I + (nxi @ nxi.T) * (1 - a) - hatso3(nxi) * b
    assert not R.isnan().any()
    return R


def JrSO3(xi: torch.Tensor) -> torch.Tensor:
    assert (xi.shape[0] == 3) & (xi.shape[1] == 1), "Expected xi to be a 3x1 vector"
    assert not xi.isnan().any(), "Expected xi not to be nan"
    dtype = xi.dtype
    device = xi.device
    mu = xi.norm()
    nxi = xi / mu
    if mu < torch.finfo(dtype).smallest_normal:
        nxi = torch.tensor([[1], [0], [0]], device=device, dtype=dtype)
    a = torch.sinc(mu / torch.pi)

    if mu < 1:
        b = a * (torch.sin(mu) / (1 + torch.cos(mu)))
    else:
        b = (1 - torch.cos(mu)) / mu
    I = torch.eye(3, device=device, dtype=dtype)
    J = a * I + (nxi @ nxi.T) * (1 - a) - hatso3(nxi) * b
    assert not J.isnan().any()
    return J


def expmSE3(nu: torch.Tensor) -> torch.Tensor:
    assert (nu.shape[0] == 6) & (nu.shape[1] == 1), "Expected nu to be a 6x1 vector"
    assert not nu.isnan().any(), "Expected nu not to be nan"
    dtype = nu.dtype
    device = nu.device
    v = nu[0:3, [0]]
    w = nu[3:6, [0]]

    S = torch.eye(4, device=device, dtype=dtype)
    S[0:3, 0:3] = expmSO3(w)
    S[0:3, [3]] = JrSO3(-w) @ v

    assert not S.isnan().any()

    return S


def rot_x(x: torch.Tensor) -> torch.Tensor:
    R = torch.zeros([3, 3], dtype=x.dtype, device=x.device)
    R[1, 1] = torch.cos(x)
    R[2, 2] = torch.cos(x)
    R[2, 1] = torch.sin(x)
    R[1, 2] = -torch.sin(x)
    R[0, 0] = 1
    return R


def rot_y(x: torch.Tensor) -> torch.Tensor:
    R = torch.zeros([3, 3], dtype=x.dtype, device=x.device)
    R[0, 0] = torch.cos(x)
    R[2, 2] = torch.cos(x)
    R[0, 2] = torch.sin(x)
    R[2, 0] = -torch.sin(x)
    R[1, 1] = 1
    return R


def rot_z(x: torch.Tensor) -> torch.Tensor:
    R = torch.zeros([3, 3], dtype=x.dtype, device=x.device)
    R[0, 0] = torch.cos(x)
    R[1, 1] = torch.cos(x)
    R[1, 0] = torch.sin(x)
    R[0, 1] = -torch.sin(x)
    R[2, 2] = 1
    return R


def rot_zyx(Thetanc: torch.Tensor) -> torch.Tensor:
    phi = Thetanc[0, 0]
    theta = Thetanc[1, 0]
    psi = Thetanc[2, 0]

    Rx = rot_x(phi)
    Ry = rot_y(theta)
    Rz = rot_z(psi)

    return Rz @ Ry @ Rx


def rot2vec(Rnc: torch.Tensor) -> torch.Tensor:
    phi = torch.atan2(Rnc[2, 1], Rnc[2, 2])

    cos_theta = torch.sqrt(Rnc[1, 0] ** 2 + Rnc[0, 0] ** 2)
    sin_theta = -Rnc[2, 0]
    theta = torch.atan2(sin_theta, cos_theta)

    psi = torch.atan2(Rnc[1, 0], Rnc[0, 0])

    thetanc = torch.empty([3, 1], dtype=Rnc.dtype, device=Rnc.device)
    thetanc[0] = phi
    thetanc[1] = theta
    thetanc[2] = psi

    return thetanc


def getTransformationMatrixFromVector(eta: torch.Tensor) -> torch.Tensor:
    assert (
        eta.shape[0] == 6 and eta.shape[1] == 1
    ), "Expected eta to have shape [6x1] but it had {}".format(eta.shape)

    Tlc = torch.eye(4, device=eta.device, dtype=eta.dtype)
    rCLl = eta[0:3, [0]]
    Thetalc = eta[3:6, [0]]
    Tlc[0:3, 0:3] = rot_zyx(Thetalc)
    Tlc[0:3, [3]] = rCLl
    return Tlc

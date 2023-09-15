import math
import sys
from typing import Callable

import torch


class TorchNetworkToVecParams:
    def __init__(self, model):
        self.model = model

    def getAsVec(self) -> torch.Tensor:
        parameters = torch.cat([param.view(-1) for param in self.model.parameters()])
        return parameters.reshape([-1, 1])

    def setAsVec(self, x: torch.Tensor) -> None:
        parameters_old = torch.cat(
            [param.view(-1) for param in self.model.parameters()]
        )
        nd = parameters_old.numel()
        assert (
            x.shape[0] == nd
        ), "Expected x to have dimension [{}x1], but it is of {}".format(nd, x.shape)
        assert (
            x.shape[1] == 1
        ), "Expected x to have dimension [{}x1], but it is of {}".format(nd, x.shape)

        # Update the associated model parameters
        index = 0
        for param in self.model.parameters():
            num_elements = param.numel()
            param.data.copy_(x[index : index + num_elements].view_as(param))
            index += num_elements


class OptimRes:
    def __init__(
        self,
        iter: int,
        x: torch.Tensor,
        f: torch.Tensor,
        g: torch.Tensor,
        R: torch.Tensor,
        termination_notes: str = "none",
        algorithmName: str = sys._getframe(1).f_code.co_name,
    ):
        self.iter = iter
        self.x = x
        self.f = f
        self.g = g
        self.R = R
        self.termination_notes = termination_notes
        self.algorithmName = algorithmName

    def __str__(self) -> str:
        outstr = "Algorithm {} terminated after {} iterations!\nNotes:\n{}\nx={}\nf={}\ng={}\n".format(
            self.algorithmName,
            self.iter,
            self.termination_notes,
            self.x.cpu().numpy().T,
            self.f,
            self.g.cpu().numpy().T,
        )
        return outstr


def DBFGSTrustQR(
    fcn: Callable,
    x0: torch.Tensor,
    max_iter=200,
    grad_tol=1e-6,
    rel_grad_tol=1e-6,
    rel_fun_tol=1e-6,
    DeltaMax=1e16,
) -> OptimRes:
    """Minimise fcn(x) by using symmetric rank two updates to compute the
        inverse Hessian factored as Hinv = R.'*R, where R is an upper
        triangular matrix using Damped BFGS updates

    Args:
        fcn (Callable): _description_
        x0 (torch.Tensor): _description_
        max_iter (int, optional): _description_. Defaults to 200.
        grad_tol (_type_, optional): _description_. Defaults to 1e-6.
        rel_grad_tol (_type_, optional): _description_. Defaults to 1e-6.
        rel_fun_tol (_type_, optional): _description_. Defaults to 1e-6.
        DeltaMax (_type_, optional): _description_. Defaults to 1e16.

    Returns:
        torch.Tensor: _description_
    """
    assert (
        not x0.requires_grad
    ), "Expected auto grad to not be enabled for input variable."
    device = x0.device
    dtype = x0.dtype
    n = x0.shape[0]
    R = torch.eye(n, dtype=dtype, device=device)

    nhist = max(10, round(math.sqrt(n)))
    # Function evaluation history
    f_hist = torch.zeros(
        [
            nhist,
        ],
        dtype=dtype,
        device=device,
    )
    # Newton decrement history
    nd_hist = torch.zeros(
        [
            nhist,
        ],
        dtype=dtype,
        device=device,
    )

    f_hist[:] = float("nan")
    nd_hist[:] = float("nan")

    x = x0
    f, g = fcn(x)
    f_hist[0] = f
    nd_hist[0] = 1

    header = " %6s %13s %10s %13s %15s %15s %15s %15s" % (
        "Iter",
        "Func-count",
        "f(x)  ",
        "TR radius",
        "Newton Dec.",
        "1st order opt.",
        "rho  ",
        "Dec.  ",
    )
    line = "%6d %13d %10g %13g %15g %15g %15g %15g"
    blockHeight = 50

    Delta = 1

    print(header)

    j = 0
    for i in range(0, max_iter):
        # Calculate scaled search direction
        # Based on Chapter 7.7.3 Solving Diagonal Trust-Region subproblems in
        # Conn, A. R., Gould, N. I., Toint, P. L., 2000. Trust region methods. SIAM.
        gs = R @ g
        ngs = gs.norm()
        if ngs > Delta:
            ps = -gs * Delta / ngs
            nps = Delta
        else:
            ps = -gs
            nps = ngs
        # Actual search direction
        p = R.T @ ps

        # The Newton decrement squared is g.'*inv(H)*g = p.'*H*p
        lambdaSQ = -torch.dot(p.flatten(), g.flatten())

        # Predicted reduction f - fp, where fp = f + p'*g + 0.5*p'*H*p
        ps2 = torch.dot(ps.flatten(), ps.flatten())
        dm = -(torch.dot(gs.flatten(), ps.flatten()) + 0.5 * ps2)

        assert (
            dm >= 0
        ), "Expected there to be a reduction in cost from the scaled trust region step"

        xn = x + p
        fn, gn = fcn(xn)
        y = gn - g
        rho = (f - fn) / dm

        if rho > 0.5:
            if nps <= 0.8 * Delta:
                # Leave trust region radius at current value
                pass
            else:
                Delta = min(2 * Delta, DeltaMax)
        elif 0.25 <= rho and rho <= 0.4:
            # Leave trust region radius at current value
            pass
        else:
            # Decrease trust region radius
            Delta = 0.25 * Delta
            # more effective than 0.5*Delta

        if Delta < 1e-10:
            return OptimRes(i, x, f, g, R, "Trust region too small!")

        # Termination conditions
        isWithinNewtonDecrement = f_hist.mean() < grad_tol

        if isWithinNewtonDecrement:
            return OptimRes(
                i,
                x,
                f,
                g,
                R,
                "CONVERGED: Newton decrement below threshold after {} iterations and {} steps.".format(
                    i, j
                ),
            )

        # Step update
        if rho > 1e-8:
            if j + 1 % blockHeight == 0:
                print("\n")
                print(header)

            print(line % (j, i, fn, Delta, lambdaSQ, max(abs(g)), rho, f - fn))
            f_hist = torch.hstack(
                [torch.tensor(f, dtype=dtype, device=device), f_hist[:-1]]
            )
            nd_hist = torch.hstack(
                [torch.tensor(lambdaSQ, dtype=dtype, device=device), nd_hist[:-1]]
            )
            j = j + 1
            x = xn
            f = fn
            g = gn

        # Damped BFGS inverse square-root inverse Hessian update
        yp = torch.dot(y.flatten(), p.flatten())
        if i == 0:
            # Initialisation
            y2 = torch.dot(y.flatten(), y.flatten())
            # See eq 6.20 of Nocedal and Wright Numerical Optimisation
            R = torch.sqrt((yp / y2).abs()) * torch.eye(n, dtype=dtype, device=device)
        else:
            # Update
            if yp < 0.2 * ps2:
                theta = 0.2 * ps2 / (ps2 - yp)
                r = theta * y + (1 - theta) * torch.linalg.solve_triangular(
                    R, ps, upper=True
                )
            else:
                r = y
            rp = torch.dot(r.flatten(), p.flatten())
            if rp > 0:
                w = 1 / rp
                C = torch.eye(n, dtype=dtype, device=device) - w * p @ r.T
                A = torch.vstack((R @ C.T, torch.sqrt(w) * p.T))
                Q, R = torch.linalg.qr(A, mode="r")
                R = R[0:n, 0:n]
                assert not torch.any(torch.isnan(R))

    return OptimRes(i, x, f, g, R, "Maximum iterations reached!")


from typing import Callable, NoReturn, Self
import numpy as np

from garch_loss import (garch_loss_gen, garch_process)
from model import (Minimize)
from scipy.optimize import minimize

class GARCH(Minimize):
    """
    Generalized Autoregressive Conditional Heteroskedasticity (GARCH) model.

    This model is used to model time series data with volatility clustering.
    """

    def __init__(
            self: Self,
            p: int = 1,
            q: int = 1,
            **kwargs,
        ):

        super().__init__(loss=garch_loss_gen(p=p, q=q), **kwargs)

        # Constant attributes
        self._p = p # p the lag of r_t
        self._q = q # q the lag of s_t

        theta0 = [0.005] + [0.1 for i in range(p)] + [0.1 for i in range(p)] + [0.85 for i in range(q)]
        self._theta = np.array(theta0)

        def ub(x):
            return 1.0 - x[1] - 0.5*x[2] - x[3]

        def lb1(x):
            return x[1] + x[2]

        def lb2(x):
            return x[0]

        def lb3(x):
            return x[1]

        def lb4(x):
            return x[3]

        self.constraints = [
            {'type':'ineq', 'fun':ub},
            {'type':'ineq', 'fun':lb1},
            {'type':'ineq', 'fun':lb2},
            {'type':'ineq', 'fun':lb3},
            {'type':'ineq', 'fun':lb4}
        ]

    @property
    def theta(self: Self) -> np.ndarray[float]:
        """
        Get the parameters for the GARCH model.
        """

        return self._theta

    @theta.setter
    def theta(self: Self, theta: np.ndarray[float]) -> NoReturn:
        """
        Set the parameters for the GARCH model.
        """

        self._theta = np.array(theta)

    @property
    def p(self: Self) -> int:
        """
        Get "p" parameter of the GARCH model (i.e. the lag of the r_t term of
        the GARCH model.
        """

        return self._p

    @property
    def q(self: Self) -> int:
        """
        Get "q" parameter of the GARCH model (i.e. the lag of the s_t term of
        the GARCH model.
        """

        return self._q


    def fit(self: Self, train_data):  # train_data: [rT,...r0]
        tr = train_data

        # Optimize using scipy and save theta
        tr_losses = []
        j = 0
        count = 0
        while j < self.max_iterations:
            j += 1

            res = minimize(
                self.loss(tr),
                self.theta,
                method=self.method,
                options={'disp': False},
                constraints=self.constraints
            )

            theta = res.x
            self.theta = theta

            tr_loss = self.loss(tr)(theta)
            tr_losses.append(tr_loss)

            # Early stopping
            if self.stopping_early is True:
                if j > 10:
                    if abs(tr_losses[-1] - tr_losses[-2]) / tr_losses[-2] < 0.0001:
                        count += 1
                        if count >= 2:
                            return tr_losses
        return tr_losses


    def sigma(self, y):
        # test data: [rT,...r0]
        s = garch_process(y, self.theta, self.p, self.q)
        return np.array(s)
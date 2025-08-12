
import numpy as np
import scipy.optimize

from dcc_loss import dcc_loss_gen
from model import (Minimize)
from typing import (Callable, NoReturn, Self)


class DCC(Minimize):
    """
    Dynamic Conditional Correlation (DCC) model for multivariate time series.
    """

    def __init__(self: Self, **kwargs) -> NoReturn:

        super().__init__(loss=dcc_loss_gen(), **kwargs)

        self._ab = np.array([0.5, 0.5])

        def ub(x):
            return 1.0 - x[0] - x[1]

        def lb1(x):
            return x[0]

        def lb2(x):
            return x[1]

        self.constraints = [
            {'type':'ineq', 'fun':ub},
            {'type':'ineq', 'fun':lb1},
            {'type':'ineq', 'fun':lb2}
        ]


    @property
    def ab(self: Self) -> np.ndarray[float]:
        """
        Get the parameters for the DCC model.
        """

        return self._ab

    @ab.setter
    def ab(self: Self, ab: np.ndarray[float]) -> NoReturn:
        """
        Set the parameters for the DCC model.
        """

        self._ab = ab


    def fit(self: Self, train_data: np.ndarray) -> list[float]:
        """
        Fit the DCC model to the training data.

        :param train_data: The training data to fit the model to.
        :return: A list of losses for each iteration.
        """

        # numpy.array([
        #   [e1_T, ..., e1_0],
        #   [e2_T,  ..., e2_0],
        #   ...,
        #   [en_T,  ..., en_0]
        # ])
        tr: np.ndarray = train_data

        # Optimize using scipy and save theta
        tr_losses: list[float] = []

        j: int = 0
        count: int = 0

        while j < self.max_iterations:
            j += 1

            res: np.ndarray[float] = scipy.optimize.minimize(
                self.loss(tr),
                np.array(self.ab),
                constraints=self.constraints,
                method=self.method,
                options={
                    'disp': True
                },
            )

            ab = res.x
            self.ab = ab

            tr_loss: float = self.loss(tr)(ab)
            tr_losses.append(tr_loss)

            if self.stopping_early is True:
                if j > 10:
                    loss_final = tr_losses[-1]
                    loss_prev  = tr_losses[-2]

                    if abs(loss_final - loss_prev) / loss_prev < 0.0001:
                        count += 1

                        if count >= 2:
                            print("Early Stopping...")
                            return tr_losses

        return tr_losses

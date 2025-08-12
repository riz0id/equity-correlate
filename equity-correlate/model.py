
import numpy as np
import scipy.optimize
from typing import (Callable, NoReturn, Self)

class Minimize(object):
    """
    Base class for the GARCH and DCC models.
    """

    def __init__(
            self: Self,
            loss: Callable[[float], float],
            max_iterations: int = 3,
            method: str = 'SLSQP',
            stopping_early: bool = True,
        ) -> NoReturn:

        self._loss = loss
        self._max_iterations = max_iterations
        self._method = method
        self._stopping_early = stopping_early


    @property
    def loss(self: Self) -> Callable[[np.ndarray], float]:
        """
        Get the loss function for the GARCH model.
        """

        return self._loss

    @loss.setter
    def loss(self: Self, f: Callable[[np.ndarray], float]) -> NoReturn:
        """
        Set the loss function for the GARCH model.
        """

        self._loss = f


    @property
    def max_iterations(self: Self) -> int:
        """
        Get the maximum number of iterations for the GARCH model.
        """

        return self._max_iterations

    @max_iterations.setter
    def max_iterations(self: Self, n: int) -> NoReturn:
        """
        Set the maximum number of iterations for the GARCH model.
        """

        if n < 1:
            raise ValueError("Maximum iterations must be at least 1.")
        else:
            self._max_iterations = n


    @property
    def method(self: Self) -> str:
        """
        Get the optimization method used by the GARCH model.
        """

        return self._method

    @method.setter
    def method(self: Self, method: str) -> NoReturn:
        """
        Set the optimization method used by the GARCH model.
        """

        self._method = method


    @property
    def stopping_early(self: Self) -> bool:
        """
        Get whether the model should stop early.
        """

        return self._stopping_early

    @stopping_early.setter
    def stopping_early(self: Self, x: bool) -> NoReturn:
        """
        Set whether the model should stop early.
        """

        self._stopping_early = x


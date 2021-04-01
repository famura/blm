import numpy as np
from tabulate import tabulate
from tqdm import tqdm
from typing import Union, Optional


class BacklashModel:
    """
    Model for backlash with linear decision boundaries as introduced in [1]

    .. note::
        The current implementation only support one-dimensional data.

    .. seealso::
        [1] J. Vörös, "Modeling and identification of systems with backlash", Automatica, 2008
    """

    def __init__(
        self,
        m_lo: Union[float, int, list, np.ndarray],
        m_up: Union[float, int, list, np.ndarray],
        c_lo: Union[float, int, list, np.ndarray],
        c_up: Union[float, int, list, np.ndarray],
        x_init: Optional[Union[float, int, list, np.ndarray]] = None,
    ):
        """
        Constructor

        :param m_lo: slope of the lower threshold
        :param m_up: slope of the upper threshold
        :param c_lo: offset of the lower threshold
        :param c_up: offset of the upper threshold
        :param x_init: initial state
        """
        self.m_lo = None
        self.m_up = None
        self.c_lo = None
        self.c_up = None
        self._x_prev = None

        self.reset(m_lo, m_up, c_lo, c_up, x_init)

    def __call__(self, u: np.ndarray):
        """
        Apply backlash it the input is not smaller than the lower threshold or bigger than the upper threshold.
        The last state is memorized and only updated if one of the thresholds is exceeded.
        Effectively creating a time-discrete nonlinear dynamical system of first order.

        :param u: input
        :return: output (same space as the input), potentially with backlash
        """
        if u <= self.z_lo:
            # Input smaller than "left" linear boundary in the u-x plane
            x_curr = self.m_lo * (u + self.c_lo)
            self._x_prev = x_curr
        elif u >= self.z_up:
            # Input larger than "right" linear boundary in the u-x plane
            x_curr = self.m_up * (u - self.c_up)
            self._x_prev = x_curr
        else:
            # In the backlash zone
            x_curr = self._x_prev

        return x_curr

    def __str__(self):
        """ Get the information formatted in a table. """
        return tabulate([["m_lo", self.m_lo], ["m_up", self.m_up], ["c_lo", self.c_lo], ["c_up", self.c_up]])

    def reset(
        self,
        m_lo: Optional[Union[float, int, list, np.ndarray]] = None,
        m_up: Optional[Union[float, int, list, np.ndarray]] = None,
        c_lo: Optional[Union[float, int, list, np.ndarray]] = None,
        c_up: Optional[Union[float, int, list, np.ndarray]] = None,
        x_init: Optional[Union[float, int, list, np.ndarray]] = None,
    ):
        """
        Optionally reset the constants and/or the initial state. Also check the values.

        :param m_lo: slope of the lower threshold
        :param m_up: slope of the upper threshold
        :param c_lo: offset of the lower threshold
        :param c_up: offset of the upper threshold
        :param x_init: initial state
        """
        # Optionally set
        if m_lo is not None:
            self.m_lo = np.atleast_1d(np.asarray(m_lo, dtype=np.float_))
        if m_up is not None:
            self.m_up = np.atleast_1d(np.asarray(m_up, dtype=np.float_))
        if c_lo is not None:
            self.c_lo = np.atleast_1d(np.asarray(c_lo, dtype=np.float_))
        if c_up is not None:
            self.c_up = np.atleast_1d(np.asarray(c_up, dtype=np.float_))
        if x_init is not None:
            self._x_prev = np.atleast_1d(np.asarray(x_init, dtype=np.float_))

        # Check the values
        if np.any(self.m_lo == 0):
            raise ValueError("m_lo must not be zero!")
        if np.any(self.m_up == 0):
            raise ValueError("m_up must not be zero!")
        if np.any(self.c_lo < 0):
            raise ValueError("c_lo must be non-negative!")
        if np.any(self.c_up < 0):
            raise ValueError("c_up must be non-negative!")

    @property
    def z_lo(self) -> np.ndarray:
        """ Get the intersection of the lower threshold line with the u-axis (abscissa). """
        return self._x_prev / self.m_lo - self.c_lo

    @property
    def z_up(self) -> np.ndarray:
        """ Get the intersection of the upper threshold line with the u-axis (abscissa). """
        return self._x_prev / self.m_up + self.c_up

    @staticmethod
    def h(s: np.ndarray) -> np.ndarray:
        """ Step function, see (4) in [1] """
        s_copy = s.copy()
        s_copy[s > 0] = 0
        s_copy[s <= 0] = 1
        return s_copy

    def f_1(self, u: np.ndarray, x_prev: np.ndarray):
        """ Feature function, see (5) in [1] """
        return self.h((self.m_lo * u + self.m_lo * self.c_lo - x_prev) / self.m_lo)

    def f_2(self, u: np.ndarray, x_prev: np.ndarray):
        """ Feature function, see (6) in [1] """
        return self.h((x_prev - self.m_up * u + self.m_up * self.c_up) / self.m_up)

    def fit(self, u: np.ndarray, x: np.ndarray, x_prev: np.ndarray, num_epoch: int = 20):
        """
        Fit the internal parameters to the data using iterative lease squares regression (i.e., MLE).

        :param u: inputs of shape [num_samples, dim_data]
        :param x: outputs of shape [num_samples, dim_data] (same space as the input), potentially with backlash
        :param x_prev: outputs of shape [num_samples, dim_data] (same space as the input), potentially with backlash
        :param num_epoch: number of iterations over the whole data set
        """
        # Verify shapes
        u, x, x_prev = np.atleast_1d(u), np.atleast_1d(x), np.atleast_1d(x_prev)
        if not u.shape == x.shape == x_prev.shape:
            raise ValueError(
                f"The shapes of u, x, and x_prev must be equal, but are {u.shape}, {x.shape}, and {x_prev.shape}!"
            )

        # Initialize
        self.reset(m_lo=1, m_up=1, c_lo=1e-2, c_up=1e-2, x_init=x_prev[0])

        for _ in tqdm(range(num_epoch), total=num_epoch, desc="Fitting", leave=False):
            # Construct feature matrix
            phi = np.concatenate(
                [u * self.f_1(u, x_prev), self.f_1(u, x_prev), u * self.f_2(u, x_prev), -self.f_2(u, x_prev)], axis=1
            )

            # Construct target matrix
            targets = x - x_prev * (1 - self.f_1(u, x_prev)) * (1 - self.f_2(u, x_prev))

            # Solve
            theta = np.linalg.lstsq(phi, targets)[0]
            assert len(theta) == phi.shape[1]

            # Extract parameters, see (10) in [1]
            self.m_lo, self.m_up = theta[0], theta[2]
            self.c_lo, self.c_up = theta[1] / theta[0], theta[3] / theta[2]

from dataclasses import asdict, astuple, dataclass
from typing import Any, Callable, Dict, List, Optional, Self, Tuple, Union

import numpy as np


@dataclass
class SegwaySimData:
    """The core data unit in the module.

    Contains the information useful for control: state, position and references.

    Implementation detail: Using nested dataclasses instead of properties would look neater but it also makes working with the objects more complex because sets of variables of interest may overlap (e.g. state vs reduced state or when rendering position, psi is also necessary).
    """

    time: float  # [s]

    # state
    dot_x: float  # [m/s]
    dot_phi: float  # [rad/s]
    dot_psi: float  # [rad/s]
    x: float  # [m]
    phi: float  # [rad]
    psi: float  # [rad]

    # acceleration (estimate)
    ddot_x: float  # [m/s^2]
    ddot_phi: float  # [rad/s^2]
    ddot_psi: float  # [rad/s^2]

    # position
    px: float  # [m]
    py: float  # [m]

    # position reference
    x_ref: float | None = None  # [m]
    y_ref: float | None = None  # [m]
    psi_ref: float | None = None  # [m]

    # velocity reference
    dot_x_ref: float | None = None  # [m/s]
    dot_psi_ref: float | None = None  # [rad/s]

    def __array__(self) -> np.ndarray:
        return np.array(astuple(self))

    @property
    def state(self) -> np.ndarray:
        return np.array(
            [self.dot_x, self.dot_phi, self.dot_psi, self.x, self.phi, self.psi]
        )

    @state.setter
    def state(self, value: np.ndarray):
        self.dot_x, self.dot_phi, self.dot_psi, self.x, self.phi, self.psi = value

    @property
    def reduced_state(self) -> np.ndarray:
        return np.array([self.dot_x, self.dot_phi, self.dot_psi, self.phi])

    @reduced_state.setter
    def reduced_state(self, value: np.ndarray):
        self.dot_x, self.dot_phi, self.dot_psi, self.phi = value

    @property
    def acceleration(self) -> np.ndarray | None:
        a = [self.ddot_x, self.ddot_phi, self.ddot_psi]
        if any(x is None for x in a):
            return None
        return np.array(a)

    @acceleration.setter
    def acceleration(self, value: np.ndarray | None):
        if value is None:
            value = [None] * 3
        self.ddot_x, self.ddot_phi, self.ddot_psi = value

    @property
    def position(self) -> np.ndarray:
        return np.array([self.px, self.py, self.psi])

    @position.setter
    def position(self, value: np.ndarray):
        self.px, self.py, self.psi = value

    @property
    def position_reference(self) -> np.ndarray | None:
        a = [self.x_ref, self.y_ref, self.psi_ref]
        if any(x is None for x in a):
            return None
        return np.array(a)

    @position_reference.setter
    def position_reference(self, value: np.ndarray | None):
        if value is None:
            value = [None] * 3
        self.x_ref, self.y_ref, self.psi_ref = value

    @property
    def velocity_reference(self) -> np.ndarray | None:
        a = [self.dot_x_ref, self.dot_psi_ref]
        if any(x is None for x in a):
            return None
        return np.array(a)

    @velocity_reference.setter
    def velocity_reference(self, value: np.ndarray | None):
        if value is None:
            value = [None] * 2
        self.dot_x_ref, self.dot_psi_ref = value

    @property
    def velocity(self):
        return np.array([self.dot_x, self.dot_phi, self.dot_psi])

    @classmethod
    def empty(cls) -> Self:
        """Generates an empty observation, so that property setters can be used to configure (parts of) the data.

        Returns
        -------
        Observation
            An observation with all fields set to None.
        """
        return cls(*([None] * 12))

    @classmethod
    def from_numpy(
        cls,
        state: np.ndarray,
        position: np.ndarray,
        position_reference: np.ndarray | None = None,
        velocity_reference: np.ndarray | None = None,
        time: float = 0,
    ) -> Self:
        """Generate the observation from numpy arrays.
        Useful when e.g. when setting initial conditions

        Parameters
        ----------
        state : np.ndarray
        position : np.ndarray
        position_reference : np.ndarray| None, optional
            by default None
        velocity_reference : np.ndarray| None, optional
            by default None
        time : float, optional
            by default 0

        Returns
        -------
        Observation
            Observations with fields filled by the data supplied.
        """
        # can be used to avoid boilerplate when it's generated in numpy
        data = cls.empty()
        data.state = state
        data.position = position
        data.position_reference = position_reference
        data.velocity_reference = velocity_reference
        data.time = time
        return data

    ## helper methods
    @staticmethod
    def reduced2full_state(reduced_state: np.ndarray) -> np.ndarray:
        """Converts the reduced state to the full state, filling zeros for x and psi.



        Parameters
        ----------
        reduced_state : np.ndarray
            The reduced state (ẋ,φ̇,ψ̇,φ)

        Returns
        -------
        np.ndarray
            The full state (ẋ,φ̇,ψ̇,x,φ,ψ).
        """
        full_state = np.zeros((6,), dtype=float)
        full_state[[0, 1, 2, 4]] = reduced_state
        return full_state

    @staticmethod
    def state_n() -> int:
        """Returns the length of the (full) state vector.

        Returns
        -------
        int
            The length.
        """
        return 6

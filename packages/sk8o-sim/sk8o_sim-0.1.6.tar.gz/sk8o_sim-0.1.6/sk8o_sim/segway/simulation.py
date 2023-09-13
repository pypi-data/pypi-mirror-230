import dataclasses
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import control
import numpy as np
import sympy as sym
from sympy import Matrix

from ..common import randomize_parameter
from ..configs import SegwayInitialConditionsCfg, SegwaySimulationCfg, ViewCfg
from .data import SegwaySimData
from .view import View


def truncated_gaussian(mean: float, std: float, bounds: Tuple[float, float]) -> float:
    """Generates samples from a truncated Gaussian distribution with the specified parameters.

    This is done by sampling from a Gaussian distribution and rejecting any samples that fall outside of the bounds. The method performs no checks on the bounds, so it could run arbitrarily long if the bounds are chosen incorrectly.

    Parameters
    ----------
    mean : float
        The mean of the Gaussian distribution.
    std : float
        The standard deviation of the Gaussian distribution.
    bounds : Tuple[float, float]
        Samples will be within [bounds[0], bounds[1]]

    Returns
    -------
    float
        Sample from the specified truncated Gaussian distribution.
    """
    while True:
        sample = np.random.normal(mean, std)
        if bounds[0] <= sample <= bounds[1]:
            return sample


class SegwaySimulation:
    """This class takes care of the actual simulation of the discretied linearized system.

    It also keeps track of other variables, such as SK8O position, which is not a part of the state.
    """

    def __init__(self, cfg: SegwaySimulationCfg):
        self._dt = cfg.timestep
        self.ic_cfg = cfg.initial_conditions
        self.phi0_std = cfg.phi0_std
        self.quantization = cfg.quantization
        self.view = View(cfg.rendering)
        self._data = None

        def ensure_matrix(std: Union[float, List, np.ndarray]) -> np.ndarray:
            # converts a scalar or a vector to a diagonal matrix
            std = np.array(std)
            if std.ndim == 0:
                return std * np.eye(SegwaySimData.state_n())
            elif std.ndim == 1:
                if len(std) != SegwaySimData.state_n():
                    raise ValueError(
                        f"Unexpected std length: {len(std)} (expected {SegwaySimData.state_n()})"
                    )
                return np.diag(std)
            elif std.ndim == 2:
                expected_shape = (SegwaySimData.state_n(), SegwaySimData.state_n())
                if std.shape != expected_shape:
                    raise ValueError(
                        f"Unexpected std shape: {std.shape} (expected {expected_shape})"
                    )
                return std
            else:
                raise ValueError("Unexpected std format")

        self.process_noise_std = (
            self._dt
            * ensure_matrix(cfg.process_noise_std)
            * (1 if cfg.use_noise else 0)
        )
        self.measurement_noise_std = ensure_matrix(cfg.measurement_noise_std) * (
            1 if cfg.use_noise else 0
        )
        self.model_uncertainty_percent_std = (
            cfg.model_uncertainty_percent_std if cfg.use_noise else 0
        )

    @property
    def velocity_reference(self) -> np.ndarray | None:
        """Returns the current velocity reference.

        Returns
        -------
        np.ndarray
            The reference (dot_x_ref, dot_psi_ref).
        """
        return self._data.velocity_reference

    @velocity_reference.setter
    def velocity_reference(self, reference: Tuple[float, float] | None):
        """Sets the velocity reference that will be included in the data from now on.

        Parameters
        ----------
        reference : Tuple[float, float] | np.ndarray | None.
            The reference (dot_x_ref, dot_psi_ref).
        """
        self._data.velocity_reference = reference

    @property
    def position_reference(self) -> np.ndarray | None:
        """Returns the current position reference.

        Returns
        -------
        np.ndarray
            The reference (x, y, psi).
        """
        return self._data.position_reference

    @position_reference.setter
    def position_reference(self, reference: Tuple[float, float, float] | None):
        """Sets the position reference that will be included in the data from now on.

        Parameters
        ----------
        reference : Tuple[float, float, float] | np.ndarray.
            The reference (x, y, psi).
        """
        self._data.position_reference = reference

    def data(self) -> SegwaySimData:
        """Returns the data without any measurement/quantization errors.

        Returns
        -------
        SegwaySimData
            The unaltered simulation data.
        """
        return dataclasses.replace(self._data)

    def reset(
        self,
        state: np.ndarray | None = None,
        position: Tuple[float, float, float] | None = None,
        position_reference: Tuple[float, float, float] | None = None,
        velocity_reference: Tuple[float, float] | None = None,
    ) -> SegwaySimData:
        """Reset the simulation, randomly generating a new Segway model and its state based on the config.

        Parameters
        ----------
        state : np.ndarray | None, optional
            Set the state (can be either the full 6D state or the reduced 4D state), by default None
        position : Tuple[float, float, float] | None, optional
            The position of the robot (x, y, psi), by default None
        position_reference : | Tuple[float, float, float] | np.ndarray | None, default None.
            The reference (x_ref, y_ref, psi_ref).
        velocity_reference : Tuple[float, float] | np.ndarray | None, default None.
            The reference (dot_x_ref, dot_psi_ref).
        """
        self.phi0 = np.random.normal(0, self.phi0_std)
        self.A_d, self.B_d = generate_system(
            self.model_uncertainty_percent_std, Ts=self._dt
        )

        if state is None:
            state = np.array(
                [
                    truncated_gaussian(*params)
                    for params in zip(
                        self.ic_cfg.state_mean,
                        self.ic_cfg.state_std,
                        self.ic_cfg.state_bounds,
                    )
                ]
            )
        elif state.shape == (4,):
            state = SegwaySimData.reduced2full_state(state)
        if not state.shape == (6,):
            raise ValueError("Unexpected state shape!")
        if position is None:
            position = np.random.uniform(
                low=self.ic_cfg.position_low, high=self.ic_cfg.position_high
            )
        self._data = SegwaySimData.from_numpy(state, position)
        self.velocity_reference = velocity_reference
        self.position_reference = position_reference
        return self.measure()

    def _update_position(self, delta_x: float):
        # position update (non-linear)
        self._data.px += np.cos(self._data.psi) * delta_x
        self._data.py += np.sin(self._data.psi) * delta_x

    def _update_state(self, action: np.ndarray):
        # update the state based on the state transition
        assert action.shape == (2,), "Incorrect action shape"
        last_velocity = self._data.velocity
        self._data.state = (
            self.A_d @ self._data.state
            + self.B_d @ action
            + self.process_noise_std @ np.random.randn(SegwaySimData.state_n())
        )
        self._data.acceleration = (self._data.velocity - last_velocity) / self._dt

    def run(self, action: np.ndarray, timestep: float) -> SegwaySimData:
        """Run a step of the simulation.

        Parameters
        ----------
        action : np.ndarray
            Action on the wheels (u_L, u_R).
        timestep : float, optional
            How long to run the simulation. Should be an integer multiple of the discretization timestep.

        Returns
        -------
        SegwaySimData
            SegwaySimData after the timestep.

        """
        if self._data is None:
            self.reset()
            logging.info(
                "Automatically resetting the environment. Consider doing this manually to have more control over the initial conditions."
            )
        for _ in np.arange(0, timestep, self._dt):
            self._data.time += self._dt
            old_x = self._data.x
            self._update_state(action)
            self._update_position(self._data.x - old_x)

        return self.measure()

    def measure(self) -> SegwaySimData:
        """Makes a copy of the data and adds measurement noise and quantization error if appropriate.

        Returns
        -------
        SegwaySimData
            (Potentially) noisy simulation data.
        """
        measurement = dataclasses.replace(
            self._data,
            phi=self._data.phi + self.phi0,
        )
        measurement.state += self.measurement_noise_std @ np.random.randn(
            SegwaySimData.state_n()
        )
        if self.quantization:
            measurement = self.quantize_measurement(measurement)
        return measurement

    @staticmethod
    def quantize_measurement(data: SegwaySimData) -> SegwaySimData:
        """Quantizes the velocities as they would be on the real robot.

        The wheel angular velocities used to compute dot_x and dot_psi are quantized with a step of 6/91 rad/s.

        Parameters
        ----------
        data : SegwaySimData
            The original data.

        Returns
        -------
        SegwaySimData
            Data with quantized dot_x and dot_psi.
        """
        wheel_r = 0.08
        segway_d = 0.29
        angular_velocity_quantization = 6 / 91
        dot_x_quantization = wheel_r / 2 * angular_velocity_quantization
        dot_psi_quantization = wheel_r / segway_d * angular_velocity_quantization
        dot_x = np.round(data.dot_x / dot_x_quantization) * dot_x_quantization
        dot_psi = np.round(data.dot_psi / dot_psi_quantization) * dot_psi_quantization
        return dataclasses.replace(data, dot_x=dot_x, dot_psi=dot_psi)

    def render(self) -> np.ndarray | None:
        if self._data is None:
            self.reset()
            logging.info(
                "Automatically resetting the environment. Consider doing this manually to have more control over the initial conditions."
            )
        return self.view.render(self._data)


def generate_system(
    model_uncertainty_percent_std: float = 0, Ts: float = 0.001, reduced: bool = False
) -> Tuple[np.ndarray, np.ndarray]:
    """Generates a discrete linearized segway system in the form of state space matrices A and B.

    Parameters
    ----------
    model_uncertainty_percent_std : float, optional
        Dictates the randomness in the model, by default 0
    Ts : float, optional
        ZOH discretization period, by default 0.001
    reduced : bool, optional
        If true the reduced model (without states x and psi) will be created, by default False

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Matrices A,B.
    """
    # define model parameters
    d = randomize_parameter(0.29, model_uncertainty_percent_std)  # wheel base
    l = randomize_parameter(0.2907, model_uncertainty_percent_std)  # COM height
    r = randomize_parameter(0.08, model_uncertainty_percent_std)  # Wheel diameter
    mb = randomize_parameter(4, model_uncertainty_percent_std)  # Body mass
    mw = randomize_parameter(0.3, model_uncertainty_percent_std)  # Wheel mass

    #  Wheel moment of inertia about its turning axis
    J = randomize_parameter(0.000735, model_uncertainty_percent_std)
    #  Wheel moment of inertia
    K = randomize_parameter(0.00039, model_uncertainty_percent_std)
    #  Pendulum moment of inertia about X (roll)
    I1 = randomize_parameter(0.015625, model_uncertainty_percent_std)
    #  Pendulum moment of inertia about Y (pitch)
    I2 = randomize_parameter(0.0118625, model_uncertainty_percent_std)
    #  Pendulum moment of inertia about Z
    I3 = randomize_parameter(0.0118625, model_uncertainty_percent_std)
    calpha = randomize_parameter(0.01, model_uncertainty_percent_std)

    g = 9.81

    # define symbolic variables
    x, th, psi, dx, dth, dpsi, uL, uR = sym.symbols("x th psi dx dth dpsi uL uR")
    q = Matrix([x, th, psi])
    dq = Matrix([dx, dth, dpsi])
    u = Matrix([uL, uR])

    # compute matrix elements
    a11 = mb + 2 * mw + 2 * J / r**2
    a12 = mb * l * sym.cos(th)
    a21 = a12
    a22 = I2 + mb * l**2
    a33 = (
        I3
        + 2 * K
        + (mw + J / r**2) * d**2 / 2
        - (I3 - I1 - mb * l**2) * sym.sin(th) ** 2
    )
    c12 = -mb * l * dth * sym.sin(th)
    c13 = -mb * l * dpsi * sym.sin(th)
    c23 = (I3 - I1 - mb * l**2) * dpsi * sym.sin(th) * sym.cos(th)
    c31 = mb * l * dpsi * sym.sin(th)
    c32 = -(I3 - I1 - mb * l**2) * dpsi * sym.sin(th) * sym.cos(th)
    c33 = -(I3 - I1 - mb * l**2) * dth * sym.sin(th) * sym.cos(th)
    d11 = 2 * calpha / r**2
    d12 = -2 * calpha / r
    d21 = d12
    d22 = 2 * calpha
    d33 = (d**2 / (2 * r**2)) * calpha

    # generate the matrices
    M = Matrix([[a11, a12, 0], [a21, a22, 0], [0, 0, a33]])
    C = Matrix([[0, c12, c13], [0, 0, c23], [c31, c32, c33]])
    D = Matrix([[d11, d12, 0], [d21, d22, 0], [0, 0, d33]])
    B = Matrix([[1 / r, 1 / r], [-1, -1], [-d / (2 * r), d / (2 * r)]])
    G = Matrix([[0, -mb * l * g * sym.sin(th), 0]]).T

    # find the linear equations
    fv = M.LUsolve(-G - (C + D) @ dq - B @ u)
    f = Matrix.vstack(fv, dq)
    Ac = f.jacobian(Matrix.vstack(dq, q))
    Bc = f.jacobian(u)

    # get numerical values at the
    substitution = [(p, 0) for p in [*dq, *q, *u]]
    Ac = np.array(Ac.subs(substitution).tolist())
    Bc = np.array(Bc.subs(substitution).tolist())
    if reduced:
        #  Drop forward poisition 'x' and yaw angle 'psi' from the state vector
        Ac = Ac[[0, 1, 2, 4], :][:, [0, 1, 2, 4]]
        Bc = Bc[[0, 1, 2, 4], :]

    sysfull_continuous = control.ss(Ac, Bc, np.eye(len(Ac)), 0)
    sysfull_discrete = control.sample_system(sysfull_continuous, Ts, "zoh")

    Ad = sysfull_discrete.A
    Bd = sysfull_discrete.B
    return Ad, Bd

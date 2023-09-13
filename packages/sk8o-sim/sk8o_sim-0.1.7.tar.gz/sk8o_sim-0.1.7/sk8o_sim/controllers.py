from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import control
import numpy as np

from .configs import SegwayLQRControllerCfg, SK8OHipControllerCfg
from .full import FullSimulationData
from .segway import SegwaySimData
from .segway.simulation import generate_system


class SK8OController(ABC):
    """The controllers below implement this interface to ensure compatibility."""

    @abstractmethod
    def action(self, data: FullSimulationData) -> np.ndarray:
        """Generates an action, depending on the implementation.

        Parameters
        ----------
        data : FullSimulationData
            Data from FullSimulation. This class is partially compatible with SegwaySimData so both might be supported implicitly in some cases.

        Returns
        -------
        np.ndarray
            The action.
        """
        pass

    def __call__(self, data: FullSimulationData) -> np.ndarray:
        """Convenience method that calls the action method.

        Parameters
        ----------
        data : FullSimulationData
            Data from FullSimulation. This class is partially compatible with SegwaySimData so both might be supported implicitly in some cases.

        Returns
        -------
        np.ndarray
            The action.
        """
        return self.action(data)

    @abstractmethod
    def reset(self):
        """This method should be called whenever the simulation is reset in some way. The individual controllers might implement features such as resetting the integrated error to zero."""
        pass


class SegwayLQRController(SK8OController):
    """The LQR controller, as defined in Adam's diploma thesis."""

    def __init__(self, cfg: SegwayLQRControllerCfg | None = None):
        if cfg is None:
            cfg = SegwayLQRControllerCfg()
        self.control_frequency = cfg.control_frequency
        self.L = np.array([[-1, 0, 0, 0], [0, 0, -1, 0]])
        self.K = self.compute_lqr(
            *generate_system(0, Ts=1 / cfg.control_frequency, reduced=True),
            cfg,
        )
        self.epsilon_k = np.array([0, 0])  # augmented state for integral action

    def action(self, data: SegwaySimData | FullSimulationData) -> np.ndarray:
        """Generate an wheel action based on controller settings.

        Parameters
        ----------
        data : SegwaySimData | FullSimulationData
            Data from either of the simulations - they both support the correct properties necessary for the function.

        Returns
        -------
        np.ndarray
            The torque for each wheel (u_L, u_R).
        """
        state = data.reduced_state
        reference = (
            data.velocity_reference
            if data.velocity_reference is not None
            else np.array([0, 0])
        )
        control = -self.K @ np.concatenate([state, self.epsilon_k])
        self.epsilon_k = self.L @ state + np.eye(2) @ self.epsilon_k + reference
        return control

    def __call__(self, data: SegwaySimData) -> np.ndarray:
        # shorthand for action
        return self.action(data)

    def reset(self):
        """Resets the controller's integral part (to be called when reference is changed.)"""
        self.epsilon_k *= 0

    @staticmethod
    def compute_lqr(
        Ad: np.ndarray,
        Bd: np.ndarray,
        cfg: SegwayLQRControllerCfg,
    ) -> np.ndarray:
        """Generates an LQR controller with integral action given the system matrices and control frequency.

        Parameters
        ----------
        Ad : np.ndarray
            System matrix A.
        Bd : np.ndarray
            System matrix B.
        # TODO: update docs

        Returns
        -------
        np.ndarray
            The K matrix s.t. u:=-Kx.
        """
        #  Compute LQR with integral action on forward velocity and qaw rate reference tracking
        L = np.array([[-1, 0, 0, 0], [0, 0, -1, 0]])
        Aint = np.block([[Ad, np.zeros((4, 2))], [L, np.eye(2)]])

        Bint = np.block([[Bd], [np.zeros((2, 2))]])
        Q = np.diag(cfg.Q)
        R = np.diag(cfg.R)

        # transform these to our states

        if not cfg.segway_state_space:
            # designed for a different state vector: [-dpsi*d/r; -2*dx/r; dth; th; -dpsi_interr*d/r; -2*dx_interr/r]=Tq
            # hence we perform a transformation to get a controller for our state
            d = 0.29  # wheel base
            r = 0.08  # Wheel diameter
            T = np.array(
                [
                    [0, 0, -d / r, 0, 0, 0],
                    [-2 / r, 0, 0, 0, 0, 0],
                    [0, 1, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0, -d / r],
                    [0, 0, 0, 0, -2 / r, 0],
                ]
            )
            Tinv = np.array(
                [
                    [0, -r / 2, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0, 0],
                    [-r / d, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, -r / 2, 0],
                    [0, 0, 0, 0, 0, -r / d],
                ]
            )
            Q = T.T @ Q @ T

        KpendI, _, _ = control.dlqr(Aint, Bint, Q, R)
        return KpendI


class SK8OHipController(SK8OController):
    """A PID controller to control SK8O's hips."""

    def __init__(self, cfg: SK8OHipControllerCfg | None = None):
        if cfg is None:
            cfg = SK8OHipControllerCfg()
        self.max_action = cfg.max_action
        self.control_frequency = cfg.control_frequency
        self.P = cfg.P
        self.D = cfg.D
        self.I = cfg.I
        self.reset()

    def action(self, data: FullSimulationData) -> np.ndarray:
        hip_pos = np.array([data.hip_L_qpos, data.hip_R_qpos])
        hip_angle_ref = data.hip_angle_ref
        if hip_angle_ref is None:
            raise ValueError("Hip controller did not find any hip reference!")
        errors = 16.5 * (hip_pos - hip_angle_ref)
        self.errors_sum += errors
        errors_change = errors - self.last_errors
        self.last_errors = errors
        action = self.P * errors + self.I * self.errors_sum + self.D * errors_change
        return -np.clip(action, -self.max_action, self.max_action)

    def reset(self):
        self.errors_sum = np.array([0, 0], dtype=float)
        self.last_errors = np.array([0, 0], dtype=float)


class SK8OFullController(SK8OController):
    """A convenience class that combines a hip controller and a wheel controller the user can combine them easily.

    Both controllers must implement the `SK8OController` interface.
    """

    def __init__(
        self,
        hip_controller: SK8OController | None = None,
        wheel_controller: SK8OController | None = None,
    ) -> None:
        if hip_controller is None:
            hip_controller = SK8OHipController()
        if wheel_controller is None:
            wheel_controller = SegwayLQRController()
        self.hip_controller = hip_controller
        self.wheel_controller = wheel_controller

    def action(self, data: FullSimulationData) -> np.ndarray:
        """Calls the action method of both controllers.

        Parameters
        ----------
        data : FullSimulationData
            Data from FullSimulation.

        Returns
        -------
        np.ndarray
            Concatenated data from the hip controller and wheel controller in the order the simulation expects it.
        """
        return np.concatenate([self.hip_controller(data), self.wheel_controller(data)])

    def reset(self):
        """Calls the reset method of both the controllers."""
        self.hip_controller.reset()
        self.wheel_controller.reset()

import logging
from typing import Any, Dict, List, Tuple

import numpy as np

from ..configs import FullSimulationCfg
from .data import FullSimulationData
from .robot import SK8OMuJoCo
from .view import View, ViewCfg


class FullSimulation:
    """This class binds together the lower-level SK8OMuJoCo class and the Data generation to make it more user-friendly."""

    def __init__(self, cfg: FullSimulationCfg):
        self.robot = SK8OMuJoCo()
        self.view = View(cfg.rendering)
        self.reference = None
        # apply the settings
        if cfg.hips_locked:
            self.lock_hips()

        self.perturbation_std = np.array(cfg.perturbation_std) * int(cfg.use_noise)
        self.model_uncertainty_percent_std = np.array(
            cfg.model_uncertainty_percent_std
        ) * int(cfg.use_noise)

        # initial conditions
        self.body_orientation = cfg.initial_conditions.body_orientation

    def run(self, action: np.ndarray, timestep: float) -> FullSimulationData:
        """Run a step of the simulation.

        Parameters
        ----------
        action : np.ndarray
            Action (torque) on the wheels and hips as per the XML file (hip_L, hip_R, wheel_L, wheel_R).
        timestep : float, optional
            How long to run the simulation. Should be an integer multiple of the timestep specified in the XML file.

        Returns
        -------
        FullSimulationData
            The data after the specified time.
        """
        self.robot.apply_com_perturbation(self.perturbation_std)
        self.robot.run(action, timestep)
        return self.get_data()

    def lock_hips(self):
        """Locks the hips by liming joint movement tightly at their current position."""
        self.robot.lock_hips()
        self._hips_locked = True
        logging.info(
            f"Hips locked at ({self.robot.data.joint('hip_L').qpos, self.robot.data.joint('hip_R').qpos})"
        )

    def unlock_hips(self):
        """Undoes the effect created by `lock_hips`."""
        self.robot.unlock_hips()
        self._hips_locked = False
        logging.info(f"Hips unlocked!")

    def new_reference(
        self,
        velocity_reference: Tuple[float, float] | None = None,
        hip_angle_reference: float | None = None,
    ):
        """Sets the reference that will be included in the data from now on.

        Parameters
        ----------
        velocity_reference : Tuple[float, float] | np.ndarray | None, default None.
            The velocity_reference (dot_x_ref, dot_psi_ref).
        hip_angle_reference : float, optional
            Distance from the ground (assumes upright orientation), by default None
        """
        self.velocity_reference = velocity_reference
        self.hip_angle_reference = hip_angle_reference
        return self.get_data()

    def get_data(self) -> FullSimulationData:
        """Reformats MuJoCo data to be more "digestable" and adds the chosen reference.

        Returns
        -------
        FullSimulationData
            The formatted data.
        """
        data = FullSimulationData.from_mujoco(self.robot, True, self.reference)
        data.velocity_reference = self.velocity_reference
        data.hip_angle_ref = self.hip_angle_reference
        return data

    def reset(
        self,
        hip_angles: float | Tuple[float, float] | None = None,
        leg_lengths: float | Tuple[float, float] | None = None,
        ground_distance: float = 0,
        velocity_reference: Tuple[float, float] | None = None,
        hip_angle_reference: float | None = None,
    ) -> FullSimulationData:
        """Resets the simulation, applying also model and position randomization as per the configuration.

        If both hip_angles and leg_lengths are set to None, the initial leg position will be sampled uniformly from the allowed range.

        Parameters
        ----------
        hip_angles : float | Tuple[float, float] | None, optional
            The angle(s) of the hips (alpha_1), by default None
        leg_lengths : float | Tuple[float, float] | None, optional
            Length(s) of legs, ignored if `hip_angles` not None, by default None
        ground_distance : float, optional
            Distance from the ground (assumes upright orientation), by default 0
        velocity_reference : Tuple[float, float] | np.ndarray | None, default None.
            The velocity_reference (dot_x_ref, dot_psi_ref).
        hip_angle_reference : float, optional
            Distance from the ground (assumes upright orientation), by default None
        """
        if self.model_uncertainty_percent_std != 0:
            self.robot.randomize_model(self.model_uncertainty_percent_std)
        self.robot.reset_simulation()
        self.robot.set_state()  # restore the original config
        self.new_reference(velocity_reference, hip_angle_reference)
        if hip_angles is not None:
            self.robot.hip_angle_config(hip_angles)
        elif leg_lengths is not None:
            self.robot.leg_length_config(leg_lengths)
        else:
            hip_angles = np.random.uniform(self.robot.hip_angle_range)
            self.robot.hip_angle_config(hip_angles)
        self.robot.set_ground_distance(ground_distance)
        if self.body_orientation:
            self.set_body_orientation()
        self.robot.apply_com_perturbation(self.perturbation_std)
        return self.get_data()

    def render(self) -> np.ndarray | None:
        """Renders the simulation.

        Returns
        -------
        np.ndarray | None
            The image if view mode set to `rgb_array`.
        """
        return self.view.render(self.robot.model, self.robot.data)

    def has_fallen(self) -> bool:
        """Decides if the robot has fallen, which is defined as any geom except for the wheels touching ground.

        Returns
        -------
        bool
            True if the robot has fallen.
        """
        return self.robot.has_fallen()

    def close(self):
        """Closes the view."""
        self.view.close()

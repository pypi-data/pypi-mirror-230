import copy
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Tuple

import mujoco
import numpy as np
from mujoco._structs import MjData, MjModel
from numpy.linalg import norm

from ..common import randomize_parameter


@dataclass
class LinkLengths:
    hip2lower_leg: float  # l_u
    lower_leg2knee_loop: float  # l_lk
    knee_loop2body_loop: float  # l_k
    body_loop2hip: float  # l_uk
    lower_leg_l: float  # l_l
    wheel_r: float
    wheel_w: float  # distance between wheels

    ## access using the indexes used in the thesis to make the formulas more readable ##
    @property
    def u(self):
        return self.hip2lower_leg

    @property
    def lk(self):
        return self.lower_leg2knee_loop

    @property
    def k(self):
        return self.knee_loop2body_loop

    @property
    def uk(self):
        return self.body_loop2hip

    @property
    def l(self):
        return self.lower_leg_l

    @classmethod
    def from_mujoco(cls, model: MjModel, data: MjData) -> Self:
        # ensure the lengths are valid
        mujoco.mj_forward(model, data)

        # load all the positions on the left (doesn't matter which side) and compute the relevant lengths
        # this assumes that the position in 'data' is valid (which at least the initial configuration is)
        hip_pos = data.body(f"upper_leg_L").xpos
        lower_leg_pos = data.body(f"lower_leg_L").xpos
        knee_loop_pos = data.body(f"leg_link_L").xpos
        body_loop_pos = data.site(f"loop_body_L").xpos
        wheel_pos = data.body("wheel_L").xpos

        hip2lower_leg = norm(hip_pos - lower_leg_pos)
        lower_leg2knee_loop = norm(lower_leg_pos - knee_loop_pos)
        knee_loop2body_loop = norm(knee_loop_pos - body_loop_pos)
        body_loop2hip = norm(body_loop_pos - hip_pos)
        lower_leg_l = norm(lower_leg_pos - wheel_pos)

        # finally find wheel parameters
        assert all(
            model.geom("wheel_L_tire").size == model.geom("wheel_R_tire").size
        ), "This env doesn't support each wheel size different!"
        # the max dimension of the tire is the one we want
        wheel_r = max(model.geom("wheel_L_tire").size)
        wheel_w = data.geom(("wheel_R_tire")).xpos - data.geom(("wheel_L_tire")).xpos
        return cls(
            hip2lower_leg,
            lower_leg2knee_loop,
            knee_loop2body_loop,
            body_loop2hip,
            lower_leg_l,
            wheel_r,
            wheel_w,
        )


class SK8OMuJoCo:
    """This class manages the MuJoCo simulation and the user hopefully won't need to interact with it at all."""

    leg_length_range = (120e-3, 330e-3)
    hip_angle_range = (0.31, 1.07)  # slightly larger to allow for soft limits
    alpha0 = np.pi / 4

    def __init__(self, xml_path: str | None = None):
        """

        Parameters
        ----------
        xml_path : str | None, optional
            The path to the XML file that contains the scene and SK8O. If None, the default path will be used, by default None
        """
        if xml_path is None:
            xml_path = str(Path(__file__).resolve().parent / "model/scene.xml")
        # prepare the mujoco model
        self.original_model = mujoco.MjModel.from_xml_path(xml_path)
        self.model = mujoco.MjModel.from_xml_path(xml_path)
        self.data = mujoco.MjData(self.model)
        self.init_qpos = self.data.qpos.ravel().copy()
        self.init_qvel = self.data.qvel.ravel().copy()

        # load distances assuming the initial configuration is valid
        self.link_l = LinkLengths.from_mujoco(self.model, self.data)
        self.wheel_ids = [
            self.model.geom(f"wheel_{s}").id
            for s in ["L_tire", "R_tire", "L_rim", "R_rim"]
        ]
        self.floor_id = self.model.geom("floor").id

    @staticmethod
    def _law_of_cosines_2d(a: float, b: float, c: float) -> float:
        """Computes the standard law of cosines in a triangle.

        Parameters
        ----------
        a : float
            Length of side a.
        b : float
            Length of side b.
        c : float
            Length of side c.

        Returns
        -------
        float
            The angle opposite to side c.
        """
        #
        return np.arccos((a**2 + b**2 - c**2) / (2 * a * b))

    def _hip2joint_angles(
        self, hip_angle: float, skip_check: bool = False
    ) -> Tuple[float, float]:
        """Computes the angles of all the joints given link lengths and the angle at the hip (alpha_1).

        Parameters
        ----------
        lenghts : LinkLengths
            The lengths of the links in the robot.
        hip_angle : float
            The angle at the hip (alpha_1)
        skip_check : bool, optional
            If true, the method won't check whether the angle is achievable (might then return nan), by default False

        Returns
        -------
        Tuple[float, float]
            The angles alpha_2 and alpha_3.

        Raises
        ------
        ValueError
            If not `skip_check` and the hip angle is not possible.
        """
        if not skip_check and not (
            self.hip_angle_range[0] <= hip_angle <= self.hip_angle_range[1]
        ):
            raise ValueError(f"Invalid hip angle ({hip_angle})")
        l = self.link_l  # to make the formulas shorter
        d = np.sqrt(
            l.u**2 + l.uk**2 - 2 * l.u * l.uk * np.cos(hip_angle + self.alpha0)
        )
        alpha2a = self._law_of_cosines_2d(d, l.u, l.uk)
        alpha2b = self._law_of_cosines_2d(d, l.lk, l.k)
        alpha3 = self._law_of_cosines_2d(l.lk, l.k, d)
        return alpha2a + alpha2b, alpha3

    def height2hip_angle(self, leg_height: float) -> float:
        """Computes the hip angle (alpha_1) the height of the equivalent segway model

        Parameters
        ----------
        leg_height : float
            The height of the equivalent segway model.
        Returns
        -------
        float
            The angle alpha_1.

        """
        if not (self.leg_length_range[0] <= leg_height <= self.leg_length_range[1]):
            raise ValueError(f"Invalid leg length ({leg_height})")
        l = self.link_l
        cos_alpha4 = (leg_height**2 + l.l**2 - l.u**2) / (2 * l.l * leg_height)
        d = np.sqrt(
            (l.l + l.lk) ** 2
            + leg_height**2
            - 2 * leg_height * (l.l + l.lk) * cos_alpha4
        )
        alpha1a = self._law_of_cosines_2d(d, l.uk, l.k) - self.alpha0
        alpha1b = self._law_of_cosines_2d(d, l.u, l.lk)
        return alpha1a + alpha1b

    def hip_angle2height(self, hip_angle: float) -> float:
        """Computes the COM height of the equivalent Segway model the (vertical) distance between the wheel and hip joints based on the hip angle.

        Parameters
        ----------
        hip_angle : float
            The hip angle in radians.

        Returns
        -------
        float
            The equivalent Segway's COM height in meters.
        """
        alpha1 = np.clip(hip_angle, *self.hip_angle_range)
        if (alpha1 - hip_angle) > 0.05:
            # small clipping may happen "normally" since it's a soft constraint -> avoid spam
            logging.warning("Invalid hip angle -> clipping!")
        alpha2, _ = self._hip2joint_angles(alpha1, skip_check=True)
        ang = alpha1 + np.pi
        knee_pos = self.link_l.u * np.array([np.cos(ang), np.sin(ang)])
        ang = np.pi - (alpha2 - alpha1)
        wheel_pos = knee_pos + self.link_l.l * np.array([np.cos(ang), np.sin(ang)])
        return np.linalg.norm(wheel_pos)

    def hip_angle_config(self, hip_angles: float | Tuple[float, float]):
        # sets the joint angles in the simulation according to hip_angles
        hip_angles = np.atleast_1d(hip_angles)
        if len(hip_angles) == 1:
            hip_angles = np.concatenate([hip_angles, hip_angles])
        ret = []
        for side, hip_angle in zip(["L", "R"], hip_angles):
            alpha2, alpha3 = self._hip2joint_angles(hip_angle)
            # sets the joints along the kinematic loop to satisfy the constraint to have the required hip angle
            self.data.joint(f"hip_{side}").qpos = hip_angle
            self.data.joint(f"knee_{side}").qpos = alpha2
            self.data.joint(f"loop_{side}").qpos = alpha3

        mujoco.mj_forward(self.model, self.data)

    def leg_length_config(self, leg_lengths: float | Tuple[float, float]):
        # sets the joints along the kinematic loop to satisfy the constraint to have the required hip angle
        leg_lengths = np.atleast_1d(leg_lengths)
        if len(leg_lengths) == 1:
            leg_lengths = np.concatenate([leg_lengths, leg_lengths])
        self._hip_angle_config(
            [self.height2hip_angle(self.link_l, h) for h in leg_lengths]
        )

    def set_motors(self, torques: Tuple[float, float, float, float] | np.ndarray):
        """Run a step of the simulation.

        Parameters
        ----------
        torues : Tuple[float, float, float, float] | np.ndarray
            Action (torque) on the wheels and hips as per the XML file (hip_L, hip_R, wheel_L, wheel_R).
        """
        self.data.ctrl[:] = np.array(torques)

    def set_state(self, qpos: np.ndarray | None = None, qvel: np.ndarray | None = None):
        """Sets the mujoco.mjData to the specified qpos and qvel.

        Parameters
        ----------
        qpos : np.ndarray | None, optional
            Joint positions. If None, the XML values will be used, by default None
        qvel : np.ndarray | None, optional
            Joint velocities. If None, the XML values will be used, by default None
        """
        if qpos is None:
            qpos = self.init_qpos
        if qvel is None:
            qvel = self.init_qvel
        assert qpos.shape == (self.model.nq,) and qvel.shape == (self.model.nv,)
        self.data.qpos[:] = np.copy(qpos)
        self.data.qvel[:] = np.copy(qvel)
        if self.model.na == 0:
            self.data.act[:] = None
        mujoco.mj_forward(self.model, self.data)

    def set_ground_distance(self, distance: float = 0):
        """Positions the robot so that the lower wheel is at a certain distance from the floor (this assumes an upright position).

        Parameters
        ----------
        distance : float, optional
            The distance from the floor of the lower wheel., by default 1e-2
        """
        mujoco.mj_forward(self.model, self.data)  # make sure all changes are propagated
        wheel_L_pos = self.data.body("wheel_L").xpos
        wheel_R_pos = self.data.body("wheel_R").xpos
        current_dist = min(wheel_L_pos[-1], wheel_R_pos[-1]) - self.link_l.wheel_r
        if len(self.data.joint("body_joint").qpos) == 7:
            self.data.joint("body_joint").qpos[2] -= current_dist - distance
        else:
            self.data.joint("body_joint").qpos[0] -= current_dist - distance

        mujoco.mj_forward(self.model, self.data)

    def set_body_orientation(self):
        # setup body orientation
        zquat = np.empty(4)
        # rotation around z
        mujoco.mju_axisAngle2Quat(
            zquat, np.array([0, 0, 1]), 2 * np.pi * np.random.rand()
        )
        # small rotation around a random axis
        rquat = np.empty(4)
        mujoco.mju_axisAngle2Quat(rquat, np.random.rand(3), 0.5 * np.random.rand())

        # compose
        quat = np.empty(4)
        mujoco.mju_mulQuat(quat, zquat, rquat)

        # and set
        if len(self.data.joint("body_joint").qpos) == 7:
            self.data.joint("body_joint").qpos[3:] = quat
        else:
            # in case the body is not given full 6 DOF, don't do anything
            logging.warning("Model doesn't seem to have 6 DOFs!")
        mujoco.mj_forward(self.model, self.data)

    def randomize_model(self, percent_std: float | None = None):
        """Randomizes model parameters.

        Parameters
        ----------
        percent_std : float|None, optional
            The % standard deviation of the normal distribution from which the parameters will be sampled, by default None
        """
        if percent_std is None:
            percent_std = self.param_noise_percent_std

        # restore the XML model
        self.model = copy.deepcopy(self.original_model)

        # modify joints
        for joint in (self.model.joint(i) for i in range(self.model.njnt)):
            # only change hinge joints
            if joint.type == mujoco.mjtJoint.mjJNT_HINGE:
                joint.damping = randomize_parameter(joint.damping, percent_std)
                joint.qpos_spring = randomize_parameter(joint.qpos_spring, percent_std)
                joint.stiffness = randomize_parameter(joint.stiffness, percent_std)

        # modify bodies
        for body in (self.model.body(i) for i in range(self.model.nbody)):
            # only change the bodies that are children of the main body (i.e. not floor etc.)
            if body.rootid == self.model.body("body").id:
                # diagonal inertia matrix
                body.inertia = randomize_parameter(body.inertia, percent_std)
                body.mass = randomize_parameter(body.mass, percent_std)

                # COM position is changed as a percentage of geom size
                # find the size of geoms corresponding to the body
                geom_sizes = np.array(
                    [
                        self.model.geom(body.geomadr + i).size
                        for i in range(body.geomnum[0])
                    ]
                )
                # take the maximum along each dimension and take the percent from there
                body.ipos = body.ipos + randomize_parameter(
                    np.zeros(3), percent_std, affine=np.max(geom_sizes, axis=0)
                )
        # propagate the changes to dependent values
        mujoco.mj_setConst(self.model, self.data)

    def apply_com_perturbation(
        self, perturbation_std: float | np.ndarray, overwrite: bool = True
    ):
        """Applies a perturbation based on the config at the COM of the main body.

        ! Note that this
        Parameters
        ----------
        perturbation_std : float | np.ndarray
            Either the std of the whole perturbation vector or a vector of 6 std values for the wrench (3D force and 3D torque).
        overwrite : bool, optional
            If True, any previous wrench will be overwritten, by default True.
        """
        force_torque = np.random.rand(6) * perturbation_std
        # the value of the applied wrench is not reset after simulation step and since perturbations are assumed to be uncorrelated, it's convenient to just overwrite it here
        if overwrite:
            self.data.xfrc_applied[self.model.body("body").id] = force_torque
        else:
            self.data.xfrc_applied[self.model.body("body").id] += force_torque

    def reset_simulation(self):
        mujoco.mj_resetData(self.model, self.data)

    def run(self, action: np.ndarray, timestep: float) -> Self:
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
        self.set_motors(action)
        if timestep < self.model.opt.timestep:
            self.model.opt.timestep = timestep
            logging.info(
                f"Run timestep smaller than simulation timestep -> decreasing it to {timestep} to match."
            )
        mujoco.mj_step(
            self.model, self.data, nstep=int(timestep // self.model.opt.timestep)
        )

    def has_fallen(self) -> bool:
        """Decides if the robot has fallen, which is defined as any geom except for the wheels touching ground.

        Returns
        -------
        bool
            True if the robot has fallen.
        """
        for c in self.data.contact:
            if c.geom1 == self.floor_id and c.geom2 not in self.wheel_ids:
                return True
        return False

    def lock_hips(self):
        """Locks the hips by liming joint movement tightly at their current position."""
        for hip in ["hip_L", "hip_R"]:
            current_pos = self.data.joint(hip).qpos
            self.model.joint(hip).range = current_pos + np.array([-0.001, 0.001])
            self.model.joint(hip).limited = 1

    def unlock_hips(self):
        """Undoes the effect created by `lock_hips`."""
        for hip in ["hip_L", "hip_R"]:
            self.model.joint(hip).limited = 0

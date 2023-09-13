from dataclasses import asdict, astuple, dataclass, fields
from enum import Enum
from typing import Dict, List, Optional, Self, Tuple, Union

import numpy as np
from numpy.linalg import norm

from .robot import SK8OMuJoCo


@dataclass
class FullSimulationData:
    """This class holds all the variables deemed useful for the user.

    This is an abstraction layer over MuJoCo that makes the data easier to access and also computes the Segway states.
    """

    robot: SK8OMuJoCo
    time: float

    ## sensors ##
    IMU_gyro_X: float
    IMU_gyro_Y: float
    IMU_gyro_Z: float

    IMU_acc_X: float
    IMU_acc_Y: float
    IMU_acc_Z: float

    # TODO: should be done using Euler angles (it's a quaternion now)
    body_orientation_A: float
    body_orientation_B: float
    body_orientation_C: float
    body_orientation_D: float

    hip_L_qpos: float
    hip_R_qpos: float
    hip_L_qvel: float
    hip_R_qvel: float

    wheel_L_qpos: float
    wheel_R_qpos: float
    wheel_L_qvel: float
    wheel_R_qvel: float

    ## computed
    dot_x: Optional[float] = None
    dot_phi: Optional[float] = None
    dot_psi: Optional[float] = None
    phi: Optional[float] = None
    roll: Optional[float] = None
    h_L: Optional[float] = None  # height of the left side
    h_R: Optional[float] = None  # height of the right side

    ## references
    dot_x_ref: Optional[float] = None
    dot_psi_ref: Optional[float] = None
    hip_angle_ref: Optional[float] = None

    @property
    def reference(self) -> np.ndarray:
        return np.array([self.dot_x_ref, self.dot_psi_ref, self.hip_angle_ref])

    @reference.setter
    def reference(self, value: np.ndarray | None = None):
        if value is None:
            value = 3 * [None]
        self.dot_x_ref, self.dot_psi_ref, self.hip_angle_ref = value

    @property
    def h_ref(self) -> float:
        # returns the computed height reference based on the hip angle reference
        if self.hip_angle_ref is None:
            return None
        return self.robot.hip_angle2height(self.hip_angle_ref)

    @h_ref.setter
    def h_ref(self, value: float | None) -> float:
        # sets the hip_ref based on the height ref
        if value is None:
            self.hip_angle_ref = None
        self.hip_angle_ref = self.robot.height2hip_angle(value)

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        field_names = (field.name for field in fields(cls))
        return cls(**{k: v for k, v in d.items() if k in field_names})

    @property
    def mean_hip_angle(self) -> np.ndarray:
        return np.mean([self.hip_L_qpos, self.hip_R_qpos])

    def __array__(self) -> np.ndarray:
        return np.array(astuple(self))

    @classmethod
    def from_mujoco(
        cls,
        robot: SK8OMuJoCo,
        fit_segway: bool = True,
        reference: Tuple[float, float, float] | np.ndarray | None = None,
    ) -> Self:
        """Updates the observation held by the object based on MuJoCo data.

        Parameters
        ----------
        data : mujoco.MjData
            SK8O simulation MuJoCo data.
        fit_segway: bool
            If true, the segway state vector will be computed, default True.
        reference : Tuple[float, float, float] | np.ndarray | None, default None.
            The reference (dot_x_ref, dot_psi_ref, hip_angle_ref).
        """
        data = robot.data
        sim_data = cls(
            robot,
            data.time,
            # sensors
            *data.sensor("IMU_gyro").data,
            *data.sensor("IMU_acc").data,
            *data.sensor("body_orientation").data,
            *(data.sensor(f"hip_{s}_pos").data[0] for s in ("L", "R")),
            *(data.sensor(f"hip_{s}_vel").data[0] for s in ("L", "R")),
            *(data.sensor(f"wheel_{s}_pos").data[0] for s in ("L", "R")),
            *(data.sensor(f"wheel_{s}_vel").data[0] for s in ("L", "R")),
        )
        if fit_segway:
            sim_data.compute_segway()
        sim_data.reference = reference
        return sim_data

    def compute_segway(self):
        """Computes the Segway state based on data from mujoco.

        Parameters
        ----------
        robot : SK8OMuJoCo
            The robot containing mujoco data.
        """
        self.dot_x = self._dot_x(self.robot)
        self.dot_phi = self._dot_phi(self.robot)
        self.dot_psi = self._dot_psi(self.robot)
        self.phi = self._phi(self.robot)
        self.roll = self._roll(self.robot)
        self.h_L, self.h_R = [
            self.robot.hip_angle2height(a) for a in (self.hip_L_qpos, self.hip_R_qpos)
        ]

    ## methods to compute the Segway state ##
    @classmethod
    def _fit_segway(cls, robot: SK8OMuJoCo) -> Tuple[np.ndarray, np.ndarray]:
        # finds an equivalent segway model
        wheel_l_pos = cls.body_pos("wheel_L", robot.data)
        wheel_r_pos = cls.body_pos("wheel_R", robot.data)
        axle = wheel_l_pos - wheel_r_pos
        wheel_center = 1 / 2 * (wheel_l_pos + wheel_r_pos)
        segway_rod = cls.body_pos("body", robot.data) - wheel_center
        return axle, segway_rod

    @classmethod
    def _forward_direction(cls, robot: SK8OMuJoCo, in_plane: bool = True) -> np.ndarray:
        # returns a normalized vector in the "forward" direction of the robot
        # the forward direction is perpendicular to both
        # and projected onto the ground - this is more akin to true forward direction
        axle, segway_rod = cls._fit_segway(robot)
        if in_plane:
            P = np.diag([1, 1, 0])
        else:
            P = np.eye(3)

        forward_direction = P @ np.cross(axle, segway_rod)
        return forward_direction / norm(forward_direction)

    @classmethod
    def _dot_x(cls, robot: SK8OMuJoCo) -> float:
        """Returns the forward velocity based on average wheel velocity.

        Parameters
        ----------
        robot : SK8OMuJoCo
            The robot containing mujoco data.

        Returns
        -------
        float
            Forward velocity dot_x.
        """
        #
        # we do not use joint qvel to avoid having to deal with taking knee bending into account

        # we are only concerned with velocities in the plane
        P = np.diag([1, 1, 0])
        left_speed = P @ robot.data.sensor("wheel_L_linvel").data
        right_speed = P @ robot.data.sensor("wheel_R_linvel").data
        return (
            0.5
            * norm(left_speed + right_speed)
            * np.sign(np.dot(left_speed + right_speed, cls._forward_direction(robot)))
        )

    @classmethod
    def _dot_phi(cls, robot: SK8OMuJoCo) -> float:
        """Returns the pitch angle derivative based on an artifical sensor placed at the origin of the main body.

        Parameters
        ----------
        robot : SK8OMuJoCo
            The robot containing mujoco data.

        Returns
        -------
        float
            The pitch angle derivative dot_phi.
        """
        return robot.data.sensor("body_frame_gyro").data[0]

    @classmethod
    def _dot_psi(cls, robot: SK8OMuJoCo) -> float:
        """Returns the angular velocity based on wheel velocity difference.

        Parameters
        ----------
        robot : SK8OMuJoCo
            The robot containing mujoco data.

        Returns
        -------
        float
            Angular velocity dot_psi.
        """
        # we are only concerned with velocities in the plane
        P = np.diag([1, 1, 0])
        left_speed = P @ robot.data.sensor("wheel_L_linvel").data
        right_speed = P @ robot.data.sensor("wheel_R_linvel").data
        diff = right_speed - left_speed
        wheel_l_pos = robot.data.geom("wheel_L_rim").xpos
        wheel_r_pos = robot.data.geom("wheel_R_rim").xpos
        semiaxle = P @ (wheel_l_pos - wheel_r_pos) / 2

        omega = np.cross(diff, semiaxle) / np.dot(semiaxle, semiaxle) / 2
        zaxis = np.array([0, 0, 1])
        sign = np.sign(np.dot(zaxis, omega))
        return sign * norm(omega)

    @classmethod
    def _phi(cls, robot: SK8OMuJoCo) -> float:
        """Returns the pitch angle.

        Parameters
        ----------
        robot : SK8OMuJoCo
            The robot containing mujoco data.

        Returns
        -------
        float
            The pitch angle phi.
        """
        forward = cls._forward_direction(robot, in_plane=False)
        z_axis = [0, 0, 1]
        offset = (
            -0.1
        )  # approximate angle -phi for which the robot is stable (empirical)
        return (np.arccos(np.dot(forward, z_axis)) - np.pi / 2) + offset

    @classmethod
    def _roll(cls, robot: SK8OMuJoCo) -> float:
        """Returns the roll angle.

        Parameters
        ----------
        robot : SK8OMuJoCo
            The robot containing mujoco data.

        Returns
        -------
        float
            The roll angle.
        """
        forward = cls._forward_direction(robot, in_plane=True)
        _, segway_rod = cls._fit_segway(robot)
        # remove the forward component
        segway_rod -= np.dot(forward, segway_rod) * forward
        z_axis = [0, 0, 1]
        r = np.arccos(np.dot(segway_rod / norm(segway_rod), z_axis))
        return r

    @staticmethod
    def body_pos(body_name: str, data) -> np.ndarray:
        # helper function that returns the position of a body from the data
        return np.copy(data.body(body_name).xpos)

    ## next define a few useful (sub)sets of data and functions to extract them ##
    @property
    def segway_names(self) -> List[str]:
        return ["dot_x", "dot_phi", "dot_psi", "phi", "dot_x_ref", "dot_psi_ref"]

    @property
    def segwayplus_names(self) -> List[str]:
        return [
            "dot_x",
            "dot_phi",
            "dot_psi",
            "phi",
            "hip_L_qpos",
            "hip_R_qpos",
            "hip_L_qvel",
            "hip_R_qvel",
            "dot_x_ref",
            "dot_psi_ref",
            "hip_angle_ref",
        ]

    @property
    def sensors_names(self) -> List[str]:
        return [
            "IMU_gyro_X",
            "IMU_gyro_Y",
            "IMU_gyro_Z",
            "IMU_acc_X",
            "IMU_acc_Y",
            "IMU_acc_Z",
            "body_orientation_A",
            "body_orientation_B",
            "body_orientation_C",
            "body_orientation_D",
            "hip_L_qpos",
            "hip_R_qpos",
            "hip_L_qvel",
            "hip_R_qvel",
            "wheel_L_qpos",
            "wheel_R_qpos",
            "wheel_L_qvel",
            "wheel_R_qvel",
            "dot_x_ref",
            "dot_psi_ref",
            "h_ref",
        ]

    @property
    def all_names(self) -> List[str]:
        return [
            "dot_x",
            "dot_phi",
            "dot_psi",
            "phi",
            "IMU_gyro_X",
            "IMU_gyro_Y",
            "IMU_gyro_Z",
            "IMU_acc_X",
            "IMU_acc_Y",
            "IMU_acc_Z",
            "body_orientation_A",
            "body_orientation_B",
            "body_orientation_C",
            "body_orientation_D",
            "hip_L_qpos",
            "hip_R_qpos",
            "hip_L_qvel",
            "hip_R_qvel",
            "wheel_L_qpos",
            "wheel_R_qpos",
            "wheel_L_qvel",
            "wheel_R_qvel",
            "dot_x_ref",
            "dot_psi_ref",
            "h_ref",
        ]

    def _keys_to_fields(self, keys: List[str]) -> np.ndarray:
        return np.array([getattr(self, k) for k in keys])

    @property
    def segway_obs(self) -> np.ndarray:
        return self._keys_to_fields(self.segway_names)

    @property
    def segwayplus_obs(self) -> np.ndarray:
        return self._keys_to_fields(self.segwayplus_names)

    @property
    def sensors_obs(self) -> np.ndarray:
        return self._keys_to_fields(self.sensors_names)

    @property
    def full_obs(self) -> np.ndarray:
        return self._keys_to_fields(self.all_names)

    @property
    def reduced_state(self):
        return np.array([self.dot_x, self.dot_phi, self.dot_psi, self.phi])

    @property
    def velocity_reference(self) -> np.ndarray | None:
        a = [self.dot_x_ref, self.dot_psi_ref]
        if any(x is None for x in a):
            return None
        return np.array(a)

    @velocity_reference.setter
    def velocity_reference(self, value: Tuple[float, float] | None):
        if value is None:
            value = 2 * [None]
        self.dot_x_ref, self.dot_psi_ref = value

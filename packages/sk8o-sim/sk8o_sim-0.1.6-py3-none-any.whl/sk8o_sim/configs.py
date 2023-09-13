import logging
from dataclasses import dataclass, field
from typing import Any, List, Tuple

import numpy as np
from omegaconf import DictConfig


@dataclass
class ViewCfg:
    window_width: int = 1600
    window_height: int = 800
    mode: str = "human"  # human -> creates window, rgb_array -> outputs an array of pixels (useful for saving)


## SK8O Segway ##
@dataclass
class SegwayInitialConditionsCfg:
    ## state (ẋ,φ̇,ψ̇,x,φ,ψ) will be sampled from a truncated normal distribution with the following parameters ##
    state_mean: Tuple[float, float, float, float, float, float] = (0, 0, 0, 0, 0, 0)
    state_std: Tuple[float, float, float, float, float, float] =  (0.5, 0.25, 0.5, 0, 0.25, 0)  # fmt: skip
    # None -> no truncation, float x -> truncation to [-x,x] or tuple (x,y) -> truncation to [x,y]
    # the true type for this is actually 'List[float] | Tuple[float, float] | None]' (and then parsed to Tuple[float, float] in __post_init__ but omegaconf doesn't support that)
    state_bounds: Tuple[Any] = (None, 0.5, None, None, 0.5, None)

    ## position [x,y,ψ] will be sampled from a uniform distribution ##
    position_low: Tuple[float, float, float] = (-3, -3, -3)
    position_high: Tuple[float, float, float] = (3, 3, 3)

    def __post_init__(self):
        def refactor_bounds(bounds):
            if bounds is None:
                return [-np.inf, np.inf]
            elif isinstance(bounds, float):
                return [-bounds, bounds]
            else:
                return tuple(bounds[0], bounds[1])

        self.state_bounds: Tuple[float, float] = [
            refactor_bounds(b) for b in self.state_bounds
        ]


@dataclass
class SegwaySimulationCfg:
    timestep: float = 1e-3
    initial_conditions: SegwayInitialConditionsCfg = field(
        default_factory=SegwayInitialConditionsCfg
    )
    rendering: ViewCfg = field(default_factory=ViewCfg)

    use_noise: bool = False  # if False, all values below are overriden by zero
    measurement_noise_std: Tuple[float, float, float, float, float, float] = (0.01, 0.05, 0.01, 0.01, 0.01, 0.01)  # fmt: skip
    process_noise_std: Tuple[float, float, float, float, float, float] = (0.01, 0.05, 0.01, 0.01, 0.01, 0.01)  # fmt: skip

    model_uncertainty_percent_std: float = 10
    phi0_std: float = 0
    quantization: bool = False

    def __post_init__(self):
        if isinstance(self.initial_conditions, DictConfig):
            self.initial_conditions = SegwayInitialConditionsCfg(
                **self.initial_conditions
            )
        if isinstance(self.rendering, DictConfig):
            self.rendering = ViewCfg(**self.rendering)


## SK8O full ##
@dataclass
class FullInitialConditionsCfg:
    # SK8O will be placed at this height from the ground (see SK8OMuJoCo.set_ground_distance)
    ground_distance: float = 0
    # if True, a random quaternion (that should be recoverable) will be applied to the initial position of the robot (see SK8OMuJoCo.set_body_orientation)
    body_orientation: bool = False

    # random references will be uniformly sampled from these ranges
    forward_velocity_range: Tuple[float, float] = (-2, 2)
    angular_velocity_range: Tuple[float, float] = (-3, 3)
    height_reference_range: Tuple[float, float] = (120e-3, 330e-3)


@dataclass
class FullSimulationCfg:
    initial_conditions: FullInitialConditionsCfg = field(
        default_factory=FullInitialConditionsCfg
    )
    rendering: ViewCfg = field(default_factory=ViewCfg)
    hips_locked: bool = False  # if True, the hips will be locked in the position defined in the XML file and will not need to be controlled
    use_noise: bool = False  # if False, all values below are overriden to zero
    model_uncertainty_percent_std: float = 10  # randomization of physical parameters
    perturbation_std: float | List[float] = 0.1  # essentially process noise
    # there is currently no way to specify measurement noise but that should be easy to add on the user side, here or even in the XML (true sensor noise can be set there)


## controllers ##
@dataclass
class SegwayLQRControllerCfg:
    control_frequency: float = 50
    # TODO: docs
    # the segway state (ẋ,φ̇,ψ̇,φ) is augmented by the cumsum of ẋ and ψ̇ reference errors.
    Q: List[
        float
    ] | None = None  # the diagonal entries of the Q matrix of the LQR criterion
    R: List[
        float
    ] | None = None  # the diagonal entries of the R matrix of the LQR criterion
    # if false, the Q matrix will be transformed to match the segway state
    segway_state_space: bool = True

    def __post_init__(self):
        # select reasonable tested values based on a experiments if nothing is selected by the user

        Q1000 = [15, 5, 1, 1, 1e-4, 1e-4]
        R1000 = [1000, 1000]

        Q200 = [2.5, 2, 0.1, 0.1, 1e-3, 1e-3]
        R200 = [500, 500]

        Q50 = [1, 1, 1e-2, 1e-2, 1, 1]
        R50 = [100, 100]
        if self.control_frequency == 50:
            Q = Q50
            R = R50
        elif self.control_frequency == 200:
            Q = Q200
            R = R200
        elif self.control_frequency == 1000:
            Q = Q1000
            R = R1000
        else:
            logging.warning(
                f"Control_frequency is {self.control_frequency} but no QR values found --> Using the controller for 1000 Hz."
            )
            Q = Q1000
            R = R1000
        if self.Q is None:
            self.Q = Q
            self.segway_state_space = False
        if self.R is None:
            self.R = R


@dataclass
class SK8OHipControllerCfg:
    # clipping the action helps with unwanted jumping and the opposite problem
    max_action: float = 0.3
    control_frequency: float = 50
    # all PID values must be set or they will be overwritten!
    P: float | None = None
    I: float | None = None
    D: float | None = None

    def __post_init__(self):
        if self.P is None or self.I is None or self.D is None:
            if self.control_frequency == 50:
                self.P = 0.3
                self.I = 0.0
                self.D = 0.01
            elif self.control_frequency == 200:
                self.P = 1
                self.I = 0.0
                self.D = 0.04
            elif self.control_frequency == 1000:
                self.P = 2
                self.I = 0.0
                self.D = 0.08
            else:
                raise NotImplementedError(
                    "HipController only supports 50, 200 or 1000 Hz with unset PID values!"
                )

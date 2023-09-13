from os import environ

# pls pygame do not spam
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from .configs import (
    FullInitialConditionsCfg,
    FullSimulationCfg,
    SegwayInitialConditionsCfg,
    SegwayLQRControllerCfg,
    SegwaySimulationCfg,
    SK8OHipControllerCfg,
    ViewCfg,
)
from .controllers import SegwayLQRController, SK8OFullController, SK8OHipController
from .full import FullSimulation, FullSimulationData
from .segway import SegwaySimData, SegwaySimulation

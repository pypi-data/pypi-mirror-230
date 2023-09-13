import time
from dataclasses import dataclass, field

from omegaconf import OmegaConf
from sk8o_sim import (
    SegwayLQRController,
    SegwayLQRControllerCfg,
    SegwaySimulation,
    SegwaySimulationCfg,
)

"""
This file showcases how you can leverage the configurability of the simulations. This showcases how you could change the configuration of a project where you work with the Segway environment and an LQR controller.

Suppose the default discretization timestep was not enough and you always want to run it at 1e-4 instead. You can do that by directly putting that in you config (see the DemoConfig class), which is loaded my OmegaConf to create the base configuration file.

Then running this as e.g. python ./config_demo.py sim_cfg.view_cfg.window_width=800 will override the window size of the rendering, even though you never mention that anywhere. This also validates all your parameters! Pretty cool, huh?
"""


@dataclass
class DemoConfig:
    sim_cfg: SegwaySimulationCfg = field(
        default_factory=lambda: SegwaySimulationCfg(timestep=1e-4)
    )
    controller_cfg: SegwayLQRControllerCfg = field(
        default_factory=SegwayLQRControllerCfg
    )


if __name__ == "__main__":
    # load our modified default config
    base_config: DemoConfig = OmegaConf.create(DemoConfig)

    # overwrite based on cli arguments
    merged_config = OmegaConf.merge(base_config, OmegaConf.from_cli())
    print(merged_config)

    # build the objects to play with using the modified config
    sim = SegwaySimulation(merged_config.sim_cfg)
    lqr = SegwayLQRController(merged_config.controller_cfg)

    # render and let the user check that the resolution has indeed been changed
    sim.render()
    time.sleep(5)

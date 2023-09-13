This folder contains code that to simulates SK8O in Python in two ways:
* as a linear approximation of a Segway ~ SK8O with fixed legs in `sk8o_sim/segway`,
* as a non-linear simulation of SK8O using [MuJoCo](https://mujoco.org/) ("full model") in `sk8o_sim/full`.

You can install this package from PyPI by running
```
pip install sk8o_sim
```
For more information, [check my diploma thesis](https://dspace.cvut.cz/handle/10467/109763).

## Making changes
This project targets Python 3.11, though it was originally written for Python 3.9, which may affect some parts of the codebase (particularly the typing annotations). The necessary packages can be installed using the standard `requirements.txt` file e.g. by 
```
pip install -r sk8o_sim/requirements.txt
```

If you make any changes you wish to make available via pip, make changes to `pyproject.toml` as necessary (at least increment version number!) and GitLab's CI should detect this change and do the dirty work for you. :-)

# Simulation
## Segway
Files in `sk8o_sim/segway` contain the linear approximation of a Segway that was used to train RL models and to tune the LQR. It is highly configurable, can generate randomized models, simulate motor quantization and can be rendered via `pygame`. Note that by default, the measurement and process noise can be quite severe (in addition to initial conditions not necessarily too close to the equilibrium), so even the LQR that works just fine on SK8O may sometimes fail to stabilize the robot.

What it does not support is any way to end the simulation due to the robot falling - it is up to you to decide when the approximation is no longer valid!

### Main components
The building block of the Segway simulation is the `SegwaySimData` dataclass found in `sk8o_sim/segway/data.py`. It contains all the simulation data and some helper functions. In `sk8o_sim/segway/simulation.py`, you can find how the simulation is performed and `view.py` is in charge of the rendering. 

### Demo
A very crude simulation of an LQR stabilization with "slow-mo" rendering can be run using the following code:
```python
import time

import numpy as np
from sk8o_sim import (
    SegwayLQRController,
    SegwayLQRControllerCfg,
    SegwaySimulation,
    SegwaySimulationCfg,
)

# initialize everything
sim = SegwaySimulation(SegwaySimulationCfg())
data = sim.reset()
controller = SegwayLQRController(SegwayLQRControllerCfg())

# run the simulation
sim_time = 10  # [s]
for k in range(sim_time * controller.control_frequency):
    action = controller(data)
    data = sim.run(action, 1 / controller.control_frequency)
    sim.render()
    time.sleep(0.5)
```
Note that the FPS will likely be unstable in this example. For a more advanced interaction, check out the `examples/interactive_segway.py` file.

## Full model
The full model is implemented in [MuJoCo](https://mujoco.org/) and can be found in `sk8o_sim/full`. The [mujoco-python-viewer](https://github.com/rohanpsingh/mujoco-python-viewer) package is used for rendering. 

If you've familiarized yourself with the Segway simulation, this one should hopefully feel similar. Again, you will mostly work with what's contained in the `simulation.py` -- this time the class is `FullSimulation` and will generate `FullSimulationData` objects found in `data.py`. This class is essentially a wrapper around MuJoCo that enables rendering and additionally computes the equivalent Segway states for easier control. Note that these may not make much sense whenever the robot is not in a "close-to-upright" position.

One (admittedly experimental) trick of this simulation is the option to "lock" SK8O's hips/legs (see the `(un)lock_hips` methods) for testing. 

You may also wish to use the `has_fallen` method to gauge whether your control system is successful. This method will return `True` whenever anything else but the wheels touch the ground.

## Controllers
The controllers can be found in `sk8o_sim/controllers.py` and include `SegwayLQRController` to control the wheels as per Adam's thesis and a simple PID hip controller, `SK8OHipController`. Both implement the `SK8OController` interface and are combined in the `SK8OFullController` class which controls both. You can use this class if you wish to implement only partial control.  For example, if your controller only takes care of wheel torques, you can implement the interface and pass your controller as the `wheel_controller` to `SK8OFullController`.


# Configuration
The project is ready for [OmegaConf](https://omegaconf.readthedocs.io/en/2.3_branch/usage.html#from-structured-config/)/[hydra](https://hydra.cc/docs/intro/): the `sk8o_sim/configs.py` file contains all the configuration classes that are available for the simulation, rendering and controllers. This allows you to control everything via custom YAML configs and/or command-line arguments with a only little bit of work. This should also make logging the configuration easy. If you experiment with many versions of a new controller, you can leverage this to easily compare the changes you've made using e.g. Weights & Biases or similar software. To see a sample, see the `examples/cli_configuration.py` demo file.
import numpy as np
from sk8o_sim import (
    FullInitialConditionsCfg,
    FullSimulation,
    FullSimulationCfg,
    SegwayLQRController,
    SegwayLQRControllerCfg,
    SK8OHipController,
    SK8OHipControllerCfg,
)
from sk8o_sim.controllers import SK8OFullController

# setup the controller
control_frequency = 200  # [Hz]
hip_controller = SK8OHipController(
    SK8OHipControllerCfg(control_frequency=control_frequency)
)
wheel_controller = SegwayLQRController(
    SegwayLQRControllerCfg(control_frequency=control_frequency)
)
controller = SK8OFullController(
    hip_controller=hip_controller, wheel_controller=wheel_controller
)

# start simulation
sim = FullSimulation(FullSimulationCfg(hips_locked=False))
# move forward (0.5 m/s) and a bit to the left (0.2 rad/s) while the hips are at 0.9 rad angle
dot_x_ref = 0.5
dot_psi_ref = 0.2
hip_ref = 0.9
data = sim.reset(
    hip_angles=0.7,
    velocity_reference=(dot_x_ref, dot_psi_ref),
    hip_angle_reference=hip_ref,
)

for k in range(100000):
    action = controller.action(data)
    # print(action)
    data = sim.run(action, 1 / control_frequency)
    # if k % 1000 == 0:
    # print(k)
    sim.render()
    if sim.has_fallen():
        print("The robot has fallen! :(")
sim.close()

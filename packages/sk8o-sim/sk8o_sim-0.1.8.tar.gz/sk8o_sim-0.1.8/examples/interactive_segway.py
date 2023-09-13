import time

import numpy as np
import pygame
from sk8o_sim import (
    SegwayLQRController,
    SegwayLQRControllerCfg,
    SegwaySimulation,
    SegwaySimulationCfg,
)

# initialize everything
sim = SegwaySimulation()
controller = SegwayLQRController()
data = sim.reset()
sim_time = 10  # [s]

# configure the video
clock = pygame.time.Clock()
fps = 50
slow_motion_factor = 2  # 1/2 speed
rendering_frequency = slow_motion_factor * fps
run_frequency = max(rendering_frequency, controller.control_frequency)

steps_per_frame = run_frequency // rendering_frequency
steps_per_action = run_frequency // controller.control_frequency

# the main loop
for k in range(sim_time * run_frequency):
    # render if necessary
    if k % steps_per_frame == 0:
        sim.render()
        clock.tick(fps)

    # set the LQR reference according to the keys being pressed
    reference = np.array([0.0, 0.0])
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        reference += [0, 5]
    if keys[pygame.K_RIGHT]:
        reference += [0, -5]
    if keys[pygame.K_UP]:
        reference += [1, 0]
    if keys[pygame.K_DOWN]:
        reference -= [1, 0]
    data.velocity_reference = reference

    # sample a new action if necessary
    if k % steps_per_action == 0:
        action = controller(data)
    # run a step of the simulation
    data = sim.run(action, 1 / run_frequency)

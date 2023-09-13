import os
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# from . import __path__ as ROOT_PATH
import numpy as np
import pygame

from ..configs import ViewCfg
from .data import SegwaySimData


class View:
    modes = ["human", "rgb_array"]

    def __init__(self, cfg: ViewCfg):
        # pygame setup
        self.window_width = cfg.window_width
        self.window_height = cfg.window_height
        if cfg.mode not in self.modes:
            raise ValueError("Unknown mode")
        self.mode = cfg.mode
        self.window = None
        self.faux_window = None
        # self.font = os.path.join(ROOT_PATH[0], "OpenSans-Regular.ttf")
        self.font = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "OpenSans-Regular.ttf"
        )
        # colors
        self.sk8to_blue = (48, 138, 178)
        self.background_color = (255, 255, 255)
        self.grey = (79, 79, 79)
        self.grid_color = (100, 100, 100)
        self.black = (0, 0, 0)
        self.target_color = (255, 0, 0)
        np.set_printoptions(formatter={"float": "{: 0.2f}".format})

    def _to_pygame(
        self,
        coords: Tuple[int, int],
        width: Optional[int] = None,
        height: Optional[int] = None,
        flip_y: bool = True,
        center_x: bool = True,
        center_y: bool = False,
    ) -> Tuple[int, int]:
        # converts "human" coordinate system to the one used by pygame ((0,0) in the top left corner)
        if width is None:
            width = self.window_width
        if height is None:
            height = self.window_height
        x, y = coords
        if center_y:
            y += height // 2
        if flip_y:
            y = height - y
        if center_x:
            x += width // 2
        return np.array([x, y])

    def side_view(self, width: int, height: int, data: SegwaySimData):
        """Side view of Sk8o.

        Parameters
        ----------
        width : int
            Window width.
        height : int
            Window height.
        data : SegwaySimData
            SegwaySimData from which to take the data.
        """

        def transform(coords):
            return self._to_pygame(coords, width, height)

        canvas = pygame.Surface((width, height))
        canvas.fill(self.background_color)
        radius = height * 0.05
        length = min(height, width) * 0.4
        start_position = np.array([0, radius])
        end_position = start_position + length * np.array(
            [np.sin(data.phi), np.cos(data.phi)]
        )
        pygame.draw.line(
            canvas,
            self.sk8to_blue,
            transform(start_position),
            transform(end_position),
            width=5,
        )
        pygame.draw.circle(canvas, self.grey, transform(start_position), radius)

        # animate rotation
        # this is not too accurate (rotation should affect this too...) but that shouldn't matter too much - this is just to show movement
        distance = np.linalg.norm([data.px, data.py])
        wheel_radius = 0.07
        angle = -(distance / wheel_radius) % 2 * np.pi
        pygame.draw.line(
            canvas,
            self.sk8to_blue,
            transform(start_position),
            transform(
                start_position + radius * np.array([np.cos(angle), np.sin(angle)])
            ),
        )

        # show information
        canvas = self._draw_text(canvas, f"Side view", bgcolor="white")
        canvas = self._draw_text(
            canvas,
            f"State (ẋ,φ̇,ψ̇,φ): {np.round(data.reduced_state, 2)}",
            position_x="center",
            position_y=40,
            fontsize=14,
            bgcolor="white",
        )
        if data.acceleration is not None:
            canvas = self._draw_text(
                canvas,
                f"Last acceleration (ẍ,ψ̈): {np.round(data.acceleration,2)}",
                position_x="center",
                position_y=60,
                fontsize=14,
                bgcolor="white",
            )

        if data.position_reference is not None:
            text = f"Target position (x, y, ψ): {np.round(data.position_reference,2)}"
        elif data.velocity_reference is not None:
            text = f"Target velocity (ẋ, ψ̇): {np.round(data.velocity_reference,2)}"
        else:
            text = None
        if text is not None:
            canvas = self._draw_text(
                canvas,
                text,
                position_x="center",
                position_y=80,
                fontsize=14,
                bgcolor="white",
            )
        return canvas

    def _draw_text(
        self,
        canvas: pygame.Surface,
        text: str,
        position_x: str = "center",
        position_y: str = "top",
        fontsize: int = 20,
        fontcolor: Union[str, Tuple[int, int, int]] = "black",
        bgcolor: Union[str, Tuple[int, int, int]] = None,
    ) -> pygame.Surface:
        # helper function to draw text
        font = pygame.font.Font(self.font, fontsize)
        text_surface = font.render(text, True, fontcolor, bgcolor)
        if position_x == "center":
            position_x = canvas.get_width() // 2 - text_surface.get_width() // 2
        elif position_x == "right":
            position_x = canvas.get_width() - text_surface.get_width()
        if position_y == "top":
            position_y = 10  # offset just to be sure
        elif position_y == "bottom":
            position_y = canvas.get_height() - text_surface.get_height()
        canvas.blit(text_surface, (position_x, position_y))
        return canvas

    def _draw_grid(self, canvas: pygame.Surface, step: int = 100):
        # draws the grid in the top view
        width = canvas.get_width()
        height = canvas.get_height()
        w = width // 2
        for i, x in enumerate(range(0, w, step)):
            if i == 0:
                pygame.draw.line(canvas, "red", [w, 0], [w, height])
            else:
                pygame.draw.line(canvas, self.grid_color, [w + x, 0], [w + x, height])
                pygame.draw.line(canvas, self.grid_color, [w - x, 0], [w - x, height])
        h = height // 2
        for i, y in enumerate(range(0, h, step)):
            if i == 0:
                pygame.draw.line(canvas, "red", [0, h], [width, h])
            else:
                pygame.draw.line(canvas, self.grid_color, [0, h + y], [width, h + y])
                pygame.draw.line(canvas, self.grid_color, [0, h - y], [width, h - y])
        return canvas

    def top_view(self, width: int, height: int, data: SegwaySimData) -> pygame.Surface:
        """Generates the top view tile in the rendered image.

        Parameters
        ----------
        width : int
            Width of the tile.
        height : int
            Height of the tile.
        data : SegwaySimData
            The SegwaySimData containing the data to be displayed.
        """

        def transform(coords):
            return self._to_pygame(coords, width, height, center_y=True)

        canvas = pygame.Surface((width, height))
        canvas.fill(self.background_color)

        # TODO: constants should be moved to __init__
        margin_ratio = 0.2
        max_zoom = 50
        min_zoom = 10
        # compute the zoom needed based on Sk8o position (with a lower limit)
        needed_zoom_x = (width // 2 * (1 - margin_ratio)) // abs(data.px)
        needed_zoom_y = (height // 2 * (1 - margin_ratio)) // abs(data.py)
        zoom = int(max(min_zoom, np.min([max_zoom, needed_zoom_x, needed_zoom_y])))
        canvas = self._draw_grid(canvas, zoom)

        x = data.px * zoom
        y = data.py * zoom
        radius = 0.5 * zoom
        pygame.draw.circle(canvas, self.sk8to_blue, transform([x, y]), radius)
        pygame.draw.line(
            canvas,
            self.grey,
            transform([x, y]),
            transform([x + radius * np.cos(data.psi), y + radius * np.sin(data.psi)]),
            width=3,
        )
        canvas = self._draw_text(canvas, f"Top view", bgcolor="white")
        canvas = self._draw_text(
            canvas,
            f"Position (x, y, ψ): {np.round(data.position,2)}",
            position_y="bottom",
            fontsize=14,
            bgcolor="white",
        )

        if data.position_reference is not None:
            # draw target
            c_h = 10
            cross_width = 5
            target = transform(zoom * np.array([target.x_ref, target.y_ref]))

            pygame.draw.line(
                canvas,
                self.target_color,
                *[c + target for c in [[-c_h, -c_h], [c_h, c_h]]],
                width=cross_width,
            )
            pygame.draw.line(
                canvas,
                self.target_color,
                *[c + target for c in [[-c_h, c_h], [c_h, -c_h]]],
                width=cross_width,
            )
        return canvas

    def _render_frame(self, data: SegwaySimData, mode: str) -> Optional[np.ndarray]:
        """Renders a single frame of the view.

        Parameters
        ----------
        data : SegwaySimData
            Contains the data to be rendered.
        mode : str
            What mode to use (currently 'human' or 'rgb_array')

        Returns
        -------
        Optional[np.ndarray]
            The view as a numpy array, if rgb_array mode is used (otherwise None).
        """
        # TODO: move the layout setup to __init__ too
        separator_width = 10
        info_height = 50
        view_width = (self.window_width - 3 * separator_width) // 2
        view_height = self.window_height - info_height - separator_width
        canvas = pygame.Surface((self.window_width, self.window_height))
        canvas.blit(
            self.side_view(view_width, view_height, data),
            (separator_width, info_height),
        )
        canvas.blit(
            self.top_view(view_width, view_height, data),
            (2 * separator_width + view_width, info_height),
        )

        self._draw_text(canvas, f"Simulation time: {data.time:.2f}s", fontcolor="white")
        if mode == "human":
            self.window.blit(canvas, canvas.get_rect())
            pygame.display.flip()
            pygame.display.update()
        elif mode == "rgb_array":
            self.faux_window.blit(canvas, canvas.get_rect())
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def render(self, data: SegwaySimData) -> Optional[np.ndarray]:
        """The main method to be used.

        Parameters
        ----------
        data : SegwaySimData
            Contains the data to be rendered.

        Returns
        -------
        Optional[np.ndarray]
            The view as a numpy array if rgb_array mode is used (otherwise None).
        """
        mode = self.mode
        if self.window is None and self.faux_window is None:
            pygame.init()
        if self.window is None and mode == "human":
            pygame.display.init()
            self.window = pygame.display.set_mode(
                (self.window_width, self.window_height)
            )
            pygame.mixer.quit()
        elif self.faux_window is None and mode == "rgb_array":
            self.faux_window = pygame.Surface((self.window_width, self.window_height))

        # check for Ctrl+C/closing window
        if self.window is not None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

        return self._render_frame(data, mode)

    def close(self):
        """Closes the view window, if it is open."""
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()

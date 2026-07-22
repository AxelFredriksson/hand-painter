import config
from models import BrushSettings, GestureState, Point
from dataclasses import dataclass
import pygame


def scale_point(point: Point, width: int, height: int):
    x = int(point.x * width)
    y = int(point.y * height)

    return (x, y)

@dataclass
class Canvas:
    width: int = config.FRAME_WIDTH
    height: int = config.FRAME_HEIGHT

    def __post_init__(self):
        self._previous_point = None
        self._surface = pygame.Surface((self.width, self.height))

    def update(self, gesture_state: GestureState, brush: BrushSettings):
        if gesture_state.is_drawing == False:
            self._previous_point = None
            return

        pixel_coordinates = scale_point(gesture_state.fingertip, self.width, self.height)

        if self._previous_point:
            pygame.draw.line(
                self._surface, brush.color, self._previous_point, pixel_coordinates, brush.thickness
            )
        else:
            pygame.draw.circle(
                self._surface, brush.color, pixel_coordinates, brush.thickness
            )

        self._previous_point = pixel_coordinates
        return

    def render(self):
        return self._surface

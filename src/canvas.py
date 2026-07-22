import config
from models import BrushSettings, GestureState, Point, ToolState
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
        self._cursor_point = None
        self._surface = pygame.Surface((self.width, self.height))
        self._surface.fill((255, 255, 255))

    def update(self, current_tool: ToolState, gesture_state: GestureState, brush: BrushSettings):
        pixel_coordinates = scale_point(gesture_state.fingertip, self.width, self.height)
        self._cursor_point = pixel_coordinates
        
        if current_tool.is_drawing == False:
            self._previous_point = None
            return


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
        display_surface = self._surface.copy()
        if self._cursor_point is not None:
            pygame.draw.circle(display_surface, color=(0,0,0), center=self._cursor_point, radius=2)
        return display_surface

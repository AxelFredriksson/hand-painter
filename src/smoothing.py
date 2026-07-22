import config
from dataclasses import dataclass
from models import Point


@dataclass
class ExponentialSmoother:
    alpha: float = config.SMOOTHING_FACTOR
    
    def __post_init__(self):
        self._previous_point = None
        
    def smooth(self, new_point: Point) -> Point:
        
        if self._previous_point is None:
            self._previous_point = new_point
            return new_point
        
        smoothed_x = self.alpha * new_point.x + (1 - self.alpha) * self._previous_point.x
        smoothed_y = self.alpha * new_point.y + (1 - self.alpha) * self._previous_point.y
        smoothed_z = self.alpha * new_point.z + (1 - self.alpha) * self._previous_point.z
        
        smoothed_point = Point(smoothed_x, smoothed_y, smoothed_z)
        
        self._previous_point = smoothed_point
        return smoothed_point
        
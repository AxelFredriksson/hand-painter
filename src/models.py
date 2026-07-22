from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Point:
    x: float
    y: float
    z: float = 0
    
    
@dataclass
class HandLandmarks:
    points: list[Point]
    handedness: str
    confidence: float
    
    def get_point(self, index):
        return self.points[index]
    
@dataclass
class GestureState:
    is_drawing: bool
    fingertip: Point
    gesture_name: str = "none"
    

@dataclass (frozen=True)
class BrushSettings:
    color: tuple[int, int, int] = (255, 0, 0)
    thickness: int = 5
    brush_type: str = "round"
    
    
    
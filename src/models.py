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
    
    
@dataclass
class GestureState:
    is_drawing: bool
    fingertip: Optional[Point]
    gesture_name: str = "none"
    

@dataclass (frozen=True)
class BrushSettings:
    color: tuple[int, int, int] = (0, 0, 0) 
    thickness: int = 5
    brush_type: str = "round"
    
    
    
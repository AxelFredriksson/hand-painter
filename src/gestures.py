import config
from models import GestureState, ToolState
import math


def interpret(landmarks):
    state = interpret_left_hand(landmarks)
    if state:
       pencil = interpret_right_hand(landmarks)
       return (state, pencil)
   
    index_point = landmarks.get_point(config.LANDMARK_INDEX_TIP)
    return (ToolState(is_drawing=False, tool_name = "none"), GestureState(fingertip=index_point))


def interpret_left_hand(landmarks):
    thumb_point = landmarks.get_point(config.LANDMARK_THUMB_TIP)
    index_point = landmarks.get_point(config.LANDMARK_INDEX_TIP)
    
    distance = math.dist((thumb_point.x, thumb_point.y), (index_point.x, index_point.y))
    print(f"Distance = {distance}")
    
    if distance < config.PINCH_THRESHOLD:
        return ToolState(is_drawing=True, tool_name="brush")
    else:
        return ToolState(is_drawing=False, tool_name="none")
    

def interpret_right_hand(landmarks):
    index_point = landmarks.get_point(config.LANDMARK_INDEX_TIP)
    
    return GestureState(fingertip=index_point)
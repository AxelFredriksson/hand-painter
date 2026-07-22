import config
from models import GestureState
import math


def interpret(landmarks):
    state = interpret_draw(landmarks)
    if state:
       return state
   
    index_point = landmarks.get_point(config.LANDMARK_INDEX_TIP)
    return GestureState(is_drawing=False, fingertip=index_point, gesture_name="none")


def interpret_draw(landmarks):
    thumb_point = landmarks.get_point(config.LANDMARK_THUMB_TIP)
    index_point = landmarks.get_point(config.LANDMARK_INDEX_TIP)
    
    distance = math.dist((thumb_point.x, thumb_point.y), (index_point.x, index_point.y))
    print(f"Distance = {distance}")
    
    if distance < config.PINCH_THRESHOLD:
        return GestureState(is_drawing=True, fingertip=index_point, gesture_name="pinch")
    else:
        return None
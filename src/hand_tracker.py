import cv2
from dataclasses import dataclass
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config
from models import HandLandmarks, Point

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

def _to_hand_landmarks(hand_landmarks, handedness_category):
    points = [Point(x=lm.x, y=lm.y, z=lm.z) for lm in hand_landmarks]
    return HandLandmarks(
        points=points,
        handedness=handedness_category.category_name,
        confidence=handedness_category.score,
    )
    
def find_by_handedness(landmarks_list, handedness):
    for landmarks in landmarks_list:
        if landmarks.handedness.lower() == handedness.lower():
            return landmarks

    return None


@dataclass
class HandTracker:
    model_path: str = config.MODEL_PATH
    max_num_hands: int = config.MAX_NUM_HANDS
    min_detection_confidence: float = config.MIN_DETECTION_CONFIDENCE
    min_tracking_confidence: float = config.MIN_TRACKING_CONFIDENCE
    
    def __post_init__(self):
        
        # configure landmarker
        base_options = BaseOptions(
            model_asset_path=self.model_path, 
            delegate=BaseOptions.Delegate.CPU
        )
        options = HandLandmarkerOptions(
            base_options = base_options,
            running_mode = VisionRunningMode.VIDEO,
            num_hands = self.max_num_hands,
            min_hand_detection_confidence = self.min_detection_confidence,
            min_tracking_confidence = self.min_tracking_confidence
        )
        self._landmarker = HandLandmarker.create_from_options(options)
        self._frame_count = 0
        
    def process(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(mp.ImageFormat.SRGB, data=rgb_frame)
        
        result = self._landmarker.detect_for_video(mp_image, int(self._frame_count))
        
        self._frame_count += 1000 / config.FRAME_RATE

        hand_landmarks_list = []
        for hand_landmarks, handedness in zip(result.hand_landmarks, result.handedness):
            hand_landmarks_list.append(
                _to_hand_landmarks(hand_landmarks, handedness[0])
            )

        return hand_landmarks_list
        

    
# if __name__ == "__main__":
#     frame = cv2.imread("/home/fredr/Projects/hand_painter/data/images/hand_1.jpg")
#     hand_tracker = HandTracker()
#     result = hand_tracker.process(frame)
#     print(result)
#     print(result.get_point(index))
        
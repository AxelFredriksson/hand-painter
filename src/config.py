# Camera resolution
FRAME_WIDTH=1280
FRAME_HEIGHT=720

# MediaPipe
MAX_NUM_HANDS=1
MIN_DETECTION_CONFIDENCE=0.7 # how confident the model needs to be to detect a new hand
MIN_TRACKING_CONFIDENCE=0.5 # same type of confidence-treshold, but for detecting a hand between frames

# Landmark indices
LANDMARK_THUMB_TIP=4
LANDMARK_INDEX_TIP=8

# Gesture
PINCH_THRESHOLD=0.05 # between 0-1

# Smoothing
SMOOTHING_FACTOR=0.5 # 0: max smoothing, 1: no smoothing
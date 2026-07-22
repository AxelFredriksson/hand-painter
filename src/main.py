import gestures
from canvas import Canvas, scale_point
from hand_tracker import HandTracker, find_by_handedness
from smoothing import ExponentialSmoother
from models import Point, GestureState, HandLandmarks, BrushSettings, ToolState
import config
import cv2
import pygame
import dataclasses
import numpy as np


PANEL_WIDTH = config.FRAME_WIDTH // 2


def main():
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    hand_tracker = HandTracker()
    smoother = ExponentialSmoother()
    canvas = Canvas(width=PANEL_WIDTH, height=config.FRAME_HEIGHT)
    brush = BrushSettings()
    screen = pygame.display.set_mode((config.FRAME_WIDTH, config.FRAME_HEIGHT))
    
    running = True
    while running == True:

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.QUIT:
                running = False
        
        ret, frame = video_capture.read()
        if not ret:
            continue
        
        frame = cv2.resize(frame, (PANEL_WIDTH, config.FRAME_HEIGHT))
        frame = cv2.flip(frame, 1)
        landmarks_list = hand_tracker.process(frame)
        
        #print(landmarks_list)
        
        right_landmarks = find_by_handedness(landmarks_list, "left")
        left_landmarks = find_by_handedness(landmarks_list, "right")
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        camera_surface = pygame.surfarray.make_surface(np.ascontiguousarray(rgb_frame.swapaxes(0, 1)))
        
        current_tool = ToolState(is_drawing=False, tool_name="none")

        if left_landmarks is not None:
            current_tool = gestures.interpret_left_hand(left_landmarks)
            if current_tool.tool_name in config.BRUSH_SETTINGS:
                brush = config.BRUSH_SETTINGS[current_tool.tool_name]

        if right_landmarks is not None:
            right_hand = gestures.interpret_right_hand(right_landmarks)
            smoothed_fingertip = smoother.smooth(right_hand.fingertip)
            right_hand = dataclasses.replace(right_hand,  fingertip=smoothed_fingertip)

            canvas.update(current_tool, right_hand, brush)
            index_scaled = scale_point(smoothed_fingertip, PANEL_WIDTH, config.FRAME_HEIGHT)
            pygame.draw.circle(camera_surface, color=(255,0,0), center=index_scaled, radius=4)

        #print(f"is_drawing = {current_tool.is_drawing} | gesture_name = {current_tool.tool_name}")
            
        screen.blit(camera_surface, (0,0))
        screen.blit(canvas.render(), (PANEL_WIDTH, 0))
        pygame.display.flip()
                
    video_capture.release()
    pygame.quit()
            
    
if __name__ == "__main__":
    main()
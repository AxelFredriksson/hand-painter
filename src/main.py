import gestures
from canvas import Canvas, scale_point
from hand_tracker import HandTracker
from smoothing import ExponentialSmoother
from models import Point, GestureState, HandLandmarks, BrushSettings
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
        landmarks = hand_tracker.process(frame)
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        camera_surface = pygame.surfarray.make_surface(np.ascontiguousarray(rgb_frame.swapaxes(0, 1)))
        
        if landmarks is not None:
            gesture_state = gestures.interpret(landmarks)
            smoothed_fingertip = smoother.smooth(gesture_state.fingertip)
            gesture_state = dataclasses.replace(gesture_state,  fingertip=smoothed_fingertip)
            
            canvas.update(gesture_state, brush)
            index_scaled = scale_point(smoothed_fingertip, PANEL_WIDTH, config.FRAME_HEIGHT)
            pygame.draw.circle(camera_surface, color=(255,0,0), center=index_scaled, radius=4)
            
        screen.blit(camera_surface, (0,0))
        screen.blit(canvas.render(), (PANEL_WIDTH, 0))
        pygame.display.flip()
                
    video_capture.release()
    pygame.quit()
            
    
if __name__ == "__main__":
    main()
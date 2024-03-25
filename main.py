import ast
import ctypes
import sys

import cv2
import pygame

from PTZ.camera import Camera
from PTZ.ptz_controller import CameraController
from video_tracker import VideoTracker
from pygame_interface import PygameInterface
from zone import Zone


def get_camera_id():
    """get camera rtsp URL from camera_id.txt, 0 is the webcam"""
    with open("camera_id.txt", "r") as file:
        camera_id = file.readline()
        # if the camera is local, it's an int value, otherwise it's a string
        if len(camera_id) <= 1: camera_id = int(camera_id)

    # PTZ CAM
    if camera_id == "rtsp://192.168.1.123/12":
        mycam = Camera("192.168.1.123", "admin", "Casa1234")
        controller = CameraController(mycam)
        return camera_id, controller
    return camera_id, None


zone_drawing = False
point = []


def pygame_event_actions(interface, tracker, controller=None):
    """manage possible inputs and commands"""
    global zone_drawing, points
    for event in pygame.event.get():
        # Quits if is pressed q
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
            # if the controller was initialized, manages the movement of the camera
            elif event.key == pygame.K_w and controller != None:
                controller.move_up()
            elif event.key == pygame.K_d and controller != None:
                controller.move_right()
            elif event.key == pygame.K_s and controller != None:
                controller.move_down()
            elif event.key == pygame.K_a and controller != None:
                controller.move_left()
            elif event.key == pygame.K_UP and controller != None:
                controller.zoom_in()
            elif event.key == pygame.K_DOWN and controller != None:
                controller.zoom_out()
        if event.type == pygame.KEYUP and controller != None:
            controller.stop()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Starts zone drawing or stops it if at least 3 points are pressed
            if interface.buttons[interface.new_zone_button].rect.collidepoint(event.pos):
                if not zone_drawing:
                    print("\nStarted Zone Draw")
                    interface.update_text(interface.new_zone_button)
                    zone_drawing = True
                    points = []
                elif len(points) >= 3:
                    print("New Zone Drawn\n")
                    Zone.create_zone(points, interface)
                    zone_drawing = False
                    interface.update_text(interface.new_zone_button)

            # Start video tracking
            elif interface.buttons[interface.start_tracking_button].rect.collidepoint(event.pos):
                if not tracker.is_started():
                    print("Started video tracking\n")
                    tracker.start()
                    interface.update_text(interface.start_tracking_button)
                else:
                    print("Stopped video tracking")
                    tracker.stop()
                    interface.update_text(interface.start_tracking_button)

            elif interface.buttons[interface.load_zones_button].rect.collidepoint(event.pos):
                with open("zones.txt", "r") as file:
                    for line in file:
                        # Reads lines from file, evaluate them as lists and removes repetitions
                        l = ast.literal_eval(line)
                        Zone.create_zone(l, interface)
                        interface.update_text(interface.load_zones_button)

            # Saves the current zones on the interface in zones.txt
            elif interface.buttons[interface.save_zones_button].rect.collidepoint(event.pos):
                Zone.save_zones()
                interface.update_text(interface.save_zones_button)

            # Deletes the current zones from the interface
            elif interface.buttons[interface.delete_zones_button].rect.collidepoint(event.pos):
                Zone.delete_zones(interface)
                interface.update_text(interface.delete_zones_button)


            # Adds point to the zone to draw if the zone drawing is started
            # and it's neither on the dead zone or the zone recap
            elif (zone_drawing
                  and not interface.dead_zone.collidepoint(event.pos)
                  and not interface.zones_recap.collidepoint(event.pos)):
                print(f"{event.pos} added to the Zone")
                points.append(event.pos)
                interface.add_point(event.pos)


if __name__ == '__main__':
    # Started tracker
    tracker = VideoTracker()

    # Get screen resolution
    #user32 = ctypes.windll.user32
    #screen_width = user32.GetSystemMetrics(0)
    #screen_height = user32.GetSystemMetrics(1)

    # Opencv video capture
    camera_id, controller = get_camera_id()
    cap = cv2.VideoCapture(camera_id)
    screen_width, screen_height = cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # Created Pygame Interface
    interface = PygameInterface("Video Tracking System", screen_width, screen_height)

    while True:
        # Read video frame from capture
        ret, frame = cap.read()
        #frame = cv2.resize(frame, (screen_width, screen_height))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Adjust frame to pygame screen
        interface.adjust_frame(frame_rgb)
        pygame_event_actions(interface, tracker, controller)

        # If there aren't people detected, after many frames
        # sends an empty list to the zone control
        if tracker.is_started():
            results = tracker.object_detection(frame, interface)
            Zone.update_zone(results)

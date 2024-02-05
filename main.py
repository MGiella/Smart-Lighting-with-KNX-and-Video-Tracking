import ast
import sys

import cv2
import pygame

from video_tracker import VideoTracker
from pygame_interface import PygameInterface
from zone import Zone


def get_camera_id():
    """get camera id from camera_id.txt"""
    with open("camera_id.txt", "r") as file:
        camera_id = file.readline()
        # if the camera is local, it's an int value, otherwise it's a string
        if len(camera_id) <= 1: camera_id = int(camera_id)
    return camera_id


zone_drawing = False
point = []

def pygame_event_actions(interface,tracker):
    """manage possible inputs and commands"""
    global zone_drawing, points
    for event in pygame.event.get():
        # Quits if is pressed q
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                tracker.stop()
                sys.exit()
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


if __name__ == '__main__':
    # Started tracker
    tracker = VideoTracker()

    # Opencv video capture
    cap = cv2.VideoCapture(get_camera_id())
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    width = 1080
    height = 720

    # Set pygame display
    interface = PygameInterface("Video Tracking System", width, height)
    cont_no_one = 0
    while True:
        # Read video frame from capture
        ret, frame = cap.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Adjust frame to pygame screen
        interface.adjust_frame(frame_rgb)
        pygame_event_actions(interface, tracker)

        # If there aren't people detected, after many frames
        # sends an empty list to the zone control
        if tracker.is_started():
            results = tracker.object_detection(frame, interface)
            if results is not None:
                Zone.update_zone(results)
                cont_no_one = 0
            else:
                cont_no_one += 1
                if cont_no_one >= 300:
                    Zone.update_zone([])
                    cont_no_one = 0

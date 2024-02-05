import random

import pygame
import lights_control

"""PygameInterface is a Singleton that manages the interface"""


class PygameInterface:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
            pygame.init()
        return cls.instance

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self._screen = pygame.display.set_mode((width, height))
        self._zones = []
        self._boxes = []
        self._points = []

        # Font size adapts to screen height
        self.font_size = int(22 * self.height / 720)
        self._font = pygame.font.Font(None, self.font_size)

        # Position and dimension of the objects are relative to the resolution
        self.object_height = self.height / 8
        self.object_width = 1080 * self.object_height / 720

        # The margins adapt to the size of the object
        self.margin_left = 20 * self.object_width / 135
        self.margin_top = 20 * self.object_height / 90
        self.margin_bottom = 0
        self.margin_right = self.width - (self.object_width + self.margin_left * 2)

        # The partitions adapt to the size of objects and margins
        self.partition_height = self.height
        self.partition_width = self.object_width + self.margin_left * 2

        self.buttons = self.create_buttons()
        self.dead_zone = self.create_dead_zone()
        self.zones_recap = self.create_zones_recap()

        pygame.display.set_caption(name)

    class Button:
        """a Button is a rectangle with a swappable text"""
        def __init__(self, pos_x, pos_y, width, height, rendered_text_default, rendered_text_changed=None):
            self.width = width
            self.height = height
            self.rect = pygame.Rect(pos_x, pos_y, self.width, self.height)

            self.rendered_text_default = rendered_text_default
            self.rendered_text_changed = rendered_text_changed

        def swap_texts(self):
            """swap the default text with the changed one if possible"""
            if self.rendered_text_changed:
                new_text = self.rendered_text_default
                self.rendered_text_default = self.rendered_text_changed
                self.rendered_text_changed = new_text

    class Zone:
        """Zone object with a polygon that will be drawn and a recap"""

        def __init__(self, name, font, polygon, light, pos_x, pos_y, width, height):
            self.polygon = polygon
            self._light = light
            self._font = font
            self.name = name
            # creates a random color for the text and the zone polygon
            self.color = (random.randint(0, 255), random.randint(0, 199), random.randint(0, 255))
            self.text_render = self._font.render(f"{self.name} {self._light.address} {self._light.state}", True,
                                                 self.color)
            self.recap = PygameInterface.Button(pos_x, pos_y, width, height, self.text_render)

        def update(self):
            """check and change the status of the light each time the zone is drawn"""
            self.text_render = self._font.render(f"{self.name} {self._light.address} {self._light.state}", True,
                                                 self.color)
            self.recap.rendered_text_default = self.text_render

    def adjust_frame(self, frame_rgb):
        """set the frame on pygame display and draws all the elements of the interface"""
        pygame_frame = pygame.surfarray.make_surface(frame_rgb)
        rotated_pygame_frame = pygame.transform.rotate(pygame_frame, -90)
        rotated_pygame_frame = pygame.transform.scale(rotated_pygame_frame, (self.width, self.height))
        # self.screen.blit(rotated_pygame_frame, (0, 0))
        mirrored_image = pygame.transform.flip(rotated_pygame_frame, True, False)
        self._screen.blit(mirrored_image, (0, 0))

        # Updates pygame display, the order represents layering
        self.draw_points()
        self.draw_zones()
        self.draw_boxes()
        self.draw_zone_recap()
        self.draw_dead_zone()
        self.draw_buttons(self.buttons.values())
        pygame.display.flip()

    def create_buttons(self):
        """creates the buttons for the interface"""
        buttons = {}
        button_height = self.object_height
        button_width = self.object_width

        # Creates the buttons with the measure given and the texts that adapt to the clicks

        # Button New Zone
        text_zones_default = self._font.render('New Zone', True, (0, 0, 0))
        text_zones_changed = self._font.render('Set Zone', True, (0, 0, 0))
        button_zone = self.Button(button_width * 0.15, button_height * 0, button_width, button_height,
                                  text_zones_default, text_zones_changed)
        buttons["New Zone"] = button_zone
        self.new_zone_button = "New Zone"

        # Button Start Tracking
        text_tracking_default = self._font.render('Start Tracking', True, (0, 0, 0))
        text_tracking_changed = self._font.render('Stop Tracking', True, (0, 0, 0))
        button_video_track = self.Button(button_width * 0.15, button_height * 1.5, button_width, button_height,
                                         text_tracking_default, text_tracking_changed)
        buttons["Start Tracking"] = button_video_track
        self.start_tracking_button = "Start Tracking"

        # Button Load Zones
        text_load_zones = self._font.render('Load Zones', True, (0, 0, 0))
        button_load_zones = self.Button(button_width * 0.15, button_height * 3, button_width, button_height,
                                        text_load_zones)
        buttons["Load Zones"] = button_load_zones
        self.load_zones_button = "Load Zones"

        # Button Save Zones
        text_save_zones = self._font.render('Save Zones', True, (0, 0, 0))
        button_save_zones = self.Button(button_width * 0.15, button_height * 4.5, button_width, button_height,
                                        text_save_zones)
        buttons["Save Zones"] = button_save_zones
        self.save_zones_button = "Save Zones"

        # Button Delete Zones
        text_flush = self._font.render('Delete Zones', True, (0, 0, 0))
        button_flush = self.Button(button_width * 0.15, button_height * 6, button_width, button_height,
                                   text_flush)
        buttons["Delete Zones"] = button_flush
        self.delete_zones_button = "Delete Zones"

        return buttons

    def draw_buttons(self, buttons_to_draw):
        """draws the buttons on the screen"""
        margin_x = self.margin_left
        margin_y = self.margin_top

        for button in buttons_to_draw:
            pygame.draw.rect(self._screen, (255, 255, 255), button.rect)
            self._screen.blit(button.rendered_text_default,
                              (button.rect.x + margin_x, button.rect.y + margin_y * 1.5))

    def add_zone(self, zone_polygon, zone_light: lights_control.Light):
        """add a zone on the interface and set data for the recap"""
        zone_name = "Zone " + str((len(self._zones) + 1))
        recap_width = self.partition_width
        recap_height = self.object_height / 1.5
        margin = self.margin_top / 2

        pos_x = self.margin_right
        pos_y = len(self._zones) * (recap_height + margin)
        zone = self.Zone(zone_name, self._font, zone_polygon, zone_light, pos_x, pos_y, recap_width, recap_height)
        self._zones.append(zone)
        self._points=[]

    def delete_zones(self):
        """removes all the zones on the interface"""
        self._zones.clear()

    def draw_zones(self):
        """draws the zones on the interface"""
        # Cycles all thr points and connects them with a line
        for zone in self._zones:
            points = list(zone.polygon.exterior.coords)
            self.draw_empty_rectangle(points, zone.color, 4)
            zone.update()

    def update_text(self, button):
        """updates the text of the button clicked"""
        if button in self.buttons:
            changed_button = self.buttons[button]
            changed_button.swap_texts()
        else:
            print("Button name not correct")

    def create_box(self, x, y, w, h):
        """creates the box that track the person"""
        rectangle = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        self._boxes.append(rectangle)

    def draw_boxes(self):
        """draws the boxes on the interface"""
        for box in self._boxes:
            self.draw_empty_rectangle(box, (0, 0, 255), 1)
        self._boxes = []

    def draw_empty_rectangle(self, points, color, width):
        """draws a polygon using the points"""
        current_point = first_point = points[0]
        points.remove(first_point)
        for point in points:
            pygame.draw.line(self._screen, color, current_point, point, width)
            current_point = point
        pygame.draw.line(self._screen, color, current_point, first_point, width)

    def create_dead_zone(self):
        """creates a partition of the interface where isn't possible create a zone"""
        dead_zone = pygame.rect.Rect(0, 0, self.partition_width, self.partition_height)
        return dead_zone

    def draw_dead_zone(self):
        """draws the dead zone on the interface"""
        pygame.draw.rect(self._screen, (200, 200, 200), self.dead_zone)

    def create_zones_recap(self):
        """creates the zone recap on the interface"""
        zones_recap = pygame.rect.Rect(self.margin_right, 0, self.partition_width, self.partition_height)
        return zones_recap

    def draw_zone_recap(self):
        """draws the zone recap on the interface and all the zone objects on the recap"""
        pygame.draw.rect(self._screen, (200, 200, 200), self.zones_recap)
        button_to_draw = []
        for zone in self._zones:
            button_to_draw.append(zone.recap)
        self.draw_buttons(button_to_draw)

    def add_point(self,position):
        self._points.append(position)

    def draw_points(self):
        for point in self._points:
            pygame.draw.circle(self._screen,(255,0,0),point,self.font_size/3)

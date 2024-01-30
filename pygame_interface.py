import pygame
import lights_control


class PygameInterface:
    pygame.init()

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))

        self.font_size = int(22 * self.height / 720)
        self.font = pygame.font.Font(None, self.font_size)
        self.buttons = self.create_buttons()
        self.zones = []
        self.boxes = []
        self.dead_zone = self.create_dead_zone()
        self.zone_recap = self.create_zone_recap()

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
        def __init__(self,name,font,polygon,light,pos_x,pos_y,width,height):
            self.polygon = polygon
            self.light = light
            self.font = font
            self.text_render = self.font.render(f"{name} {self.light.address}", True, (0, 0, 0))
            self.recap = PygameInterface.Button(pos_x,pos_y,width,height,self.text_render)

    def adjust_frame(self, frame_rgb):
        """set the frame on pygame display"""
        pygame_frame = pygame.surfarray.make_surface(frame_rgb)
        rotated_pygame_frame = pygame.transform.rotate(pygame_frame, -90)
        rotated_pygame_frame = pygame.transform.scale(rotated_pygame_frame, (self.width, self.height))
        # self.screen.blit(rotated_pygame_frame, (0, 0))
        mirrored_image = pygame.transform.flip(rotated_pygame_frame, True, False)
        self.screen.blit(mirrored_image, (0, 0))

        # Updates pygame display, the order represents layering
        self.draw_zones()
        self.draw_boxes()
        self.draw_zone_recap()
        self.draw_dead_zone()
        self.draw_buttons(self.buttons.values())
        pygame.display.flip()
        self.boxes = []
    def create_buttons(self):
        """creates the buttons for the interface"""
        buttons = {}

        # Position and dimension of the button are relative to the resolution
        button_height = self.height / 8
        button_width = 1080 * button_height / 720


        # Creates the buttons with the measure given and the texts that adapt to the clicks

        # Button New Zone
        text_zones_default = self.font.render('New Zone', True, (0, 0, 0))
        text_zones_changed =  self.font.render('Set Zone', True, (0, 0, 0))
        button_zone = self.Button(button_width * 0.15, button_height * 0, button_width, button_height,
                                  text_zones_default, text_zones_changed)
        buttons["New Zone"] = button_zone
        self.new_zone_button = "New Zone"

        # Button Start Tracking
        text_tracking_default =  self.font.render('Start Tracking', True, (0, 0, 0))
        text_tracking_changed = self.font.render('Stop Tracking', True, (0, 0, 0))
        button_video_track = self.Button(button_width * 0.15, button_height * 1.5, button_width, button_height,
                                         text_tracking_default, text_tracking_changed)
        buttons["Start Tracking"] = button_video_track
        self.start_tracking_button = "Start Tracking"

        # Button Load Zones
        text_load_zones =  self.font.render('Load Zones', True, (0, 0, 0))
        button_load_zones = self.Button(button_width * 0.15, button_height * 3, button_width, button_height,
                                        text_load_zones)
        buttons["Load Zones"] = button_load_zones
        self.load_zones_button = "Load Zones"

        # Button Save Zones
        text_save_zones =  self.font.render('Save Zones', True, (0, 0, 0))
        button_save_zones = self.Button(button_width * 0.15, button_height * 4.5, button_width, button_height,
                                        text_save_zones)
        buttons["Save Zones"] = button_save_zones
        self.save_zones_button = "Save Zones"

        # Button Delete Zones
        text_flush =  self.font.render('Delete Zones', True, (0, 0, 0))
        button_flush = self.Button(button_width * 0.15, button_height * 6, button_width, button_height,
                                   text_flush)
        buttons["Delete Zones"] = button_flush
        self.delete_zones_button = "Delete Zones"

        return buttons
    def draw_buttons(self,buttons_to_draw):
        """draws the buttons on the screen"""
        # The margins adapt to the size of the buttons

        button_height = self.height / 8
        button_width = 1080 * button_height / 720
        margin_x = 20 * button_width / 135
        margin_y = 20 * button_height / 90

        for button in buttons_to_draw:
            pygame.draw.rect(self.screen, (255, 255, 255), button.rect)
            self.screen.blit(button.rendered_text_default,
                             (button.rect.x + margin_x, button.rect.y + margin_y * 1.5))
    def add_zone(self, zone_polygon,zone_light:lights_control.Light):
        """add a zone on the interface and set data for the recap"""
        zone_name = "Zone " + str((len(self.zones)+1))
        recap_width = self.dead_zone.width
        print(recap_width)
        recap_height = self.height/8
        margin = 20 * recap_height / 90
        pos_x = self.width-self.dead_zone.width
        pos_y = len(self.zones) * (recap_height + margin)
        zone = self.Zone(zone_name,self.font,zone_polygon,zone_light,pos_x,pos_y,recap_width,recap_height)
        self.zones.append(zone)
    def delete_zones(self):
        """removes all the zones on the interface"""
        self.zones.clear()
    def draw_zones(self):
        """draws the zones on the interface"""
        # Cycles all thr points and connects them with a line
        for zone in self.zones:
            points = list(zone.polygon.exterior.coords)
            self.draw_empty_rectangle(points, [255, 150, 0], 4)
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
        self.boxes.append(rectangle)
    def draw_boxes(self):
        """draws the boxes on the interface"""
        for box in self.boxes:
            self.draw_empty_rectangle(box, (0, 0, 255), 1)
    def draw_empty_rectangle(self, points, color, widht):
        """draws a polygon using the points"""
        current_point = first_point = points[0]
        points.remove(first_point)
        for point in points:
            pygame.draw.line(self.screen, color, current_point, point, widht)
            current_point = point
        pygame.draw.line(self.screen, color, current_point, first_point, widht)
    def create_dead_zone(self):
        """creates a partition of the interface where isn't possible create a zone"""
        dead_zone_height = self.height

        # button height is height/8, it has the same width of the button + margin*2(rt,lt)
        button_width = 1080 * (self.height / 8) / 720
        button_margin_x = 20 * button_width / 135
        dead_zone_width = button_width + button_margin_x*2

        dead_zone = pygame.rect.Rect(0, 0, dead_zone_width, dead_zone_height)
        return dead_zone
    def draw_dead_zone(self):
        """draws the dead zone on the interface"""
        pygame.draw.rect(self.screen, (200, 200, 200), self.dead_zone)
    def create_zone_recap(self):
        """creates the zone recap on the interface"""
        zone_recap_height = self.height
        zone_recap_width = self.dead_zone.width
        zone_recap = pygame.rect.Rect(self.width - zone_recap_width, 0, zone_recap_width, zone_recap_height)
        return zone_recap
    def draw_zone_recap(self):
        """draws the zone recap on the interface and all the zone objects on the recap"""
        pygame.draw.rect(self.screen, (200, 200, 200), self.zone_recap)
        button_to_draw = []
        for zone in self.zones:
            button_to_draw.append(zone.recap)
        self.draw_buttons(button_to_draw)


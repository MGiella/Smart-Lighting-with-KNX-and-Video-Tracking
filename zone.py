import math
from shapely import Polygon

import lights_control
from pygame_interface import PygameInterface


class Zone:
    zones = {}
    people_in_zone = {}
    collider_borders = 50

    def __init__(self, points):
        ordered_points = self.order_points_clockwise(points)
        self.zone_polygon = Polygon(ordered_points)
        self.people_count = 0
        self.light = lights_control.Light()


    def __str__(self):
        l = list(self.zone_polygon.exterior.coords)
        l.remove(l[0])
        return str(l)

    def update(self, people):
        if people > 0:
            self.light.light_on()
        else:
            self.light.light_off()

        self.people_count = people
        Zone.zones[self] = self.people_count

    def contains(self, point):
        """return True if the polygon intersects the square created by the center given"""
        x,y = point
        borders = Zone.collider_borders
        collide = Polygon([(x-borders,y-borders),(x-borders,y+borders),(x+borders,y+borders),(x+borders,y-borders)])
        return self.zone_polygon.intersects(collide)



    @classmethod
    def create_zone(cls, points: list, interface: PygameInterface):
        """creates a new Zone instance"""
        ordered_points = cls.order_points_clockwise(points)
        new_zone_polygon = Polygon(ordered_points)
        for zone in Zone.zones:
            if zone.zone_polygon == new_zone_polygon:
                print("Zone Already Created")
                return
        new_zone = Zone(points)
        print("New Zone Created" + str(new_zone))
        cls.zones[new_zone] = new_zone.people_count
        interface.add_zone(new_zone_polygon,new_zone.light)

    @classmethod
    def update_zone(cls, points: list[(float, float)]):
        """check how many people are in each zone and manages changes"""
        cls.people_in_zone.clear()
        for zone in cls.zones.keys():
            cls.people_in_zone[zone] = 0
            if points:
                for point in points:
                    if zone.contains(point):
                        cls.people_in_zone[zone] += 1
                    else:
                        cls.people_in_zone[zone] = 0

        for zone in cls.people_in_zone.keys():
            if cls.people_in_zone[zone] != cls.zones[zone]:
                zone.update(cls.people_in_zone[zone])

    @classmethod
    def save_zones(cls):
        """writes the actual zones in zones.txt"""
        with open("zones.txt", "w") as file:
            for zone in cls.zones.keys():
                file.write(str(zone) + "\n")

    @classmethod
    def delete_zones(cls, interface: PygameInterface):
        """delete all zones objects and clean zones.txt"""
        cls.zones.clear()
        lights_control.Light.clear_lights()
        interface.delete_zones()

    @staticmethod
    def order_points_clockwise(points):
        # Centroid of the points
        sum_x = sum(x for x, y in points)
        sum_y = sum(y for x, y in points)
        num_points = len(points)
        centroid_x = sum_x / num_points
        centroid_y = sum_y / num_points

        # Orders the points clockwise in relation to the centroid
        ordered_points = sorted(points, key=lambda point: math.atan2(point[1] - centroid_y, point[0] - centroid_x))
        return ordered_points

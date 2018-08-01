from traffic_simuator import CityLocation

class Pedestrian(object):

    def __init__(self, name: str, start_location: CityLocation, destination: CityLocation, list_short_paths):

        self.start_location = start_location
        self.list_short_paths = list_short_paths
        self.destination = destination
        self.name = name

    def __str__(self) -> str:
        return "Name: {}, Started: {}, Destination: {})".format(self.name, self.start_location, self.destination)
from traffic_simuator import GeoLocation

class Pedestrian(object):

    def __init__(self, start_location: GeoLocation = None, current_location: GeoLocation = None, destination: GeoLocation = None):

        self.start_location = start_location
        self.current_location = current_location
        self.destination = destination

    def __str__(self) -> str:
        return "Started: {}, Currently: {}, Destination: {})".format(self.start_location, self.current_location, self.destination)
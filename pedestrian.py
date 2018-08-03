import random

import matplotlib.pyplot as plt
import networkx as nx

from city import (CityLocation,
                  City, )


class PedestrianCommute(object):

    def __init__(self, start_location: CityLocation, destination: CityLocation):
        self.start_location = start_location
        self.destination = destination

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.start_location == o.start_location and self.destination == o.destination
        else:
            return False

    def __hash__(self) -> int:
        return 31 * hash(self.start_location.__hash__) * hash(self.destination.__hash__)

    def __str__(self) -> str:
        return "({} - {})".format(self.start_location.__str__, self.destination.__str__)

    def __repr__(self) -> str:
        return self.__str__()


class Pedestrian(object):

    def __init__(self, name: str, city: City, start_location: CityLocation, destination: CityLocation,
                 list_short_paths):
        self.name = name
        self.city = city
        self.pedestrian_commute = PedestrianCommute(start_location, destination)
        self.list_short_paths = list_short_paths

    @classmethod
    def filter_locations(cls, city_graph: nx.Graph, location_checker):
        return [location for location in city_graph.nodes() if location_checker(location)]

    @classmethod
    def generate_random_pedestrians(cls, num_peds, city: City) -> list:

        """
            For pedestrian start origins, we randomly select, without replacement, n number of residences from city
            grid,
            one for each pedestrian
            """

        res_nodes = [i for i in city.city_graph.nodes() if CityLocation.is_residence(i) == True]

        try:
            start_nodes = random.sample(res_nodes, num_peds)
        except ValueError:
            print("Sorry, the city grid size is not sufficiently large for this number of pedestrians.")
            return None

        """
        For destinations, we randomly select, without replacement, n number of businesses from city grid,
        one for each pedestrian
        """

        business_nodes = [j for j in city.city_graph.nodes() if CityLocation.is_business(j) == True]

        end_nodes = random.sample(business_nodes, num_peds)

        combined_nodes = zip(start_nodes, end_nodes)

        """
        To account for generated nodes with blockages, we run the simulation on a copy of the city grid
        where blocked nodes have been removed so that shortest paths for pedestrians will only include
        open pathways
        """

        blocked_nodes = [i for i in city.city_graph.nodes() if CityLocation.is_blocked(i) == True]

        city_unblocked = city.city_graph.copy(as_view=False)
        city_unblocked.remove_nodes_from(blocked_nodes)

        """
        We now initiate all of our pedestrians, assigning each one of the random pairs of start/end points
        and using that to construct a generator of all shortest paths for each pedestrian

        """

        pedestrians = []
        ped_num = 1
        for start, end in combined_nodes:
            pedestrians.append(
                Pedestrian("Ped" + str(ped_num), city, start, end, nx.all_shortest_paths(city_unblocked, start, end)))
            ped_num += 1

        return pedestrians


def __str__(self) -> str:
    return "Name: {}, Started: {}, Destination: {})".format(self.name, self.start_location, self.destination)

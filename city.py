import random
from enum import Enum
from typing import (List,
                    Tuple, )

import matplotlib.pyplot as plt
import networkx as nx


class GeoLocation(object):
    """
    Represents the physical geographical location of a place in terms of latitude and longitude.

    >>> GeoLocation(12, 10).latitude
    12
    >>> GeoLocation(12, 10).longitude
    10
    >>> GeoLocation(10, 10) == GeoLocation(10, 10)
    True
    >>> GeoLocation(12, 10)
    (12, 10)

    For simplicity, for the purpose of this application, latitude and longitude are only assumed to be integers.
    """

    def __init__(self, latitude: int, longitude: int):

        if latitude < 0:
            raise ValueError("latitude cannot be < 0")
        if longitude < 0:
            raise ValueError("longitude cannot be < 0")

        self.latitude = latitude
        self.longitude = longitude

    def latitude(self) -> int:
        return self.latitude

    def longitude(self) -> int:
        return self.longitude

    def __str__(self) -> str:
        return "({}, {})".format(self.latitude, self.longitude)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.latitude == o.latitude and self.longitude == o.longitude
        else:
            return False

    def __hash__(self) -> int:
        return 71 * hash(self.latitude) * hash(self.longitude)


class CityLocationType(Enum):
    """
    Represents the type of a block (called location in this simulation) in city.
    """
    residence = 1
    business = 2
    blockage = 3
    walkway = 4


class CityLocation(object):
    """
    A CityLocation (city block) is identified by a physical location (GeoLocation) and a location type (
    CityLocationType)

    Note: This is a simplified representation of city block for the purpose of this application. It is understood in
    actuality a block might be a collection of geo locations.

    >>> CityLocation(GeoLocation(10, 12), CityLocationType.residence).is_business()
    False
    >>> CityLocation(GeoLocation(10, 12), CityLocationType.residence).is_residence()
    True
    >>> CityLocation(GeoLocation(10, 12), CityLocationType.residence)
    residence, (10, 12)
    """

    def __init__(self, geo_location: GeoLocation, location_type: CityLocationType):
        self.geo_location = geo_location
        self.location_type = location_type

    def geo_location(self) -> GeoLocation:
        return self.location

    def location_type(self) -> CityLocationType:
        return self.location_type

    def is_residence(self) -> bool:
        return self.location_type == CityLocationType.residence

    def is_business(self) -> bool:
        return self.location_type == CityLocationType.business

    def is_walkway(self) -> bool:
        return self.location_type == CityLocationType.walkway

    def is_blocked(self) -> bool:
        return self.location_type == CityLocationType.blockage

    def __str__(self) -> str:
        return "{}, {}".format(self.location_type.name, self.geo_location.__str__())

    def __repr__(self):
        return self.__str__()

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.geo_location == o.geo_location and self.location_type == o.location_type
        else:
            return False

    def __hash__(self) -> int:
        return 29 * hash(self.geo_location.__hash__) * hash(self.location_type.__hash__)


# Of all locations in the city 30% should be walkways, 30% residences, 25% businesses, and 15% blockages.
CITY_LOCATION_TYPE_WEIGHT_DISTRIBUTION_ = [(CityLocationType.walkway, 35), (CityLocationType.residence, 25),
                                           (CityLocationType.business, 35), (CityLocationType.blockage, 5)]


class City:
    """

    A City is represented both as a matrix (List[List[CityLocation]]) and as a NetworkX graph. Matrix representation
    is used for simplicity of generation, but the more important graph notation is used for running simulations and
    calculating statistics.

    >>> len(City([[CityLocation(GeoLocation(1, 2), CityLocationType.residence)], [CityLocation(GeoLocation(3, 4),
    ... CityLocationType.business)]]).city_graph.nodes())
    2

    """

    def __init__(self, grid_map: List[List[CityLocation]]):
        self.grid_map = grid_map
        self.city_graph = self.generate_graph_from_grid_map(grid_map)

    @classmethod
    def generate_graph_from_grid_map(cls, grid_map: List[List[CityLocation]]) -> nx.Graph:

        """
        Generates a nx.Graph of city from a 2D grid map (represented by List[List[CityLocation]]). All adjacent nodes
        are connected by edges. Edges are blocked (can not be traversed) when location type is blocked.

        >>> City.generate_graph_from_grid_map([[CityLocation(GeoLocation(1, 2), CityLocationType.residence)],
        ... [CityLocation(GeoLocation(3, 4), CityLocationType.business)]]).nodes()
        NodeView((residence, (1, 2), business, (3, 4)))

        :param grid_map: The 2D map of city in the form of List[List[CityLocation]]
        :return: A NetworkX Graph representing city.
        """
        city_graph = nx.Graph()

        # Add nodes for each point in the city 2D map
        for row in range(0, len(grid_map)):
            for column in range(0, len(grid_map[0])):
                city_graph.add_node(grid_map[row][column])

        # connect adjacent city nodes
        for row in range(0, len(grid_map)):
            for column in range(0, len(grid_map[0])):
                if row + 1 < len(grid_map):
                    cls.add_edge(city_graph, grid_map[row][column], grid_map[row + 1][column])
                if row - 1 >= 0:
                    cls.add_edge(city_graph, grid_map[row][column], grid_map[row - 1][column])
                if column + 1 < len(grid_map[0]):
                    cls.add_edge(city_graph, grid_map[row][column], grid_map[row][column + 1])
                if column - 1 >= 0:
                    cls.add_edge(city_graph, grid_map[row][column], grid_map[row][column - 1])

        return city_graph

    @classmethod
    def add_edge(cls, city_graph: nx.Graph, source: CityLocation, destination: CityLocation):
        """
        Adds an edge in the given graph between source and destination, marks edge as blocked when that path cannot
        be traversed.

        :param city_graph: The graph to add edge in
        :param source: The source of edge
        :param destination: The destination of edge

        """
        city_graph.add_edge(source, destination, blocked=source.is_blocked() or destination.is_blocked())

    @classmethod
    def generate_random_city(cls, rows: int, columns: int):
        """
        This is the main factory method that is used to generate a random city based on the grid size.

        >>> len(City.generate_random_city(30, 20).city_graph.nodes())
        600

        :param rows: The number of rows (East-West lanes in the city)
        :param columns:  The number of columns (North-South lanes in the city)
        :return: A city generated at random.
        """

        city_grid = []
        for row in range(0, rows):
            row_list = []
            for column in range(0, columns):
                location = CityLocation(GeoLocation(row, column),
                                        cls.get_random_location_type(CITY_LOCATION_TYPE_WEIGHT_DISTRIBUTION_))
                row_list.append(location)
            city_grid.append(row_list)

        return City(city_grid)

    @classmethod
    def get_random_location_type(cls, weight_distribution: List[Tuple]):

        """
        Generates a random location type for a city location based on provided weight distribution.

        >>> City.get_random_location_type([("loc1", 100), ("loc2", 0)])
        'loc1'
        >>> City.get_random_location_type([("loc1", 100), ("loc2", 0)])
        'loc1'
        >>> City.get_random_location_type([("loc1", 100), ("loc2", 0)])
        'loc1'
        >>> City.get_random_location_type([("loc1", 100), ("loc2", 0)])
        'loc1'
        >>> City.get_random_location_type([("loc1", 100), ("loc2", 0)])
        'loc1'
        >>> City.get_random_location_type([("loc1", 100), ("loc2", 0)])
        'loc1'
        >>> City.get_random_location_type([("loc1", 100), ("loc2", 0)])
        'loc1'

        :param weight_distribution: The distribution of relative weight of chance of getting each city location.
        :return: An one with city location type, based on probability
        """
        total = sum(w for c, w in weight_distribution)
        r = random.uniform(0, total)
        upto = 0
        for c, w in weight_distribution:
            if upto + w >= r:
                return c
            upto += w
        assert False, "Shouldn't get here"

    def print(self, as_graph: bool = False, as_grid: bool = True, mark_node_list: list = None,
              marked_node_legend: str = ""):
        """
        A utility function to print the city on console, and as a matplotlib network graph

        :param as_graph: prints the city as matplotlib graph when True
        :param as_grid: prints the city as 2D when True
        :param mark_node_list:  Marks these nodes on city graph as special when present.
        :param marked_node_legend: The legend of node to be marked

        """

        if as_grid:
            mark_geo_location_set = None
            if mark_node_list:
                mark_geo_location_set = set(
                    map(lambda loc: (loc.geo_location.latitude, loc.geo_location.longitude), mark_node_list))
            city = ""
            for row in self.grid_map:
                city_lane = "| "
                for location in row:
                    if mark_geo_location_set and (
                            location.geo_location.latitude, location.geo_location.longitude) in mark_geo_location_set:
                        city_lane = city_lane + "*    | "
                    elif location.is_walkway():
                        city_lane = city_lane + "     | "
                    elif location.is_blocked():
                        city_lane = city_lane + "X    | "
                    elif location.is_business():
                        city_lane = city_lane + "B    | "
                    elif location.is_residence():
                        city_lane = city_lane + "R    | "
                    elif mark_geo_location_set and (
                            location.geo_location.latitude, location.geo_location.longitude) in mark_geo_location_set:
                        city_lane = city_lane[0:2] + "*" + city_lane[3:]
                    else:
                        city_lane = city_lane + "     | "
                city = city + city_lane + "\n"

            print(city)
            print("Legend")
            print("R - Residence")
            print("B - Business")
            print("X - Blockage")
            print("  - Walkway")
            if mark_node_list:
                print("* - {}".format(marked_node_legend))

        if as_graph:

            pos = nx.random_layout(self.city_graph)

            walkway_locations = []
            business_locations = []
            residence_locations = []
            blocked_locations = []

            for location in self.city_graph.nodes():
                if location.is_walkway():
                    walkway_locations.append(location)
                if location.is_residence():
                    residence_locations.append(location)
                if location.is_business():
                    business_locations.append(location)
                if location.is_blocked():
                    blocked_locations.append(location)

            nx.draw_networkx_nodes(self.city_graph, pos, nodelist=walkway_locations, node_color="black", node_size=20,
                                   node_shape=".", alpha=0.8)
            nx.draw_networkx_nodes(self.city_graph, pos, nodelist=residence_locations, node_color="yellow",
                                   node_size=250, node_shape="s", alpha=0.8)
            nx.draw_networkx_nodes(self.city_graph, pos, nodelist=business_locations, node_color="blue", node_size=250,
                                   node_shape="o", alpha=0.8)
            nx.draw_networkx_nodes(self.city_graph, pos, nodelist=blocked_locations, node_color="red", node_size=200,
                                   node_shape="x", alpha=0.8)

            if mark_node_list:
                nx.draw_networkx_nodes(self.city_graph, pos, nodelist=mark_node_list, node_color="green", node_size=300,
                                       node_shape="*", alpha=1)

            nx.draw_networkx_edges(self.city_graph, pos, width=0.1, alpha=0.2)

            nx.write_gexf(self.city_graph, "city-gephi.gexf", encoding="utf-8")

            plt.title("City Graph - Total City Blocks({}), Residences({}), Businesses({}), Blockages({}), Walkways({"
                      "})".format(len(self.grid_map) * len(self.grid_map[0]), len(residence_locations),
                                  len(business_locations), len(blocked_locations), len(walkway_locations)),
                      fontsize="9")

            labels = ["walkway", "residence", "business", "blockage"]

            if mark_node_list:
                labels.append(marked_node_legend)

            legend = plt.legend(shadow=True, labels=labels, loc="lower left")

            for label in legend.get_texts():
                label.set_fontsize("small")

            for label in legend.get_lines():
                label.set_linewidth(5)

            plt.axis('off')

            # save as png
            if mark_node_list:
                plt.savefig("city-with-marked_locations.png")
            else:
                plt.savefig("city.png")
            plt.show(block=False)

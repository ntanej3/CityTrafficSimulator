import random
from enum import Enum
from typing import List

import matplotlib.pyplot as plt
import networkx as nx

import numpy as np


class GeoLocation(object):

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
    residence = 1
    business = 2
    blockage = 3
    walkway = 4


class CityLocation(object):

    def __init__(self, location: GeoLocation, location_type: CityLocationType):
        self.location = location
        self.location_type = location_type

    def location(self) -> GeoLocation:
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
        return "{}, {}".format(self.location_type, self.location.__str__())

    def __repr__(self):
        return self.__str__()

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.location == o.location and self.location_type == o.location_type
        else:
            return False

    def __hash__(self) -> int:
        return 29 * hash(self.location.__hash__) * hash(self.location_type.__hash__)


class City:

    def __init__(self, grid_map: List[List[CityLocation]], city_graph: nx.Graph):
        self.grid_map = grid_map
        self.city_graph = self.generate_graph_from_grid_map(grid_map)

    @classmethod
    def generate_graph_from_grid_map(cls, grid_map: List[List[CityLocation]]) -> nx.Graph:

        city_graph = nx.Graph()

        # Add nodes for each point in the city
        for row in range(0, len(grid_map)):
            for column in range(0, len(grid_map[0])):
                city_graph.add_node(grid_map[row][column])

        # connect city nodes
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
        city_graph.add_edge(source, destination, blocked=source.is_blocked() or destination.is_blocked())

    @classmethod
    def generate_random_city(cls, rows: int, columns: int):

        print("Generating a random city")

        weight_distribution = [(CityLocationType.walkway, 30), (CityLocationType.residence, 30),
                               (CityLocationType.business, 25), (CityLocationType.blockage, 15)]

        city_grid = []
        for row in range(0, rows):
            row_list = []
            for column in range(0, columns):
                location = CityLocation(GeoLocation(row, column), cls.get_random_location_type(weight_distribution))
                row_list.append(location)
            city_grid.append(row_list)

        return City(city_grid, nx.Graph())

    @classmethod
    def get_random_location_type(cls, weight_distribution: dict) -> CityLocationType:

        total = sum(w for c, w in weight_distribution)
        r = random.uniform(0, total)
        upto = 0
        for c, w in weight_distribution:
            if upto + w >= r:
                return c
            upto += w
        assert False, "Shouldn't get here"

    def print(self, as_graph: bool = False, as_grid: bool = True, top_node_list: list = None):

        if as_grid and len(self.grid_map) <= 50:
            top_node_set = None
            if top_node_list:
                top_node_set = set(map(lambda loc: (loc.location.latitude, loc.location.longitude), top_node_list))
            city = ""
            for row in self.grid_map:
                city_lane = "| "
                for location in row:
                    if top_node_set and (location.location.latitude, location.location.longitude) in top_node_set:
                        city_lane = city_lane + "*    | "
                    elif location.is_walkway():
                        city_lane = city_lane + "     | "
                    elif location.is_blocked():
                        city_lane = city_lane + "+    | "
                    elif location.is_business():
                        city_lane = city_lane + "B    | "
                    elif location.is_residence():
                        city_lane = city_lane + "R    | "
                    elif top_node_set and (location.location.latitude, location.location.longitude) in top_node_set:
                        city_lane = city_lane[0:2] + "*" + city_lane[3:]
                    else:
                        city_lane = city_lane + "     | "
                city = city + city_lane + "\n"

            print(city)
            print("Legend")
            print("R - Residence")
            print("B - Business")
            print("+ - Blockage")
            print("  - Walkway")
            if top_node_list:
                print("* - Location with most foot traffic")

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
                                   node_shape="x", alpha=0.8)
            nx.draw_networkx_nodes(self.city_graph, pos, nodelist=residence_locations, node_color="yellow",
                                   node_size=250, node_shape="s", alpha=0.8)
            nx.draw_networkx_nodes(self.city_graph, pos, nodelist=business_locations, node_color="blue", node_size=250,
                                   node_shape="o", alpha=0.8)
            nx.draw_networkx_nodes(self.city_graph, pos, nodelist=blocked_locations, node_color="red", node_size=200,
                                   node_shape="+", alpha=0.8)

            if top_node_list:
                nx.draw_networkx_nodes(self.city_graph, pos, nodelist=top_node_list, node_color="green", node_size=300,
                                       node_shape="*", alpha=1)

            nx.draw_networkx_edges(self.city_graph, pos, width=0.1, alpha=0.2)

            labels = dict([(loc, loc.location_type.name) for loc in self.city_graph.nodes()])
            # nx.draw_networkx_labels(self.city_graph, pos, labels, font_size=5, alpha=0.8)

            nx.write_gexf(self.city_graph, "city-gephi.gexf", encoding="utf-8")

            plt.title("City Graph - Total City Blocks({}), Residences({}), Businesses({}), Blockages({}), Walkways({"
                      "})".format(len(self.grid_map) * len(self.grid_map[0]), len(residence_locations),
                                  len(business_locations), len(blocked_locations), len(walkway_locations)),
                      fontsize="9")

            labels = ["walkway", "residence", "business", "blockage"]

            if top_node_list:
                labels.append("top_locations")

            legend = plt.legend(shadow=True, labels=labels, loc="lower left")

            for label in legend.get_texts():
                label.set_fontsize("small")

            for label in legend.get_lines():
                label.set_linewidth(5)

            plt.axis('off')
            if top_node_list:
                plt.savefig("city-with-top-location.png")
            else:
                plt.savefig("city.png")  # save as png
            plt.show(block=False)

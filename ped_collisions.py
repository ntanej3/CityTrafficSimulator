"""
IS590 Monte Carlo Simulation: Optimizing Pedestrian Collision in a Path Network

By Neha Taneja
and Nicholas Wolf

"""

# !/usr/bin/python3

from city import (City,
                  CityLocation, )
from pedestrian import Pedestrian
import random
import networkx as nx
from beautifultable import BeautifulTable

from typing import Tuple


def query_number_pedestrians(grid_size) -> Tuple[int, int]:
    """
    Function to query user for number of pedestrians to use for the simulation
    :return: integer greater than 0
    """
    while True:
        min_num_peds = input("Simulation Variable:\tMinimum pedestrians for this simulation: ")
        max_num_peds = input("Simulation Variable:\tMaximum pedestrians for this simulation: ")
        try:
            int(min_num_peds)
            int(max_num_peds)

            if 1 <= int(min_num_peds) <= int(max_num_peds) <= grid_size * grid_size:
                return int(min_num_peds), int(max_num_peds)
                break
            else:
                print("Invalid response. You have either select a number less than 1 or have an insufficient grid "
                      "size for this number of pedestrians.")
        except:
            print("Invalid response. Try again.")


def query_size_grid() -> int:
    """
    Function to query user for size of city grid to use for the simulation
    :return: integer greater than 0 and less than/equal to 40
    """
    while True:
        size_grid = input("Fixed:\tSize of city grid to use for the simulation: ")
        try:
            int(size_grid)
            if 10 <= int(size_grid):
                return int(size_grid)
                break
            else:
                print("Invalid response. Please select a size >= 10 for good simulation")
        except:
            print("Invalid response. Try again.")


def query_number_simulations() -> int:
    """
    Function to query user for number of simulations to run
    :return: integer greater than 0
    """
    while True:
        num_simuls = input("Fixed:\tNumber of simulations to run: ")
        try:
            int(num_simuls)
            if int(num_simuls) >= 1:
                return int(num_simuls)
                break
            else:
                print("Invalid response.")
        except:
            print("Invalid response. Try again.")


def run_simulation(city, num_peds):
    pedestrians = Pedestrian.generate_random_pedestrians(num_peds, city)

    """
    We create a count of how many times a node (CityLocation object) appears in 
    the shortest simple paths of pedestrians, indicating a "hot spot" in the grid. We also
    examine the number of times that a node is occupied by a pedestrian
    on a path at the "same time," i.e. in the same index position in a pathway, as another
    node. This indicates frequent "collisions" of pedestrians at the same place at same time.
    We exclude start and destination nodes from this count.
    """

    intersect_dict = {}

    for ped in pedestrians:
        shortest_path = ped.shortest_path
        node_position = 1
        for short_path_node in shortest_path[1:-1]:
            count = intersect_dict.get(short_path_node, 0)
            intersect_dict[short_path_node] = count + 1
            node_position += 1

    return sorted(intersect_dict.items(), key=lambda x: x[1], reverse=True)


def print_outtable(simulation_summary, grid_size):
    print("\nSimulation Summary\n")
    """
    A helper function to pretty print a table of results
    :param results_dict:
    :param grid_size:
    :return: None (prints ASCII table)
    """
    table = BeautifulTable()
    table.column_headers = ["City Grid Size", "Number of Simulations", "Number of Pedestrians", "Top Location Node",
                            "Highest Number of Pedestrian Collisions for Node"]

    max_collisions = 0
    top_place = None

    print(simulation_summary)
    for simulation_number in simulation_summary:
        pedestrian_report = simulation_summary[simulation_number]
        for pedestrian_count in pedestrian_report:
            collisions = pedestrian_report[pedestrian_count]["Number_Collisions"]
            if collisions >= max_collisions:
                top_place = pedestrian_report[pedestrian_count]["Top_Location"]
            table.append_row(
                [str(grid_size), str(simulation_number), str(pedestrian_report[pedestrian_count]["Pedestrians"]),
                 str(pedestrian_report[pedestrian_count]["Top_Location"]),
                 str(pedestrian_report[pedestrian_count]["Number_Collisions"])])

    print(table)

    print("\nThe top location for pedestrian traffic is located at the node located at {} with {} collisions.\n".format(
        top_place, max_collisions))


def main():
    size = query_size_grid()  # Query user for size of city grid

    num_simuls = query_number_simulations()  # Query user for number of simulations to run

    (min_num_peds, max_num_peds) = query_number_pedestrians(size)  # Query user for number of pedestrians

    city = City.generate_random_city(size, size)  # Build the city network

    print("\nHere is the randomly generated city grid that will be used for simulation (also saved as city.png):\n")

    city.print(True, True)  # Display city network

    simulation_summary = {}  # Container for all results summary
    simulation = 1
    while simulation <= num_simuls:  # Run simulations and record results

        print("Running simulation {}".format(simulation))

        pedestrian_summary = {}
        for num_peds in range(min_num_peds, max_num_peds + 1):

            print("Number of pedestrians is {}".format(num_peds))

            intersection_list = run_simulation(city, num_peds)

            if intersection_list:
                pedestrian_summary[num_peds] = {
                    "Pedestrians": num_peds,
                    "City": city,
                    "Top_Location": intersection_list[0][0],
                    "Number_Collisions": intersection_list[0][1]
                }
            else:
                break
        simulation_summary[simulation] = pedestrian_summary
        simulation += 1

    print_outtable(simulation_summary, size)

    simulation_reports = []
    simulation_reports.extend([report for report in simulation_summary.values()])


if __name__ == main():
    main()

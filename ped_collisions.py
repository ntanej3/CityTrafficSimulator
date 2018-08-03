"""
IS590 Monte Carlo Simulation: Optimizing Pedestrian Collision in a Path Network

By Neha Taneja
and Nicholas Wolf

"""

#!/usr/bin/python3

from traffic_simuator import City, CityLocation
from pedestrian import Pedestrian
import random
import networkx as nx
from beautifultable import BeautifulTable

def query_number_pedestrians(grid_size):
    """
    Function to query user for number of pedestrians to use for the simulation
    :return: integer greater than 0
    """
    while True:
        num_peds = input("How many pedestrians for this simulation?")
        try:
            int(num_peds)
            if int(num_peds) >=1 and int(num_peds) <= grid_size/2:
                return(int(num_peds))
                break
            else:
                print("Invalid response. You have either select a number less than 1 or have an insufficient grid size\n \
                for this number of pedestrians. The number of pedestrians cannot exceed the number of residences \n \
                to serve as starting positions (common in small grids).")
        except:
            print("Invalid response. Try again.")

def query_size_grid():
    """
    Function to query user for size of city grid to use for the simulation
    :return: integer greater than 0 and less than/equal to 40
    """
    while True:
        size_grid = input("What size city grid to use for the simulation (select a number between 10 and 40):")
        try:
            int(size_grid)
            if int(size_grid) >= 10 and int(size_grid)<= 40:
                return(int(size_grid))
                break
            else:
                print("Invalid response. Select a number between 10 and 40")
        except:
            print("Invalid response. Try again.")


def query_number_simulations():
    """
    Function to query user for number of simulations to run
    :return: integer greater than 0
    """
    while True:
        size_grid = input("How many simulations to run?")
        try:
            int(size_grid)
            if int(size_grid) >= 1:
                return(int(size_grid))
                break
            else:
                print("Invalid response. Select a number greater than 0")
        except:
            print("Invalid response. Try again.")


def intersect_count(count_dict, node_object, node_position):
    try:
        count_dict[node_object]["total_count"] += 1
    except KeyError:
        count_dict[node_object]  = {"total_count":1, "position_collisions":{}}
    try:
        count_dict[node_object]["position_collisions"][node_position] += 1
    except KeyError:
        count_dict[node_object]["position_collisions"][node_position] = 1
    return count_dict


def run_simulation(city, num_peds):
    """
    For pedestrian start origins, we randomly select, without replacement, n number of residences from city grid,
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
        pedestrians.append(Pedestrian("Ped" + str(ped_num), start, end, nx.all_shortest_paths(city_unblocked, start, end)))
        ped_num += 1

    """
    Finally, we create a count of how many times a node (CityLocation object) appears in 
    the shortest simple paths of pedestrians, indicating a "hot spot" in the grid. We also
    examine the number of times that a node is occupied by a pedestrian
    on a path at the "same time," i.e. in the same index position in a pathway, as another
    node. This indicates frequent "collisions" of pedestrians at the same place at same time.
    We exclude start and destination nodes from this count.
    """

    intersect_dict = {}

    for ped in pedestrians:
        for short_path in ped.list_short_paths:
            node_position = 1
            for short_path_node in short_path[1:-1]:
                intersect_dict = intersect_count(intersect_dict, short_path_node, node_position)
                node_position+=1

    return sorted(intersect_dict.items(), key=lambda x: x[1]["total_count"], reverse=True)


def print_outtable(results_dict, grid_size):
    """
    A helper function to pretty print a table of results
    :param results_dict:
    :param grid_size:
    :return: None (prints ASCII table)
    """
    table = BeautifulTable()
    table.column_headers = ["Simulation Number", "City Grid Size", "Number Pedestrians",
                           "Top Location Node", "Number of Times Node in a Pedestrian Path",
                            "Highest Number of Pedestrian Collisions for Node"]
    for result in results_dict:
        table.append_row([str(result), str(grid_size),
                         str(results_dict[result]["Pedestrians"]),
                         str(results_dict[result]["Top_Location"]),
                         str(results_dict[result]["Number_Intersections"]),
                         str(results_dict[result]["Number_Collisions"])])
    print(table)


def main():

    simulation_summary = {}                         # Container for all results summary

    num_simuls = query_number_simulations()         # Query user for number of simulations to run

    size = query_size_grid()                        # Query user for size of city grid

    num_peds = query_number_pedestrians(size)       # Query user for number of pedestrians

    city = City.generate_random_city(size, size)    # Build the city network

    print("Here is the generated city grid that will be tested:")

    city.print(True, True)                         # Display city network

    while num_simuls > 0:                           # Run simulations and record results
        results_list = run_simulation(city, num_peds)
        if results_list:
            top_collision_count_list = sorted(results_list[0][1]["position_collisions"].items(),
                                                            key=lambda x: x[1], reverse=True)
            top_collision_count = top_collision_count_list[0][1]
            simulation_summary[num_simuls] = {"Pedestrians":num_peds,
                                              "City":city,
                                              "Top_Location":results_list[0][0],
                                              "Number_Intersections":results_list[0][1]["total_count"],
                                              "Number_Collisions":top_collision_count}
        else:
            break
        num_simuls-=1



    print_outtable(simulation_summary, size)
    top_place = sorted(simulation_summary.items(), key=lambda x: x[1]["Number_Intersections"],
                                                                         reverse=True)[0]
    print("The top location for pedestrian traffic is located at the node located \n \
     at lat-long {}".format(top_place[1]["Top_Location"].location))



if __name__ == main():
    main()
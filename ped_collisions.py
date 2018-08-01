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

def query_number_pedestrians():
    """
    Function to query user for number of pedestrians to use for the simulation
    :return: integer whole number greater than 0
    """
    while True:
        num_peds = input("How many pedestrians for this simulation?")
        try:
            int(num_peds)
            if int(num_peds) >=1:
                return(int(num_peds))
                break
            else:
                print("Invalid response. Select a number greater than 0")
        except:
            print("Invalid response. Try again.")

def query_size_grid():
    """
    Function to query user for size of city grid to use for the simulation
    :return: integer whole number greater than 0 and less than/equal to 10
    """
    while True:
        size_grid = input("What size city grid to use for the simulation (select a number between 1 and 10):")
        try:
            int(size_grid)
            if int(size_grid) >= 1 and int(size_grid)<= 10:
                return(int(size_grid))
                break
            else:
                print("Invalid response. Select a number between 1 and 10")
        except:
            print("Invalid response. Try again.")


def query_number_simulations():
    """
    Function to query user for number of simulations to run
    :return: integer whole number greater than 0
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


def collision_count(count_dict, node_object):
    try:
        count_dict[node_object] += 1
    except KeyError:
        count_dict[node_object]  = 1
    return count_dict


def run_simulation(city, num_peds):
    """
    For pedestrian start origins, we randomly select, without replacement, n number of residences from city grid,
    one for each pedestrian
    """

    res_nodes = [i for i in city.city_graph.nodes() if CityLocation.is_residence(i) == True]

    start_nodes = random.sample(res_nodes, num_peds)

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
    We now build all of our pedestrians, assigning each one of the random pairs of start/end points
    and using that to construct a generator of all shortest paths for each pedestrian
    
    """

    pedestrians = []
    ped_num = 1
    for start, end in combined_nodes:
        pedestrians.append(Pedestrian("Ped" + str(ped_num), start, end, nx.all_shortest_paths(city_unblocked, start, end)))
        ped_num += 1

    """
    Finally, we count all collisions (i.e. common nodes) between pedestrians that occur for all shortest paths
    between start and destinations available to pedestrians. The resulting dictionary contains nodes and the count
    of collisions that occur.
    
    """
    count_dict = {}

    for ped in pedestrians:
        for short_path in ped.list_short_paths:
            for short_path_node in short_path[1:-1]:
                count_dict = collision_count(count_dict, short_path_node)

    return sorted(count_dict.items(), key=lambda x: x[1], reverse=True)


def print_outtable(results_dict, grid_size):
    """
    A helper function to pretty print a table of results (needs work)
    :param results_dict:
    :param grid_size:
    :return:
    """
    table = "| Iteration Number | Grid Size | Number Pedestrians | Top Location | Number of Collisions |\n"
    for result in results_dict:
        row = "|\t\t" + str(result) + " | " + str(grid_size) \
              + " |\t\t" + str(results_dict[result]["Pedestrians"]) \
              + " |\t\t" + str(results_dict[result]["Top_Location"]) \
              + " |\t\t" + str(results_dict[result]["Number_Collisions"]) + " |\n"
        table+=row
    print(table)


def main():

    simulation_summary = {}                         # Container for all results summary

    num_simuls = query_number_simulations()         # Query user for number of simulations to run

    size = query_size_grid()                        # Query user for size of city grid

    num_peds = query_number_pedestrians()           # Query user for number of pedestrians

    city = City.generate_random_city(size, size)    # Build the city network

    city.print(False, True)                         # Display city network

    while num_simuls > 0:                           # Run simulations and record results
        results_list = run_simulation(city, num_peds)
        simulation_summary[num_simuls] = {"Pedestrians":num_peds,
                                          "City":city,
                                          "Top_Location":results_list[0][0],
                                          "Number_Collisions":results_list[0][1]}
        num_simuls-=1

    print_outtable(simulation_summary, size)



if __name__ == main():
    main()
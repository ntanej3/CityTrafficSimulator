"""
IS590 Monte Carlo Simulation: Optimizing Pedestrian Collision in a Path Network

By Neha Taneja
and Nicholas Wolf

"""

#!/usr/bin/python3

import networkx as nx

class Grid:

    def __init__(self, node_size: int, type: str):
        self.node_size = node_size
        self.type = type


    

    def __str__(self):
        return 'A grid of type ' + self.type + ' with ' + self.node_size + ' nodes'

    def __repr__(self):
        return self.__str__()


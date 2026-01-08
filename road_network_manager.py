from typing import Tuple, List, Optional

# Graph Operations for Road Networks
import networkx as nx
import numpy as np


class RoadNetworkManager:
    def __init__(self):
        """
        Initializes the road network manager.
        """
        # Underlying graph representing the road network
        self.graph = nx.DiGraph()  # Directed graph for one-way road segments

    def add_road(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """
        Adds a road segment between two points.

        Args:
            start: Starting point of the road (x, y).
            end: Ending point of the road (x, y).

        Returns:
            True if the road was added successfully, else False (e.g., already exists).
        """
        if self.graph.has_edge(start, end):
            return False  # Road already exists
        # Add edge with default weight (e.g., distance between tiles)
        distance = np.linalg.norm(np.array(end) - np.array(start))  # Euclidean distance
        self.graph.add_edge(start, end, weight=distance)
        return True

    def remove_road(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """
        Removes a road segment between two points.

        Args:
            start: Starting point of the road (x, y).
            end: Ending point of the road (x, y).

        Returns:
            True if the road was removed successfully, else False (e.g., road does not exist).
        """
        if not self.graph.has_edge(start, end):
            return False  # Road does not exist
        self.graph.remove_edge(start, end)
        return True

    def find_path(self, start: Tuple[int, int], destination: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Finds the shortest path between two points in the road network.

        Args:
            start: Starting point (x, y).
            destination: Endpoint (x, y).

        Returns:
            List of tuples representing the shortest path if one exists, else None.
        """
        try:
            path = nx.shortest_path(self.graph, source=start, target=destination, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None  # No path available

    def is_connected(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """
        Checks if two points are directly connected in the road network.

        Args:
            start: Starting point (x, y).
            end: Ending point (x, y).

        Returns:
            True if there is a direct road between the points, else False.
        """
        return self.graph.has_edge(start, end)

    def reset(self):
        """
        Resets the road network, clearing all roads and intersections.
        """
        self.graph.clear()
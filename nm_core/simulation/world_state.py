from typing import List, Dict

import numpy as np


class WorldState:
    def __init__(self,
                 map_data: np.ndarray,
                 cars: List[Dict],
                 destinations: List[Dict],
                 score: int,
                 time_elapsed: float,
                 is_game_over: bool):
        """
        Args:
            map_data: 2D NumPy array representing the tile grid for the map.
            cars: List of cars, where each car is a dictionary containing its position and status.
            destinations: List of destination buildings and their properties.
            score: Current game score.
            time_elapsed: Elapsed time in the game simulation.
            is_game_over: Boolean indicating if the game has ended.
        """
        self.map_data = map_data
        self.cars = cars
        self.destinations = destinations
        self.score = score
        self.time_elapsed = time_elapsed
        self.is_game_over = is_game_over
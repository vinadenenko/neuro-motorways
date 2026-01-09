from typing import Optional

import numpy as np


class GameMap:
    def __init__(self, width: int, height: int):
        """
        Initializes the map as a 2D grid.

        Args:
            width: Width of the map in tiles.
            height: Height of the map in tiles.
        """
        # 2D NumPy array to represent the map grid
        self.grid = np.zeros((height, width), dtype=int)  # 0 = empty, 1 = road, 2 = building
        self.width = width
        self.height = height

    def add_tile(self, x: int, y: int, tile_type: int) -> bool:
        """
        Adds a specific type of tile to the map.

        Args:
            x: X-coordinate of the tile.
            y: Y-coordinate of the tile.
            tile_type: The type of tile (0 = empty, 1 = road, 2 = building).

        Returns:
            True if the tile is added successfully, else False (e.g., out of bounds).
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = tile_type
            return True
        return False  # Out of bounds

    def remove_tile(self, x: int, y: int) -> bool:
        """
        Removes a tile (sets it to empty).

        Args:
            x: X-coordinate of the tile.
            y: Y-coordinate of the tile.

        Returns:
            True if the tile is removed successfully, else False (e.g., out of bounds).
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = 0  # Set to empty
            return True
        return False  # Out of bounds

    def get_tile(self, x: int, y: int) -> Optional[int]:
        """
        Gets the type of tile at a specific location.

        Args:
            x: X-coordinate.
            y: Y-coordinate.

        Returns:
            The tile type if the coordinates are valid, else None.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None  # Out of bounds
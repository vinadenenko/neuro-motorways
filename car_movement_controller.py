from typing import Tuple, List


class Car:
    def __init__(self, car_id: int, start: Tuple[int, int], destination: Tuple[int, int], path: List[Tuple[int, int]]):
        """
        Initialize a car object.

        Args:
            car_id: Unique identifier for this car.
            start: (x, y) coordinate of the starting position.
            destination: (x, y) coordinate of the destination.
            path: List of (x, y) tuples representing the car's planned path.
        """
        self.car_id = car_id
        self.position = start
        self.destination = destination
        self.path = path
        self.path_index = 0  # Index in the path that the car is currently following.
        self.active = True  # Whether the car is active (reaching the destination or despawned).

    def move(self):
        """
        Move the car to the next position along its path.
        """
        # If car has already reached the destination, remain idle
        if not self.active or self.path_index >= len(self.path):
            return

        # Move to the next tile in the path
        self.position = self.path[self.path_index]
        self.path_index += 1

        # Check if the car has finished its journey
        if self.path_index >= len(self.path):
            self.active = False  # Car is no longer active (reached destination)
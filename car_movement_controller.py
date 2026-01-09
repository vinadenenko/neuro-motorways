from typing import Tuple, List, Optional


class Car:
    def __init__(self, car_id: str, start: Tuple[int, int], destination: Optional[Tuple[int, int]], path: List[Tuple[int, int]]):
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
        self.state = "Idle"  # Tracks the car's task-based state
        self.origin = start  # To know where to return
        self.color = "red"  # Default color

    def set_route(self, path: List[Tuple[int, int]]):
        """
        Assign a route for the car to follow.
        """
        self.path = path
        self.path_index = 0
        self.active = True

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
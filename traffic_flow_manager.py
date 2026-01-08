from typing import Tuple, List, Dict

from car_movement_controller import Car
from road_network_manager import RoadNetworkManager


class TrafficFlowManager:
    def __init__(self, road_network: RoadNetworkManager):
        """
        Initialize the traffic flow manager.

        Args:
            road_network: Instance of the RoadNetworkManager to handle pathfinding.
        """
        self.road_network = road_network
        self.cars = {}  # A dictionary of active cars {car_id: Car}
        self.next_car_id = 0  # Counter to assign unique IDs to cars

    def spawn_car(self, start: Tuple[int, int], destination: Tuple[int, int]) -> bool:
        """
        Spawns a car at a given start position with a destination.

        Args:
            start: (x, y) coordinate of the spawn point.
            destination: (x, y) coordinate of the destination.

        Returns:
            True if the car was spawned, otherwise False (e.g., no valid path).
        """
        # Find path from start to destination
        path = self.road_network.find_path(start, destination)
        if path is None:
            return False  # No path exists for this car, vehicle cannot spawn

        # Create a new car and add it to the manager
        new_car = Car(car_id=self.next_car_id, start=start, destination=destination, path=path)
        self.cars[self.next_car_id] = new_car
        self.next_car_id += 1
        return True

    def update(self):
        """
        Updates all cars by moving them along their respective paths.
        """
        cars_to_remove = []
        for car_id, car in self.cars.items():
            # Update car's position
            car.move()
            # Check if the car is no longer active
            if not car.active:
                cars_to_remove.append(car_id)  # Mark car for removal

        # Remove inactive cars
        for car_id in cars_to_remove:
            del self.cars[car_id]

    def get_cars(self) -> List[Dict]:
        """
        Returns a list of all active cars and their statuses.

        Returns:
            List of dictionaries, where each dictionary contains car information.
        """
        return [
            {
                'car_id': car.car_id,
                'position': car.position,
                'destination': car.destination,
                'active': car.active
            }
            for car in self.cars.values()
        ]
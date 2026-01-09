# entities/house.py
from typing import Tuple, List, Optional, TYPE_CHECKING
from nm_core.entities.car import Car
from nm_common.constants import DEFAULT_CAR_LIMIT

if TYPE_CHECKING:
    from nm_core.simulation.traffic import TrafficFlowManager

class House:
    def __init__(self, house_id: str, location: Tuple[int, int], traffic_manager: 'TrafficFlowManager', color: str = "red", car_count: int = DEFAULT_CAR_LIMIT):
        """
        Initialize a house object (garage).

        Args:
            house_id: Unique identifier for this house.
            location: (x, y) location of the house on the grid.
            traffic_manager: Reference to the traffic flow manager for task coordination.
            color: Color of the house. Should match shopping center color for car dispatch.
            car_count: Number of cars available in the house. Default is 2.
        """
        self.house_id = house_id
        self.location = location
        self.traffic_manager = traffic_manager
        self.color = color
        self.cars = [Car(car_id=f"{house_id}_{i}", start=location, destination=None, path=[]) for i in range(car_count)]
        for car in self.cars:
            car.color = color # Cars inherit house color
        self.idle_cars: List[Car] = list(self.cars)  # Track idle cars
        for car in self.cars:
            car.active = False # Cars in house are initially inactive

    def dispatch_car(self, target_location: Tuple[int, int]) -> bool:
        """
        Dispatch an idle car to a target location (shopping center).

        Args:
            target_location: The (x, y) location of the shopping center.

        Returns:
            True if a car was dispatched, False if no car is available.
        """
        if not self.idle_cars:
            return False  # No cars available

        # Check if path exists before popping
        route = self.traffic_manager.road_network.find_path(self.location, target_location)
        if not route:
            return False

        car = self.idle_cars.pop()
        car.set_route(route)
        car.destination = target_location
        car.state = "ToShoppingCenter"  # Update the car state
        car.active = True
        self.traffic_manager.add_car_to_simulation(car)  # Register the car as active in the simulation
        return True

    def return_car(self, car: Car):
        """
        Return a car to the house after completing its task.

        Args:
            car: The car that has returned.
        """
        car.state = "Idle"
        car.path = []
        car.path_index = 0
        car.position = self.location
        car.destination = None
        car.active = False
        self.idle_cars.append(car)
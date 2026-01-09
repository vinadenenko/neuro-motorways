from typing import Tuple, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from house_car_management import House
    from shopping_center_pin_manager import ShoppingCenter

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
        self.cars: Dict[str, Car] = {}  # A dictionary of active cars {car_id: Car}
        self.houses: List['House'] = []
        self.shopping_centers: List['ShoppingCenter'] = []

    def add_car_to_simulation(self, car: Car):
        """
        Adds a car to the active simulation tracking.
        """
        self.cars[car.car_id] = car

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
        car_id = f"spawned_{len(self.cars)}"
        new_car = Car(car_id=car_id, start=start, destination=destination, path=path)
        self.cars[car_id] = new_car
        return True

    def update(self):
        """
        Updates all cars by moving them along their respective paths.
        """
        cars_to_remove = []
        for car_id, car in self.cars.items():
            # Update car's position
            car.move()
            
            # Check if the car has finished its journey
            if not car.active:
                if car.state == "ToShoppingCenter":
                    # Car arrived at shopping center, fulfill pin and return home
                    for sc in self.shopping_centers:
                        # Match location AND color
                        if sc.location == car.destination and sc.color == car.color:
                            if sc.fulfill_pin():
                                # We can't easily return score here, but we can have a callback or just increment a counter in sc
                                pass
                            break
                    
                    # Set route back home
                    home_path = self.road_network.find_path(car.position, car.origin)
                    if home_path:
                        car.set_route(home_path)
                        car.destination = car.origin
                        car.state = "ReturningHome"
                        car.active = True
                    else:
                        # Cannot find path back home, just remove it (should not happen in good road network)
                        cars_to_remove.append(car_id)
                
                elif car.state == "ReturningHome":
                    # Car arrived back at house
                    for house in self.houses:
                        if house.location == car.position:
                            house.return_car(car)
                            break
                    cars_to_remove.append(car_id)
                else:
                    # Generic spawned car reached destination
                    cars_to_remove.append(car_id)

        # Remove inactive cars
        for car_id in cars_to_remove:
            if car_id in self.cars:
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
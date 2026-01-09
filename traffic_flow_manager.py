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
        Updates all cars by moving them along their respective paths, considering traffic and directions.
        """
        cars_to_remove = []
        
        # Track occupied positions and their directions to handle two-sided roads and traffic jams
        # occupied maps (position, next_position) -> car_id
        occupied = {}

        # First, mark current positions as occupied (where they ARE now and where they are HEADED)
        for car in self.cars.values():
            if car.active:
                next_pos = car.get_next_position()
                occupied[(car.position, next_pos)] = car.car_id

        # To avoid cars from different directions overlapping on the same tile at intersections
        # we track which tiles are "claimed" for entry in this step.
        tile_claims = {} # next_pos -> car_id

        for car_id, car in self.cars.items():
            if not car.active:
                continue

            next_pos = car.get_next_position()
            if next_pos:
                # Find what would be the car's NEXT segment if it moved
                next_next_pos = None
                if car.path_index + 1 < len(car.path):
                    next_next_pos = car.path[car.path_index + 1]
                
                target_segment = (next_pos, next_next_pos)
                
                # COLLISION LOGIC:
                # 1. Is the target segment occupied? (Directly following someone)
                # 2. Is the target tile being entered by someone else from a DIFFERENT direction?
                #    (Wait, if it's a two-sided road, someone can enter from OPPOSITE direction safely)
                
                is_blocked = False
                
                # Check segment occupancy (standard queueing)
                for seg, other_car_id in occupied.items():
                    if other_car_id != car_id and seg == target_segment:
                        is_blocked = True
                        break
                
                # Check intersection conflict:
                # If someone else is ALREADY on next_pos AND they are NOT moving in the opposite direction of us.
                # Our direction: (next_pos[0] - position[0], next_pos[1] - position[1])
                # Their direction: (seg[1][0] - seg[0][0], seg[1][1] - seg[0][1]) if seg[1] exists
                
                my_dir = (next_pos[0] - car.position[0], next_pos[1] - car.position[1])
                
                if not is_blocked:
                    for (other_pos, other_next), other_car_id in occupied.items():
                        if other_car_id == car_id: continue
                        if other_pos == next_pos:
                            # Someone is on the tile we want to enter.
                            if other_next is None:
                                # They are at their destination, so they are blocking the tile.
                                is_blocked = True
                                break
                            
                            other_dir = (other_next[0] - other_pos[0], other_next[1] - other_pos[1])
                            # Opposite check: my_dir == (-other_dir[0], -other_dir[1])
                            if my_dir != (-other_dir[0], -other_dir[1]):
                                # They are not moving opposite to us (e.g. they are moving perpendicular or same)
                                # Actually if they are moving same direction, they should be covered by segment check,
                                # but they are ALREADY on the tile, so they are in segment (next_pos, other_next).
                                # If my target segment is (next_pos, next_next_pos) and they are in (next_pos, other_next),
                                # and next_next_pos != other_next, it means we are turning differently or they are at an intersection.
                                is_blocked = True
                                break

                # 3. Conflict with other cars TRYING to move to the same tile this step (priority)
                if not is_blocked:
                    if next_pos in tile_claims:
                        other_car_id = tile_claims[next_pos]
                        other_car = self.cars[other_car_id]
                        other_dir = (next_pos[0] - other_car.position[0], next_pos[1] - other_car.position[1])
                        if my_dir != (-other_dir[0], -other_dir[1]):
                            is_blocked = True

                if not is_blocked:
                    # Claim the tile for this step
                    tile_claims[next_pos] = car_id
                    
                    # Before moving, remove old occupancy and add new one
                    old_segment = (car.position, next_pos)
                    if old_segment in occupied:
                        del occupied[old_segment]
                    
                    car.move()
                    car.waiting = False
                    
                    # Update occupancy with new position
                    new_next = car.get_next_position()
                    occupied[(car.position, new_next)] = car.car_id
                else:
                    car.waiting = True
            else:
                # Car reached destination tile in its current path
                car.move() # This will set active=False
            
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
                'previous_position': car.previous_position,
                'next_position': car.get_next_position(),
                'destination': car.destination,
                'active': car.active,
                'color': car.color,
                'waiting': car.waiting
            }
            for car in self.cars.values()
        ]
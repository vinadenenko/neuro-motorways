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
        
        # We need a snapshot of where cars are and where they want to go
        # to make movement decisions without partial updates affecting other cars in the same step.
        
        # (position, next_position) -> car_id
        # This represents the segment a car is CURRENTLY occupying.
        current_segments = {}
        for car_id, car in self.cars.items():
            if car.active:
                next_pos = car.get_next_position()
                current_segments[(car.position, next_pos)] = car_id

        # To ensure fairness and avoid fixed-priority deadlocks, randomize processing order
        import random
        car_ids = list(self.cars.keys())
        random.shuffle(car_ids)

        # tile_claims: next_pos -> car_id (who is allowed to enter this tile this step)
        tile_claims = {}
        
        # moved_cars: car_ids that have successfully moved this step
        moved_cars = set()

        # We might need multiple passes if a car moving frees up space for another car
        # BUT in this simulation, if car A moves from tile 1 to tile 2, car B can move from tile 0 to tile 1
        # in the SAME step. This is handled by checking if the TARGET segment is occupied.
        # If car A is at (1,1) moving to (1,2), its current segment is ((1,1), (1,2)).
        # If car B is at (1,0) moving to (1,1), its target segment is ((1,1), (1,2)).
        # Wait, that's not right. 
        # If car A moves, ((1,1), (1,2)) becomes its new current segment.
        # Car B's target segment is ((1,1), (something)).
        
        # Let's simplify: 
        # A car at `pos` moving to `next_pos` wants to occupy segment `(next_pos, next_next_pos)`.
        # It is blocked if:
        # 1. Someone is already in `(next_pos, next_next_pos)`.
        # 2. Someone is at `next_pos` and NOT moving out in the same step (or moving opposite).
        
        # Actually, the sequential update with `occupied` mutation was almost correct for fluid movement, 
        # but the order and the collision logic were flawed.
        
        # Let's use the current positions but be careful about intersections.
        
        occupied_segments = current_segments.copy()
        tile_occupied_by = {car.position: car_id for car_id, car in self.cars.items() if car.active}

        for car_id in car_ids:
            car = self.cars[car_id]
            if not car.active:
                continue

            next_pos = car.get_next_position()
            if next_pos:
                next_next_pos = None
                if car.path_index + 1 < len(car.path):
                    next_next_pos = car.path[car.path_index + 1]
                
                target_segment = (next_pos, next_next_pos)
                my_dir = (next_pos[0] - car.position[0], next_pos[1] - car.position[1])
                
                is_blocked = False
                
                # 1. Segment occupancy (Queueing)
                # If someone is in our target segment, we are blocked.
                if target_segment in occupied_segments:
                    is_blocked = True
                
                # 2. Tile occupancy (Intersection / Entry)
                if not is_blocked and next_pos in tile_occupied_by:
                    other_car_id = tile_occupied_by[next_pos]
                    other_car = self.cars[other_car_id]
                    other_next = other_car.get_next_position()
                    
                    if other_next is None:
                        # They are at their destination
                        is_blocked = True
                    else:
                        other_dir = (other_next[0] - next_pos[0], other_next[1] - next_pos[1])
                        # Opposite check
                        if my_dir != (-other_dir[0], -other_dir[1]):
                            is_blocked = True
                
                # 3. Conflict with others wanting the same tile
                if not is_blocked and next_pos in tile_claims:
                    other_car_id = tile_claims[next_pos]
                    other_car = self.cars[other_car_id]
                    other_dir = (next_pos[0] - other_car.position[0], next_pos[1] - other_car.position[1])
                    if my_dir != (-other_dir[0], -other_dir[1]):
                        is_blocked = True

                if not is_blocked:
                    # SUCCESS! Move the car
                    tile_claims[next_pos] = car_id
                    
                    # Update tracking
                    old_pos = car.position
                    old_segment = (old_pos, next_pos)
                    
                    if old_segment in occupied_segments:
                        del occupied_segments[old_segment]
                    if old_pos in tile_occupied_by:
                        del tile_occupied_by[old_pos]
                    
                    car.move()
                    car.waiting = False
                    
                    # New state
                    new_next = car.get_next_position()
                    occupied_segments[(car.position, new_next)] = car.car_id
                    tile_occupied_by[car.position] = car.car_id
                else:
                    car.waiting = True
            else:
                # Car reached destination tile in its current path
                # Despawn/State change handled below
                car.move() # active=False
                # Update tracking so someone can move into the tile we just vacated (if we were at destination)
                # Wait, car.move() here sets car.active = False.
                # We should probably clear it from tile_occupied_by if it was there.
                if car.position in tile_occupied_by:
                     del tile_occupied_by[car.position]
            
            # Post-move logic (Arrivals)
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
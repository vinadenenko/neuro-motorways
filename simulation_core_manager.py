from typing import Tuple, Dict, Optional, List

from action_parameters_handler import Action
from game_map_manager import GameMap
from road_network_manager import RoadNetworkManager
from traffic_flow_manager import TrafficFlowManager
from world_state_initialization import WorldState
from house_car_management import House
from shopping_center_pin_manager import ShoppingCenter


class SimulationCore:
    def __init__(self, width: int, height: int):
        """Initialize the simulation core."""
        self.map = GameMap(width, height)
        self.road_network = RoadNetworkManager()
        self.traffic_manager = TrafficFlowManager(self.road_network)
        self.houses: List[House] = []
        self.shopping_centers: List[ShoppingCenter] = []
        self.score = 0
        self.time_elapsed = 0.0
        self.is_game_over = False
        self.pin_generation_interval = 10  # Generate a pin every 100 steps

    def spawn_car(self, start: Tuple[int, int], destination: Tuple[int, int]) -> bool:
        """
        Spawns a car in the simulation.

        Args:
            start: (x, y) coordinate for the car's starting position.
            destination: (x, y) coordinate of the car's destination.

        Returns:
            True if the car was successfully spawned, otherwise False.
        """
        return self.traffic_manager.spawn_car(start, destination)

    def add_house(self, position: Tuple[int, int], color: str = "red", car_limit: int = 2):
        """Adds a house (garage) to the simulation."""
        house_id = f"house_{len(self.houses)}"
        house = House(house_id, position, self.traffic_manager, color, car_limit)
        self.houses.append(house)
        self.traffic_manager.houses.append(house)

    def add_shopping_center(self, position: Tuple[int, int], color: str = "red"):
        """Adds a shopping center to the simulation."""
        sc_id = f"sc_{len(self.shopping_centers)}"
        shopping_center = ShoppingCenter(sc_id, position, color)
        self.shopping_centers.append(shopping_center)
        self.traffic_manager.shopping_centers.append(shopping_center)

    def step(self, action: Optional[Action]) -> Tuple[WorldState, float, bool, Dict]:
        """
        Executes a single simulation step.

        Args:
            action: Action object specifying the player's or AI's move. Could be None.

        Returns:
            Tuple:
                - WorldState: Updated game state.
                - Reward: Reward for the action (if training an AI environment).
                - Done: Whether the game is over.
                - Info: Additional metadata for debugging.
        """
        # Process player/AI action if provided
        if action is not None:
            if action.action_type == 'add_road':  # Example action: Add a new road
                self.road_network.add_road(action.params['start'], action.params['end'])
            elif action.action_type == 'remove_road':  # Example action: Remove an existing road
                self.road_network.remove_road(action.params['start'], action.params['end'])
            # Additional action handlers could be added here.

        # Update traffic flow
        self.traffic_manager.update()

        # Update pins and dispatch cars
        if int(self.time_elapsed) % self.pin_generation_interval == 0 and self.shopping_centers:
            import random
            sc = random.choice(self.shopping_centers)
            sc.generate_pin()
            
        # Dispatch cars for pending pins
        for sc in self.shopping_centers:
            # Update failure timer (assuming 1 step = 1 unit of time, but we should use a proper dt)
            # For simplicity let's say 10 steps = 1 second
            if sc.update_failure_timer(0.1):
                self.is_game_over = True

            if sc.pins:
                # Try to dispatch a car from a house of the SAME color
                for house in self.houses:
                    if house.color == sc.color and house.dispatch_car(sc.location):
                        break

        # Update score, check game-over logic, and increment simulation time
        self.time_elapsed += 1

        # Calculate score based on total fulfilled pins
        self.score = sum(sc.fulfilled_counter for sc in self.shopping_centers)

        # Prepare the next WorldState to track game progress
        world_state = WorldState(
            map_data=self.map.grid,
            cars=self.traffic_manager.get_cars(),
            destinations=[
                {
                    'id': sc.center_id,
                    'location': sc.location,
                    'pins': len(sc.pins)
                }
                for sc in self.shopping_centers
            ],
            score=self.score,
            time_elapsed=self.time_elapsed,
            is_game_over=self.is_game_over
        )

        return world_state, 0, self.is_game_over, {}


from typing import Tuple, Dict, Optional

from action_parameters_handler import Action
from game_map_manager import GameMap
from road_network_manager import RoadNetworkManager
from traffic_flow_manager import TrafficFlowManager
from world_state_initialization import WorldState


class SimulationCore:
    def __init__(self, width: int, height: int):
        """Initialize the simulation core."""
        self.map = GameMap(width, height)
        self.road_network = RoadNetworkManager()
        self.traffic_manager = TrafficFlowManager(self.road_network)
        self.score = 0
        self.time_elapsed = 0.0
        self.is_game_over = False

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

        # Update score, check game-over logic, and increment simulation time
        self.time_elapsed += 1

        # Prepare the next WorldState to track game progress
        world_state = WorldState(
            map_data=self.map.grid,
            cars=self.traffic_manager.get_cars(),
            destinations=[],  # Destinations can be added later
            score=self.score,
            time_elapsed=self.time_elapsed,
            is_game_over=self.is_game_over
        )

        return world_state, 0, self.is_game_over, {}


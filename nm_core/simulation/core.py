from typing import Tuple, Dict, Optional, List

from nm_common.actions import Action
from nm_core.simulation.map import GameMap
from nm_core.simulation.road_network import RoadNetworkManager
from nm_core.simulation.traffic import TrafficFlowManager
from nm_core.simulation.world_state import WorldState
from nm_core.entities.house import House
from nm_core.entities.shopping_center import ShoppingCenter
from nm_common.constants import PIN_GENERATION_INTERVAL, SIMULATION_TICK_RATE


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
        self.pin_generation_interval = PIN_GENERATION_INTERVAL  # Generate a pin every 10 steps
        self.tick_accumulator = 0.0
        self.tick_duration = 1.0 / SIMULATION_TICK_RATE

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

    def step(self, action: Optional[Action], dt: Optional[float] = None) -> Tuple[WorldState, float, bool, Dict]:
        """
        Executes simulation steps based on elapsed time.

        Args:
            action: Action object specifying the player's or AI's move. Could be None.
            dt: Time elapsed since the last step in seconds. If None, exactly one logic tick is executed.

        Returns:
            Tuple: WorldState, Reward, Done, Info.
        """
        # Process player/AI action if provided (actions happen immediately)
        if action is not None:
            if action.action_type == 'add_road':
                self.road_network.add_road(action.params['start'], action.params['end'])
            elif action.action_type == 'remove_road':
                self.road_network.remove_road(action.params['start'], action.params['end'])

        if dt is None:
            # Legacy/Test mode: execute exactly one logic tick
            self._logic_tick()
            # Still update failure timers with a default tick duration
            for sc in self.shopping_centers:
                if sc.update_failure_timer(self.tick_duration):
                    self.is_game_over = True
        else:
            # Real-time mode: accumulate and execute ticks
            for sc in self.shopping_centers:
                if sc.update_failure_timer(dt):
                    self.is_game_over = True

            self.tick_accumulator += dt
            # Robustness: Cap the number of logic ticks per frame to prevent "Spiral of Death" 
            # if the CPU lags significantly.
            max_ticks_per_frame = 5 
            ticks_processed = 0
            while self.tick_accumulator >= self.tick_duration and ticks_processed < max_ticks_per_frame:
                self.tick_accumulator -= self.tick_duration
                self._logic_tick()
                ticks_processed += 1
            
            # If we hit the cap, discard remaining time to keep the game playable
            if ticks_processed >= max_ticks_per_frame:
                self.tick_accumulator = 0.0

        # Prepare the next WorldState
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

    def _logic_tick(self):
        """Internal logic tick executed at SIMULATION_TICK_RATE."""
        # Update traffic flow
        self.traffic_manager.update()

        # Update pins and dispatch cars
        if self.pin_generation_interval > 0 and int(self.time_elapsed) > 0 and int(self.time_elapsed) % self.pin_generation_interval == 0 and self.shopping_centers:
            import random
            sc = random.choice(self.shopping_centers)
            sc.generate_pin()
            
        # Dispatch cars for pending pins
        for sc in self.shopping_centers:
            # Calculate how many cars need to be dispatched
            needed_dispatches = len(sc.pins) - sc.dispatched_pins_count
            
            for _ in range(needed_dispatches):
                dispatched = False
                # Try to dispatch a car from a house of the SAME color
                for house in self.houses:
                    if house.color == sc.color and house.dispatch_car(sc.location):
                        sc.dispatched_pins_count += 1
                        dispatched = True
                        break
                if not dispatched:
                    break # No more cars available to dispatch for this SC right now

        # Increment simulation time (ticks)
        self.time_elapsed += 1

        # Calculate score based on total fulfilled pins
        self.score = sum(sc.fulfilled_counter for sc in self.shopping_centers)


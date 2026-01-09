import random
from typing import Tuple, List

from nm_common.constants import ESTIMATED_RTT

class GrowthManager:
    def __init__(self, simulation_core, difficulty: str = 'medium'):
        self.sim = simulation_core
        self.difficulty = difficulty
        self.colors = ["red", "blue", "green", "yellow", "purple"]
        self.active_colors = []
        self.step_counter = 0
        self.growth_interval = 200 # Spawn something every 200 steps
        
        # Difficulty multipliers for "need"
        # easy: 2.0x needed houses
        # medium: 1.2x needed houses
        # hard: 1.0x needed houses (bare minimum)
        self.difficulty_multipliers = {
            'easy': 2.0,
            'medium': 1.2,
            'hard': 1.0
        }

    def update(self):
        self.step_counter += 1
        if self.step_counter % self.growth_interval == 0:
            self.spawn_new_building()
            
    def _calculate_needs(self) -> dict:
        """
        Calculates how many houses are needed for each active color.
        
        Logic:
        - Each SC generates pins at a rate of 1 / pin_generation_interval.
        - Total demand for a color = (number of SCs of that color) / pin_generation_interval.
        - Each car can fulfill 1 pin per round trip.
        - Round trip time (RTT) estimated roughly as 2 * average distance (let's say 20 steps for now).
        - Capacity of one car = 1 / RTT.
        - Capacity of one house = car_limit / RTT.
        - Needed houses = Total demand / Capacity of one house.
        """
        needs = {}
        pin_rate = 1.0 / self.sim.pin_generation_interval
        estimated_rtt = ESTIMATED_RTT # Estimated round trip steps
        car_capacity = 1.0 / estimated_rtt
        
        for color in self.active_colors:
            sc_count = sum(1 for sc in self.sim.shopping_centers if sc.color == color)
            house_count = sum(1 for h in self.sim.houses if h.color == color)
            
            if sc_count == 0:
                needs[color] = 0
                continue
            
            # For each house, we assume default 2 cars (this matches SimulationCore.add_house default)
            car_limit = 2
            house_capacity = car_limit * car_capacity
            
            total_demand = sc_count * pin_rate
            needed_houses = total_demand / house_capacity
            
            # Apply difficulty multiplier
            needed_houses *= self.difficulty_multipliers.get(self.difficulty, 1.2)
            
            # In Mini Motorways, at least 1-2 houses are usually needed per SC to be safe
            # But the requirement says "mathematically needed quantity"
            needs[color] = {
                'needed': max(1, int(needed_houses)),
                'current': house_count,
                'demand': total_demand
            }
        return needs

    def spawn_new_building(self):
        needs = self._calculate_needs()
        
        # Check if any color urgently needs houses
        under_supplied = [c for c, n in needs.items() if n['current'] < n['needed']]
        
        if under_supplied:
            # Randomly pick one of the under-supplied colors
            color = random.choice(under_supplied)
            self.spawn_house(color=color)
        else:
            # If all colors are sufficiently supplied, decide whether to spawn a new SC or an extra house
            if random.random() < 0.3 or not self.sim.shopping_centers:
                self.spawn_shopping_center()
            else:
                # Spawn a house for a random active color (giving it more buffer)
                if self.active_colors:
                    self.spawn_house(color=random.choice(self.active_colors))
                else:
                    self.spawn_shopping_center()

    def spawn_shopping_center(self):
        pos = self._find_empty_pos()
        if pos:
            color = random.choice(self.colors)
            if color not in self.active_colors:
                self.active_colors.append(color)
            self.sim.add_shopping_center(pos, color=color)
            self.sim.map.add_tile(pos[0], pos[1], 2)
            print(f"Spawned shopping center at {pos} with color {color}")
            
            # Ensure at least one house of the same color is spawned
            self.spawn_house(color=color)
            
    def spawn_house(self, color=None):
        pos = self._find_empty_pos()
        if pos:
            if color is None:
                if not self.active_colors:
                    color = random.choice(self.colors)
                    self.active_colors.append(color)
                else:
                    color = random.choice(self.active_colors)
            
            self.sim.add_house(pos, color=color)
            self.sim.map.add_tile(pos[0], pos[1], 2)
            print(f"Spawned house at {pos} with color {color}")

    def _find_empty_pos(self) -> Tuple[int, int]:
        # Simple random search for an empty position
        # Avoid edges and existing buildings
        for _ in range(100):
            x = random.randint(1, self.sim.map.width - 2)
            y = random.randint(1, self.sim.map.height - 2)
            if self.sim.map.get_tile(x, y) == 0:
                # Check neighbors to avoid crowding (optional)
                return (x, y)
        return None

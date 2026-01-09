import random
from typing import Tuple, List

class GrowthManager:
    def __init__(self, simulation_core):
        self.sim = simulation_core
        self.colors = ["red", "blue", "green", "yellow", "purple"]
        self.active_colors = []
        self.step_counter = 0
        self.growth_interval = 200 # Spawn something every 200 steps
        
    def update(self):
        self.step_counter += 1
        if self.step_counter % self.growth_interval == 0:
            self.spawn_new_building()
            
    def spawn_new_building(self):
        # Decide whether to spawn a house or a shopping center
        # In Mini Motorways, shopping centers are rarer but more critical
        if not self.sim.shopping_centers or random.random() < 0.2:
            self.spawn_shopping_center()
        else:
            self.spawn_house()
            
    def spawn_shopping_center(self):
        pos = self._find_empty_pos()
        if pos:
            color = random.choice(self.colors)
            if color not in self.active_colors:
                self.active_colors.append(color)
            self.sim.add_shopping_center(pos, color=color)
            self.sim.map.add_tile(pos[0], pos[1], 2)
            print(f"Spawned shopping center at {pos} with color {color}")
            
    def spawn_house(self):
        pos = self._find_empty_pos()
        if pos:
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

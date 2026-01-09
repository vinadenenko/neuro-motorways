from nm_core.simulation.core import SimulationCore
from nm_clone.growth import GrowthManager
from nm_common.actions import Action

class MiniMotorwaysGame:
    def __init__(self, width: int, height: int, difficulty: str = 'medium'):
        self.sim = SimulationCore(width, height)
        self.growth_manager = GrowthManager(self.sim, difficulty=difficulty)
        self.is_running = True
        
        # Initial setup: one shopping center and one house of the same color
        self.growth_manager.spawn_shopping_center()
        
    def step(self, action=None, dt=0.0):
        if not self.is_running:
            return None, 0, True, {}
            
        # Execute simulation step
        world_state, reward, done, info = self.sim.step(action, dt=dt)
        
        # Update growth
        self.growth_manager.update(dt=dt)
        
        if done:
            self.is_running = False
            
        return world_state, reward, done, info

    def add_road(self, start, end):
        action = Action(action_type='add_road', params={'start': start, 'end': end})
        self.sim.step(action)

    def remove_road(self, start, end):
        action = Action(action_type='remove_road', params={'start': start, 'end': end})
        self.sim.step(action)

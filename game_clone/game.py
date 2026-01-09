from simulation_core_manager import SimulationCore
from game_clone.growth_manager import GrowthManager
from action_parameters_handler import Action

class MiniMotorwaysGame:
    def __init__(self, width: int, height: int):
        self.sim = SimulationCore(width, height)
        self.growth_manager = GrowthManager(self.sim)
        self.score = 0
        self.is_running = True
        
        # Initial setup: one shopping center and two houses of the same color
        self.growth_manager.spawn_shopping_center()
        self.growth_manager.spawn_house()
        self.growth_manager.spawn_house()
        
    def step(self, action=None):
        if not self.is_running:
            return None, 0, True, {}
            
        # Execute simulation step
        world_state, reward, done, info = self.sim.step(action)
        
        # Update growth
        self.growth_manager.update()
        
        # Update game score (can be based on fulfilled pins)
        # For now, let's use the simulation's time or some other metric if we have one
        # Actually, let's track score based on pin fulfillment. 
        # We need to expose fulfilled pins from simulation.
        
        if done:
            self.is_running = False
            
        return world_state, reward, done, info

    def add_road(self, start, end):
        action = Action(action_type='add_road', params={'start': start, 'end': end})
        self.sim.step(action)

    def remove_road(self, start, end):
        action = Action(action_type='remove_road', params={'start': start, 'end': end})
        self.sim.step(action)

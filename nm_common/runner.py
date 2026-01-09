import pygame
from nm_common.constants import FPS

class SimulationRunner:
    """
    A centralized runner to handle Pygame boilerplate and simulation stepping.
    """
    def __init__(self, simulation_core, fps=FPS):
        self.sim = simulation_core
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self, render_callback=None, input_callback=None, update_callback=None, max_steps=None):
        """
        Main loop for simulation and rendering.
        
        Args:
            render_callback: function(sim, screen, world_state)
            input_callback: function(event)
            update_callback: function(sim, dt)
            max_steps: optional limit for automated tests
        """
        step_count = 0
        screen = pygame.display.get_surface()
        if screen is None:
            # Fallback if pygame.display.set_mode wasn't called yet
            pygame.init()
            # Default size if not set
            from nm_common.constants import SCREEN_WIDTH, SCREEN_HEIGHT
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            
            # 1. Handle Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if input_callback:
                    input_callback(event)

            # 2. Update Simulation
            if update_callback:
                update_callback(self.sim, dt)
            
            world_state, _, done, _ = self.sim.step(None, dt=dt)
            
            # 3. Render
            if render_callback:
                render_callback(self.sim, screen, world_state)
            
            pygame.display.flip()

            step_count += 1
            if max_steps and step_count >= max_steps:
                self.running = False
            
            if done:
                self.running = False
                
        return step_count

import pygame
import sys
from game_clone.game import MiniMotorwaysGame

# Constants
GRID_SIZE = 40
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 15

# Color Map
COLOR_MAP = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 255, 0),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "gray": (100, 100, 100),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "bg": (230, 230, 220)
}

class GameVisualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mini Motorways Clone")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.game = MiniMotorwaysGame(SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE)
        self.running = True
        self.last_mouse_pos = None

    def run(self):
        while self.running:
            self.handle_input()
            world_state, _, done, _ = self.game.step()
            self.render(world_state)
            if done:
                print(f"Game Over! Final Score: {world_state.score}")
                self.running = False
            self.clock.tick(FPS)
        
        # Keep window open for a bit after game over
        pygame.time.wait(2000)
        pygame.quit()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click: build road
                    pos = self._get_grid_pos(event.pos)
                    self.last_mouse_pos = pos
                elif event.button == 3: # Right click: remove road
                    pos = self._get_grid_pos(event.pos)
                    # For simplicity, remove_road needs start and end. 
                    # We'll just remove all edges connected to this tile in a real impl.
                    pass

            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]: # Left button held
                    pos = self._get_grid_pos(event.pos)
                    if self.last_mouse_pos and self.last_mouse_pos != pos:
                        # Connect adjacent tiles
                        if abs(pos[0] - self.last_mouse_pos[0]) + abs(pos[1] - self.last_mouse_pos[1]) == 1:
                            self.game.add_road(self.last_mouse_pos, pos)
                            self.game.add_road(pos, self.last_mouse_pos)
                            self.last_mouse_pos = pos

    def _get_grid_pos(self, mouse_pos):
        return (mouse_pos[0] // GRID_SIZE, mouse_pos[1] // GRID_SIZE)

    def render(self, world_state):
        self.screen.fill(COLOR_MAP["bg"])
        
        # Draw grid
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, (210, 210, 200), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, (210, 210, 200), (0, y), (SCREEN_WIDTH, y))

        # Draw roads
        for road in self.game.sim.road_network.roads:
            start, end = road
            start_px = (start[0] * GRID_SIZE + GRID_SIZE // 2, start[1] * GRID_SIZE + GRID_SIZE // 2)
            end_px = (end[0] * GRID_SIZE + GRID_SIZE // 2, end[1] * GRID_SIZE + GRID_SIZE // 2)
            pygame.draw.line(self.screen, COLOR_MAP["gray"], start_px, end_px, 6)

        # Draw houses
        for house in self.game.sim.houses:
            rect = pygame.Rect(house.location[0] * GRID_SIZE + 4, house.location[1] * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)
            pygame.draw.rect(self.screen, COLOR_MAP.get(house.color, (0,0,0)), rect)
            # Draw idle cars count
            txt = self.font.render(str(len(house.idle_cars)), True, COLOR_MAP["white"])
            self.screen.blit(txt, (house.location[0] * GRID_SIZE + 8, house.location[1] * GRID_SIZE + 8))

        # Draw shopping centers
        for sc in self.game.sim.shopping_centers:
            rect = pygame.Rect(sc.location[0] * GRID_SIZE, sc.location[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, COLOR_MAP.get(sc.color, (0,0,0)), rect)
            # Draw pins
            for i in range(len(sc.pins)):
                px = sc.location[0] * GRID_SIZE + (i % 3) * 10 + 5
                py = sc.location[1] * GRID_SIZE + (i // 3) * 10 + 5
                pygame.draw.circle(self.screen, COLOR_MAP["white"], (px, py), 4)
            
            # Draw failure timer circle if failing
            if sc.is_failing:
                progress = sc.failure_timer / 60.0
                pygame.draw.arc(self.screen, (0, 0, 0), rect.inflate(10, 10), 0, progress * 2 * 3.14159, 3)

        # Draw cars
        for car_data in world_state.cars:
            pos = car_data['position']
            # We need color for car too, but world_state.cars currently doesn't have it.
            # Let's find the car in traffic manager for now or just draw green
            px = pos[0] * GRID_SIZE + GRID_SIZE // 4
            py = pos[1] * GRID_SIZE + GRID_SIZE // 4
            pygame.draw.rect(self.screen, (0, 200, 0), (px, py, GRID_SIZE // 2, GRID_SIZE // 2))

        # Draw UI
        score_txt = self.font.render(f"Score: {world_state.score}", True, (0, 0, 0))
        self.screen.blit(score_txt, (20, 20))
        
        pygame.display.flip()

if __name__ == "__main__":
    vis = GameVisualizer()
    vis.run()

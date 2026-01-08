import pygame
import time
from simulation_core_manager import SimulationCore

# Initialize Pygame-CE settings
GRID_SIZE = 40  # Size of each grid square in pixels
SCREEN_WIDTH = 400  # Total screen width in pixels
SCREEN_HEIGHT = 400  # Total screen height in pixels
FPS = 5  # Frames per second


# Function to render the simulation
def render(simulation_core, screen):
    """
    Renders the game grid, roads, and cars.

    Args:
        simulation_core: The simulation core instance running the backend logic.
        screen: The Pygame screen to draw on.
    """
    screen.fill((0, 0, 0))  # Clear the screen with a black background

    # Draw the grid
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)  # Draw grid lines

    # Draw the roads
    for road_segment in simulation_core.road_network.roads:
        start, end = road_segment
        road_color = (100, 100, 100)
        start_pixel = (start[0] * GRID_SIZE + GRID_SIZE // 2, start[1] * GRID_SIZE + GRID_SIZE // 2)
        end_pixel = (end[0] * GRID_SIZE + GRID_SIZE // 2, end[1] * GRID_SIZE + GRID_SIZE // 2)

        pygame.draw.line(screen, road_color, start_pixel, end_pixel, 5)  # Draw roads (thicker lines)

    # Draw the cars
    for car_data in simulation_core.traffic_manager.get_cars():
        car_position = car_data['position']
        car_rect = pygame.Rect(
            car_position[0] * GRID_SIZE + GRID_SIZE // 4,
            car_position[1] * GRID_SIZE + GRID_SIZE // 4,
            GRID_SIZE // 2,
            GRID_SIZE // 2,
        )
        pygame.draw.rect(screen, (0, 255, 0), car_rect)  # Green square for cars


# Main function to run the visualization
def main():
    pygame.init()

    # Create the Pygame screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Traffic Simulation")

    # Set up simulation core
    sim = SimulationCore(SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE)

    # Create a simple road network
    for x in range(9):
        sim.road_network.add_road((x, 5), (x + 1, 5))

    # Spawn cars
    sim.spawn_car((0, 5), (9, 5))
    sim.spawn_car((3, 5), (9, 5))

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update simulation
        sim.step(None)

        # Render simulation
        render(sim, screen)
        pygame.display.flip()

        # Frame delay
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
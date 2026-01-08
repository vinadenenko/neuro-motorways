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

    # Draw the houses
    for house in simulation_core.houses:
        house_rect = pygame.Rect(
            house.location[0] * GRID_SIZE + GRID_SIZE // 8,
            house.location[1] * GRID_SIZE + GRID_SIZE // 8,
            3 * GRID_SIZE // 4,
            3 * GRID_SIZE // 4,
        )
        pygame.draw.rect(screen, (0, 0, 255), house_rect)  # Blue for houses
        # Draw number of idle cars
        font = pygame.font.SysFont(None, 24)
        img = font.render(str(len(house.idle_cars)), True, (255, 255, 255))
        screen.blit(img, (house.location[0] * GRID_SIZE + 2, house.location[1] * GRID_SIZE + 2))

    # Draw the shopping centers
    for sc in simulation_core.shopping_centers:
        sc_rect = pygame.Rect(
            sc.location[0] * GRID_SIZE,
            sc.location[1] * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE,
        )
        pygame.draw.rect(screen, (255, 0, 0), sc_rect)  # Red for shopping centers
        # Draw pins
        for i, pin in enumerate(sc.pins):
            pin_rect = pygame.Rect(
                sc.location[0] * GRID_SIZE + (i % 3) * (GRID_SIZE // 3),
                sc.location[1] * GRID_SIZE + (i // 3) * (GRID_SIZE // 3),
                GRID_SIZE // 4,
                GRID_SIZE // 4,
            )
            pygame.draw.circle(screen, (255, 255, 255), pin_rect.center, GRID_SIZE // 8)

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

    # Set up a simulation core
    sim = SimulationCore(SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE)

    # Create a simple road network
    # Road from (1, 2) to (8, 2)
    for x in range(1, 8):
        sim.road_network.add_road((x, 2), (x + 1, 2))
        sim.road_network.add_road((x + 1, 2), (x, 2)) # Bidirectional for return

    # Add a house and a shopping center
    sim.add_house((1, 2))
    sim.add_shopping_center((8, 2))

    # Optional: spawn some manual cars
    # sim.spawn_car((1, 2), (8, 2))

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
import pygame
import time
from nm_core.simulation.core import  SimulationCore

# Initialize Pygame-CE settings
GRID_SIZE = 40  # Size of each grid square in pixels
SCREEN_WIDTH = 800  # Total screen width in pixels
SCREEN_HEIGHT = 600  # Total screen height in pixels
FPS = 10  # Frames per second


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

    # Helper to add bidirectional roads
    def add_bi_road(p1, p2):
        sim.road_network.add_road(p1, p2)
        sim.road_network.add_road(p2, p1)

    # Create a more complex road network
    # Horizontal main road
    for x in range(2, 18):
        add_bi_road((x, 5), (x + 1, 5))
    
    # Vertical roads
    for y in range(2, 12):
        if y != 5:
            add_bi_road((5, y), (5, y + 1))
        add_bi_road((15, y), (15, y + 1))
    
    # Connect vertical to horizontal
    add_bi_road((5, 5), (5, 6))
    add_bi_road((5, 4), (5, 5))
    add_bi_road((15, 5), (15, 6))
    add_bi_road((15, 4), (15, 5))

    # Add another horizontal road
    for x in range(5, 15):
        add_bi_road((x, 12), (x + 1, 12))
    
    # Connect the two horizontal roads
    for y in range(5, 12):
        add_bi_road((5, y), (5, y + 1))
        add_bi_road((15, y), (15, y + 1))
    
    # Houses
    sim.add_house((2, 5), car_limit=2)
    sim.add_house((5, 2), car_limit=2)
    sim.add_house((15, 2), car_limit=3)
    sim.add_house((10, 12), car_limit=2)

    # Shopping Centers
    sim.add_shopping_center((18, 5))
    sim.add_shopping_center((5, 12))
    sim.add_shopping_center((15, 12))

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
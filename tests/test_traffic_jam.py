import pygame
import sys
import time
from nm_core.simulation.core import SimulationCore
from nm_common.constants import GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_MAP

FPS = 5

def render(sim, screen, font, world_state):
    screen.fill(COLOR_MAP["bg"])
    
    # Draw roads
    for road in sim.road_network.roads:
        start, end = road
        start_px = (start[0] * GRID_SIZE + GRID_SIZE // 2, start[1] * GRID_SIZE + GRID_SIZE // 2)
        end_px = (end[0] * GRID_SIZE + GRID_SIZE // 2, end[1] * GRID_SIZE + GRID_SIZE // 2)
        pygame.draw.line(screen, COLOR_MAP["gray"], start_px, end_px, 6)

    # Draw houses
    for house in sim.houses:
        rect = pygame.Rect(house.location[0] * GRID_SIZE + 4, house.location[1] * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)
        pygame.draw.rect(screen, COLOR_MAP.get(house.color, (0,0,0)), rect)

    # Draw shopping centers
    for sc in sim.shopping_centers:
        rect = pygame.Rect(sc.location[0] * GRID_SIZE, sc.location[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, COLOR_MAP.get(sc.color, (0,0,0)), rect)

    # Draw cars
    # Sort cars by ID to make rendering consistent
    sorted_cars = sorted(world_state.cars, key=lambda x: x['car_id'])
    for car_data in sorted_cars:
        pos = car_data['position']
        prev_pos = car_data.get('previous_position', pos)
        next_pos = car_data.get('next_position')
        
        if next_pos:
            direction = (next_pos[0] - pos[0], next_pos[1] - pos[1])
        elif pos != prev_pos:
            direction = (pos[0] - prev_pos[0], pos[1] - prev_pos[1])
        else:
            direction = (0, 0)
        
        offset_scale = 6
        offset_x = -direction[1] * offset_scale
        offset_y = direction[0] * offset_scale
        
        car_color = COLOR_MAP.get(car_data.get('color', 'green'), (0, 200, 0))
        if car_data.get('waiting', False):
            car_color = tuple(max(0, c - 50) for c in car_color)

        px = pos[0] * GRID_SIZE + GRID_SIZE // 2 - 5 + offset_x
        py = pos[1] * GRID_SIZE + GRID_SIZE // 2 - 5 + offset_y
        
        pygame.draw.rect(screen, car_color, (px, py, 10, 10))
        if car_data.get('waiting', False):
            pygame.draw.rect(screen, (255, 255, 255), (px, py, 10, 10), 1)

    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Traffic Jam & Two-Sided Road Test")
    font = pygame.font.SysFont("Arial", 18)
    clock = pygame.time.Clock()

    sim = SimulationCore(SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE)
    sim.pin_generation_interval = 999999 

    # Scenario: 
    # Two houses on opposite ends of a long road.
    # House 1 at (2, 5), SC 1 at (15, 5) - RED
    # House 2 at (15, 5) [actually SC 2], SC 2 at (2, 5) [actually House 2] - BLUE
    
    sim.add_house((2, 5), color="red", car_limit=5)
    sim.add_shopping_center((15, 5), color="red")
    
    sim.add_house((15, 6), color="blue", car_limit=5)
    sim.add_shopping_center((2, 6), color="blue")

    # Add road for RED: (2,5) <-> (15,5)
    for x in range(2, 15):
        sim.road_network.add_road((x, 5), (x + 1, 5))
        sim.road_network.add_road((x + 1, 5), (x, 5))

    # Add road for BLUE: (2,6) <-> (15,6)
    for x in range(2, 15):
        sim.road_network.add_road((x, 6), (x + 1, 6))
        sim.road_network.add_road((x + 1, 6), (x, 6))
        
    # Connector roads to make them cross if we wanted, but let's first test simple jamming
    # Let's make them share the SAME ROAD segment
    # (5, 5) <-> (10, 5) used by both?
    # Actually let's just use one road for both colors.
    
    # Scenario: Crossroad Jam
    sim.road_network.reset()
    # Horizontal road at y=5
    for x in range(1, 18):
        sim.road_network.add_road((x, 5), (x + 1, 5))
        sim.road_network.add_road((x + 1, 5), (x, 5))
    
    # Vertical road at x=8
    for y in range(1, 10):
        sim.road_network.add_road((8, y), (8, y + 1))
        sim.road_network.add_road((8, y + 1), (8, y))

    sim.houses = []
    sim.shopping_centers = []
    sim.traffic_manager.houses = []
    sim.traffic_manager.shopping_centers = []
    
    # Red: Left to Right
    sim.add_house((2, 5), color="red", car_limit=10)
    sim.add_shopping_center((15, 5), color="red")
    
    # Blue: Right to Left
    sim.add_house((16, 5), color="blue", car_limit=10)
    sim.add_shopping_center((1, 5), color="blue")

    # Green: Top to Bottom
    sim.add_house((8, 2), color="green", car_limit=10)
    sim.add_shopping_center((8, 9), color="green")

    # Yellow: Bottom to Top
    sim.add_house((8, 8), color="yellow", car_limit=10)
    sim.add_shopping_center((8, 1), color="yellow")

    running = True
    step_count = 0
    total_generated = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if step_count == 2:
            # Generate many pins to trigger multiple cars
            for sc in sim.shopping_centers:
                for _ in range(8):
                    sc.generate_pin()
                    total_generated += 1
            print(f"Total pins generated manually: {total_generated}")

        world_state, _, _, _ = sim.step(None)
        render(sim, screen, font, world_state)
        step_count += 1
        clock.tick(FPS)
        
        # Monitor progress
        if step_count % 20 == 0:
            total_pins = sum(len(sc.pins) for sc in sim.shopping_centers)
            total_fulfilled = sum(sc.fulfilled_counter for sc in sim.shopping_centers)
            print(f"Step {step_count}: Pending Pins={total_pins}, Fulfilled={total_fulfilled}")

        if step_count > 150: # Increased to 400 steps
            running = False

    final_fulfilled = sum(sc.fulfilled_counter for sc in sim.shopping_centers)
    print(f"Final Report: Generated={total_generated}, Fulfilled={final_fulfilled}")
    if final_fulfilled > total_generated:
        print("WARNING: More pins fulfilled than manually generated! Checking for automatic generation...")
    
    pygame.quit()

if __name__ == "__main__":
    main()

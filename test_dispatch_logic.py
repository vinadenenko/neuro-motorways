import pygame
import sys
import time
from simulation_core_manager import SimulationCore

# Constants
GRID_SIZE = 40
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 5

COLOR_MAP = {
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 255, 0),
    "gray": (100, 100, 100),
    "bg": (230, 230, 220),
    "white": (255, 255, 255),
    "black": (0, 0, 0)
}

def render(sim, screen, font):
    screen.fill(COLOR_MAP["bg"])
    
    # Draw roads
    for road in sim.road_network.roads:
        start, end = road
        start_px = (start[0] * GRID_SIZE + GRID_SIZE // 2, start[1] * GRID_SIZE + GRID_SIZE // 2)
        end_px = (end[0] * GRID_SIZE + GRID_SIZE // 2, end[1] * GRID_SIZE + GRID_SIZE // 2)
        pygame.draw.line(screen, COLOR_MAP["gray"], start_px, end_px, 6)

    # Draw house
    for house in sim.houses:
        rect = pygame.Rect(house.location[0] * GRID_SIZE + 4, house.location[1] * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)
        pygame.draw.rect(screen, COLOR_MAP[house.color], rect)
        txt = font.render(str(len(house.idle_cars)), True, COLOR_MAP["white"])
        screen.blit(txt, (house.location[0] * GRID_SIZE + 12, house.location[1] * GRID_SIZE + 8))

    # Draw shopping center
    for sc in sim.shopping_centers:
        rect = pygame.Rect(sc.location[0] * GRID_SIZE, sc.location[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, COLOR_MAP[sc.color], rect)
        # Pins
        for i in range(len(sc.pins)):
            px = sc.location[0] * GRID_SIZE + (i % 3) * 10 + 5
            py = sc.location[1] * GRID_SIZE + (i // 3) * 10 + 5
            pygame.draw.circle(screen, COLOR_MAP["white"], (px, py), 4)
        
        # Dispatch info
        dispatch_txt = font.render(f"Dispatched: {sc.dispatched_pins_count}", True, COLOR_MAP["black"])
        screen.blit(dispatch_txt, (sc.location[0] * GRID_SIZE, (sc.location[1] + 1) * GRID_SIZE))

    # Draw cars
    for car_data in sim.traffic_manager.get_cars():
        pos = car_data['position']
        px = pos[0] * GRID_SIZE + GRID_SIZE // 4
        py = pos[1] * GRID_SIZE + GRID_SIZE // 4
        pygame.draw.rect(screen, (0, 200, 0), (px, py, GRID_SIZE // 2, GRID_SIZE // 2))

    # UI
    info_txt = font.render("Scenario: 1 Pin generated, House has 2 cars. Only 1 should be sent.", True, COLOR_MAP["black"])
    screen.blit(info_txt, (20, 20))
    
    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dispatch Logic Test")
    font = pygame.font.SysFont("Arial", 18)
    clock = pygame.time.Clock()

    sim = SimulationCore(SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE)
    # Fully disable automatic pin generation
    sim.pin_generation_interval = 999999 
    sim.time_elapsed = 1.0 # Start from 1 to avoid the % 0 check if it triggers at 0

    # Setup: House at (2, 5), SC at (10, 5)
    house_pos = (2, 5)
    sc_pos = (10, 5)
    sim.add_house(house_pos, color="red", car_limit=3)
    sim.add_shopping_center(sc_pos, color="red")

    # Add road
    for x in range(house_pos[0], sc_pos[0]):
        sim.road_network.add_road((x, 5), (x + 1, 5))
        sim.road_network.add_road((x + 1, 5), (x, 5))

    running = True
    pins_generated_manually = False
    step_count = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Generate 2 pins at step 10
        if step_count == 10 and not pins_generated_manually:
            sim.shopping_centers[0].generate_pin()
            sim.shopping_centers[0].generate_pin()
            pins_generated_manually = True
            print("2 Pins generated manually!")

        sim.step(None)
        render(sim, screen, font)
        
        # Check logic: at step 11, dispatched_pins_count should be 2, and idle_cars should be 1 (out of 3)
        if step_count == 11:
            sc = sim.shopping_centers[0]
            house = sim.houses[0]
            print(f"Step 11: Pins={len(sc.pins)}, Dispatched={sc.dispatched_pins_count}, Idle Cars={len(house.idle_cars)}")
            if sc.dispatched_pins_count != 2:
                print(f"FAILURE: Expected 2 dispatched pins, got {sc.dispatched_pins_count}")
            elif len(house.idle_cars) != 1:
                 print(f"FAILURE: Expected 1 idle car, got {len(house.idle_cars)}")
            else:
                print("SUCCESS: Exactly 2 cars dispatched for 2 pins.")

        step_count += 1
        clock.tick(FPS)
        if step_count > 100: # End test after some time
             running = False

    pygame.quit()

if __name__ == "__main__":
    main()

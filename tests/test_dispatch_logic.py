import pygame
import sys
import time
from nm_core.simulation.core import SimulationCore
from nm_common.constants import GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_MAP, FPS
from nm_common.runner import SimulationRunner

def render(sim, screen, world_state):
    font = pygame.font.SysFont("Arial", 18)
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
        for i in range(len(sc.pins)):
            px = sc.location[0] * GRID_SIZE + (i % 3) * 10 + 5
            py = sc.location[1] * GRID_SIZE + (i // 3) * 10 + 5
            pygame.draw.circle(screen, COLOR_MAP["white"], (px, py), 4)
        
        dispatch_txt = font.render(f"Dispatched: {sc.dispatched_pins_count}", True, COLOR_MAP["black"])
        screen.blit(dispatch_txt, (sc.location[0] * GRID_SIZE, (sc.location[1] + 1) * GRID_SIZE))

    # Draw cars
    for car_data in world_state.cars:
        pos = car_data['position']
        px = pos[0] * GRID_SIZE + GRID_SIZE // 4
        py = pos[1] * GRID_SIZE + GRID_SIZE // 4
        pygame.draw.rect(screen, (0, 200, 0), (px, py, GRID_SIZE // 2, GRID_SIZE // 2))

    info_txt = font.render("Scenario: 2 Pins generated, House has 3 cars. Only 2 should be sent.", True, COLOR_MAP["black"])
    screen.blit(info_txt, (20, 20))

def main():
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dispatch Logic Test")

    sim = SimulationCore(SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE)
    sim.pin_generation_interval = 0
    sim.time_elapsed = 1.0

    house_pos = (2, 5)
    sc_pos = (10, 5)
    sim.add_house(house_pos, color="red", car_limit=3)
    sim.add_shopping_center(sc_pos, color="red")

    for x in range(house_pos[0], sc_pos[0]):
        sim.road_network.add_road((x, 5), (x + 1, 5))
        sim.road_network.add_road((x + 1, 5), (x, 5))

    step_count = 0
    pins_generated_manually = False

    def update_logic(sim, dt):
        nonlocal step_count, pins_generated_manually
        if step_count == 10 and not pins_generated_manually:
            sim.shopping_centers[0].generate_pin()
            sim.shopping_centers[0].generate_pin()
            pins_generated_manually = True
            print("2 Pins generated manually!")

        if step_count == 11:
            sc = sim.shopping_centers[0]
            house = sim.houses[0]
            print(f"Step 11: Pins={len(sc.pins)}, Dispatched={sc.dispatched_pins_count}, Idle Cars={len(house.idle_cars)}")
            if sc.dispatched_pins_count == 2 and len(house.idle_cars) == 1:
                print("SUCCESS: Exactly 2 cars dispatched for 2 pins.")
            else:
                 print("FAILURE in dispatch logic verification.")

        step_count += 1

    runner = SimulationRunner(sim, fps=FPS)
    runner.run(render_callback=render, update_callback=update_logic, max_steps=100)
    pygame.quit()

if __name__ == "__main__":
    main()

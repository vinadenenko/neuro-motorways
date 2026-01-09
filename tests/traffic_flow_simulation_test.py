from simulation_core_manager import SimulationCore


def test_traffic_flow():
    # Step 1: Initialize the simulation core
    width, height = 10, 10
    sim = SimulationCore(width, height)

    # Step 2: Add a simple road network
    # Example: A straight horizontal road from (0, 5) to (9, 5)
    for x in range(9):
        sim.road_network.add_road((x, 5), (x + 1, 5))

    # Step 3: Spawn two cars with different destinations
    car_1_start = (0, 5)
    car_1_dest = (9, 5)
    car_2_start = (3, 5)
    car_2_dest = (9, 5)

    sim.spawn_car(car_1_start, car_1_dest)  # Add a first car
    sim.spawn_car(car_2_start, car_2_dest)  # Add a second car

    # Step 4: Run the simulation for a few steps and print results
    print("Initial Traffic State")
    print("--------------------------------")
    print(f"Initial Cars: {sim.traffic_manager.get_cars()}")

    # Simulate the game for 10 steps
    for step in range(10):

        sim.step(None)  # No specific Action is passed right now
        print(f"\nAfter Step {step + 1}")
        print("--------------------------------")
        cars = sim.traffic_manager.get_cars()
        for car in cars:
            print(f"Car ID: {car['car_id']} | Position: {car['position']} | Active: {car['active']}")

    # Check if cars reached their destinations
    print("\nFinal Traffic State")
    print("--------------------------------")
    print(f"Final Cars: {sim.traffic_manager.get_cars()}")


# Run the test
if __name__ == "__main__":
    test_traffic_flow()
### Robust FPS Decoupling System

To achieve a professional and robust 60 FPS experience while keeping the game logic at its original speed (15 logic ticks/sec), I have implemented a **Time-Accumulator Decoupling** architecture. 

This approach is standard in high-end game engines (like Unity or Unreal) to separate the **Rendering Frequency** from the **Simulation Frequency**.

#### 1. Why Decoupling is Necessary
If we simply ran the simulation logic once per frame at 60 FPS, the game would run **4x faster** (cars would move 4 tiles per second instead of 1, etc.). By decoupling them:
- **Visualizer**: Runs at 60 FPS (or higher) for smooth UI and animations.
- **Simulation Core**: Runs at a fixed **15 Hz** (`SIMULATION_TICK_RATE = 15`). This ensures deterministic behavior for Reinforcement Learning (RL) and consistent gameplay difficulty.

#### 2. The `tick_accumulator` Mechanism
The "Source of Truth" for time is the `delta_time (dt)` provided by the Pygame clock. Here is how the `SimulationCore.step` method handles it:

1. **Time Debt**: The simulation maintains an `accumulator` (a "time debt"). 
2. **Accumulation**: Every frame, the `dt` (e.g., 0.016s for 60 FPS) is added to the accumulator.
3. **Consumption**: The simulation checks if the debt is greater than the `tick_duration` (1/15s $\approx$ 0.066s).
4. **Execution**: 
   - If the debt is met, it executes exactly **one logic tick** (`_logic_tick()`) and subtracts the duration from the debt.
   - If the computer lags (e.g., a massive spike), the `while` loop can run multiple logic ticks in one frame to "catch up."
   - **Robustness (Spiral of Death Protection)**: I added a cap (`max_ticks_per_frame = 5`). If the lag is too extreme, the game will drop logic ticks rather than freezing the entire system trying to catch up.

#### 3. Continuous vs. Discrete Time
I categorized game mechanics into two types for better precision:
- **Discrete Mechanics (15 Hz)**: Car movement, pathfinding, and pin generation happen in `_logic_tick`. These must be discrete to remain deterministic.
- **Continuous Mechanics (Real-time)**: **Failure Timers** on shopping centers are updated using the raw `dt` every frame. This means the 60-second failure limit is extremely precise and doesn't "stutter" with the logic ticks.

#### 4. Growth System Adaptation
The `GrowthManager` also uses a `time_accumulator`. Instead of counting "100 steps," it now counts "13.0 seconds." This makes the game's progression feel identical whether you are running at 30 FPS, 60 FPS, or 144 FPS.

### Summary of Robustness
- **Consistency**: 1 second of real-world time always equals 15 logic steps.
- **Determinism**: The core logic remains tick-based, which is essential for future AI training.
- **Safety**: The "catch-up" cap prevents the game from crashing during system lag.
- **Smoothness**: The visualizer is free to render as often as the monitor allows without affecting the simulation speed.
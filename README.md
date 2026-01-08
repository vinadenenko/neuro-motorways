# Mini Motorways AI Project

A hybrid **game + AI research project** aimed at building a playable Mini Motorways-style game while training neural networks to achieve and exceed human high scores using reinforcement learning.

The project supports **two parallel environments**:

1. **Game Clone Environment** — a fully playable Mini Motorways-like game built with **pygame-ce**.
2. **Computer Vision Environment** — an adapter that allows the same AI agent to play the original Mini Motorways game using screen capture and input automation.

Both environments connect to the same AI core through a **bridge / adapter interface**.

---

## Project Goals

- Build a **playable Mini Motorways-style game** for humans.
- Design a **deterministic simulation core** suitable for reinforcement learning.
- Train neural network agents to achieve high scores.
- Support **two interchangeable environments**:
  - Clone environment (pygame-ce)
  - Vision environment (real game via CV)
- Use a single AI core with no knowledge of which environment it controls.
- Allow future extensions:
  - Multiplayer
  - Meta-progression
  - Replay system
  - Competitive benchmarking

---

## Core Design Principle

> **The simulation core is authoritative.  
Rendering, input, AI, and networking are all clients of it.**

This ensures:

- No duplicated logic
- Deterministic training
- Identical behavior for humans and AI
- Clean multiplayer and replay support

---

## Architecture Overview

The AI interacts only with the **Simulation Core** through an abstract interface.

---

## Dual Environment Strategy

### 1. Clone Environment

- Built with **pygame-ce**
- Fully playable by humans
- Deterministic simulation
- Headless mode for RL training
- High-performance stepping

### 2. Vision Environment

- Uses screen capture + computer vision
- Detects game objects from the real Mini Motorways game
- Converts observations into the same `WorldState`
- Converts AI actions into mouse/keyboard input

Both environments implement the same interface.

---

## AI Integration

- **PyTorch** for neural networks
- **PPO / custom RL algorithms**
- **Heuristic baseline agents**
- **Curriculum training**
- **Replay and evaluation tools**

The AI never knows whether it is playing:

- the **clone game**
- or the **real Mini Motorways**

---

## Game Mechanics To Be Implemented

- **Grid-based road network**
- **Houses and buildings with color matching**
- **Traffic flow and congestion**
- **Pins and failure timers**
- **Weekly upgrade choice system**
- **Resource management**
- **Deterministic tick-based simulation**

---

## Event-Driven Simulation

The simulation emits structured events:

- **Pin increased / decreased**
- **Upgrade choice required**
- **Upgrade applied**
- **Week passed**
- **Game over**

UI, AI, and networking consume these events.

---

## Technology Stack

| Area                | Choice               |
|---------------------|----------------------|
| Language            | Python               |
| Rendering           | pygame-ce            |
| AI / ML             | PyTorch              |
| RL                  | PPO / custom         |
| CV                  | OpenCV + PyTorch     |
| Input Automation    | PyAutoGUI / pynput   |
| Networking (future) | asyncio + websockets |

---

## Current Progress

- **Simulation Core**:
  - The foundation for grid-based roads is in progress, where a road network can connect grid cells.
  - Visual rendering of roads and a grid system has been implemented, using `pygame-ce` for visualization.
  - Basic entities like **houses (garages)** and **shopping centers** with pins are being established.
  - Cars have been introduced and can move between entities (e.g., houses and shopping centers) in a simplistic manner.
  - Designed a tick-based update loop, where both AI and human players interact within a deterministic simulation.

- **Visual Representation**:
  - A **grid rendering system** was developed to visualize roads, houses, shopping centers, and cars.
  - The simulation has a simple step-forward system to animate cars traveling on roads.

- **Upcoming Work**:
  - Finalize pin-generation logic for shopping centers and implement stateful car behavior (idle, driving, returning).
  - Introduce proper collision-free car pathfinding and alignment with reinforcement learning data requirements.

---

## Simulation Core Milestone

The **Simulation Core** is the foundation of both environments (clone and vision) and aims to be fully deterministic for reinforcement learning integration. The following features have been designed, implemented, or are planned:

### **Features Designed / Implemented**
- **Grid-Based Roads**:
  - Roads consist of connected grid cells, representing paths for cars to navigate.
  - Grid rendering visually displays roads for debugging and gameplay.

- **Houses (Garages)**:
  - Houses act as car spawners, and each house starts with a fixed number of cars (2 by default).
  - Cars are ready to respond when a demand (pin) is raised at a nearby shopping center.

- **Shopping Centers**:
  - Shopping centers can generate pins, representing customer demands, and cars need to fulfill these demands.

- **Pins and Events**:
  - Pins increase at shopping centers periodically based on elapsed simulation time.
  - Event-based simulation logic will dispatch updates such as "pin increased" or "demand fulfilled" for external systems (AI, UI, etc.).

- **Car Movement**:
  - Cars navigate from a house to a shopping center when a pin is generated.
  - Cars use a simple stepping mechanism to traverse a path and return after fulfilling the demand.

### **Planned Features**
- **Traffic Flow and Congestion**:
  - Cars will account for congestion and adapt routing decisions.

- **Upgradeable Features**:
  - Weekly upgrades (roads, bridges, tunnels, etc.) will dynamically enhance simulation complexity.

- **Resource Management**:
  - Cars and roads act as limited resources that must be optimally managed by players or the AI.

---

## Development Roadmap

**Phase 1**

- Simulation core
- Minimal playable clone

**Phase 2**

- UI polish and gameplay parity

**Phase 3**

- Heuristic AI agent

**Phase 4**

- RL training integration

**Phase 5**

- Vision environment

**Phase 6**

- Meta progression and multiplayer experiments

---

## Final Objective

Train a neural network agent capable of achieving and exceeding high scores in **Mini Motorways** using both:

1. A cloned environment
2. The original game via computer vision

<details>
<summary>The core idea for implementation (click to expand/collapse):</summary>

+-----------------------------+
|        Agent Core           |
|  (Policy / Training / RL)   |
+-------------▲---------------+
              |
        Abstract Interface
              |
+-------------▼---------------+
|   World Adapter (Bridge)    |
|  (API or CV-based)          |
+-------------▲---------------+
              |
        Concrete World
              |
+-------------▼---------------+
|  Game Implementation        |
|  (Clone or Real Game)       |
+-----------------------------+

</details>

### Key Design Principles

- **One Agent Core**
- **Multiple World Adapters**
- **Zero duplication of learning logic**

---

### The Most Important Rule

- The Agent must **never know** how the world is implemented.
- The Agent only talks to **interfaces**.
- Actions are **intent-based**, not UI-based.

---

### Adapter Responsibilities

- **CV adapter**: Translates intent → mouse inputs.
- **Clone adapter**: Translates intent → internal calls.



# NeuroMotorways Ecosystem Naming Convention

NeuroMotorways is an ecosystem of interconnected projects focused on simulation, game design, and neural agent research inspired by Mini Motorways.

All repositories follow a unified naming convention:

neuro-motorways-component

This ensures consistency, discoverability, and scalability across the ecosystem.

## Core Repositories

| Repository | Purpose |
|---------|---------|
| neuro-motorways-core | Deterministic simulation engine (headless, no rendering) |
| neuro-motorways-clone | Playable Pygame-ce game clone |
| neuro-motorways-env | Gym-style environment bridge for RL |
| neuro-motorways-rl | Reinforcement learning agents and training |
| neuro-motorways-cv | Computer-vision agent for original game |
| neuro-motorways-tools | Debugging, replay, and analytics tools |
| neuro-motorways-meta | Multiplayer and meta-progression systems |

## Code Namespace Convention

Python modules use:

Example:

```python
from nm_core.simulation import World
from nm_env.gym_env import NeuroMotorwaysEnv


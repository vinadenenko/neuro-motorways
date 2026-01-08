from abc import ABC, abstractmethod
from typing import Tuple, Dict, List

from action_parameters_handler import Action
from world_state_initialization import WorldState


class Environment(ABC):
    @abstractmethod
    def reset(self) -> "WorldState":
        """
        Resets the environment to its initial state.

        Returns:
            WorldState object representing the initial state.
        """
        pass

    @abstractmethod
    def step(self, action: "Action") -> Tuple["WorldState", float, bool, Dict]:
        """
        Executes a given action in the environment.

        Args:
            action: The action to perform.

        Returns:
            A tuple containing:
                - WorldState: The new state of the environment.
                - reward: A float representing the reward for the action.
                - done: A bool indicating the end of the episode (if True, game over).
                - info: A dictionary containing additional metadata.
        """
        pass

    @abstractmethod
    def render(self):
        """Optional: Renders the current state (useful for debugging or human play)."""
        pass
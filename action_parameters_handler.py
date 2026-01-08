from typing import Dict


class Action:
    def __init__(self, action_type: str, params: Dict):
        """
        Args:
            action_type: A string representing the type of action (e.g., 'add_road', 'remove_road').
            params: A dictionary of parameters for performing the action.
        """
        self.action_type = action_type
        self.params = params
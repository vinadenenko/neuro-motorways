# entities/shopping_center.py
from typing import Tuple, List

class ShoppingCenter:
    def __init__(self, center_id: str, location: Tuple[int, int]):
        """
        Initialize a shopping center object.

        Args:
            center_id: Unique identifier for this shopping center.
            location: (x, y) location of the center on the grid.
        """
        self.center_id = center_id
        self.location = location
        self.pins: List[int] = []  # List of active pins
        self.pin_counter = 0

    def generate_pin(self) -> int:
        """
        Generate a new service request (pin).
        
        Returns:
            int: The ID of the generated pin.
        """
        self.pin_counter += 1
        self.pins.append(self.pin_counter)
        print(f"ShoppingCenter {self.center_id} generated a pin! Current pins: {self.pins}")
        return self.pin_counter

    def fulfill_pin(self) -> bool:
        """
        Fulfill a pin request when a car arrives.
        
        Returns:
            bool: True if a pin was fulfilled, False if there were no pins.
        """
        if self.pins:
            fulfilled_pin = self.pins.pop(0)
            print(f"Pin {fulfilled_pin} fulfilled at ShoppingCenter {self.center_id}!")
            return True
        return False
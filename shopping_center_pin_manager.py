# entities/shopping_center.py
from typing import Tuple, List

class ShoppingCenter:
    def __init__(self, center_id: str, location: Tuple[int, int], color: str = "red"):
        """
        Initialize a shopping center object.

        Args:
            center_id: Unique identifier for this shopping center.
            location: (x, y) location of the center on the grid.
            color: Color of the shopping center and its pins.
        """
        self.center_id = center_id
        self.location = location
        self.color = color
        self.pins: List[int] = []  # List of active pins
        self.pin_counter = 0
        self.fulfilled_counter = 0
        self.failure_timer = 0.0
        self.max_pins = 10
        self.is_failing = False

    def generate_pin(self) -> int:
        """
        Generate a new service request (pin).
        
        Returns:
            int: The ID of the generated pin.
        """
        self.pin_counter += 1
        self.pins.append(self.pin_counter)
        if len(self.pins) > self.max_pins // 2:
            self.is_failing = True
        print(f"ShoppingCenter {self.center_id} ({self.color}) generated a pin! Current pins: {self.pins}")
        return self.pin_counter

    def fulfill_pin(self) -> bool:
        """
        Fulfill a pin request when a car arrives.
        
        Returns:
            bool: True if a pin was fulfilled, False if there were no pins.
        """
        if self.pins:
            fulfilled_pin = self.pins.pop(0)
            self.fulfilled_counter += 1
            if len(self.pins) <= self.max_pins // 2:
                self.is_failing = False
                self.failure_timer = 0.0
            print(f"Pin {fulfilled_pin} fulfilled at ShoppingCenter {self.center_id}!")
            return True
        return False

    def update_failure_timer(self, dt: float) -> bool:
        """
        Updates the failure timer if the center is failing.
        Returns True if the game should be over.
        """
        if self.is_failing:
            self.failure_timer += dt
            if self.failure_timer >= 60.0:  # 60 seconds of failure leads to game over
                return True
        return False
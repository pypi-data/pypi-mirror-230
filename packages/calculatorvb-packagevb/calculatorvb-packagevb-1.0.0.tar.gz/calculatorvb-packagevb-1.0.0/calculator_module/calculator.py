class Calculator:
    """A simple calculator class that performs basic math operations and memory manipulation."""

    def __init__(self):
        self.memory = 0

    def add(self, value):
        """Add a number to the current memory value."""
        self.memory += value
        return self.memory

    def subtract(self, value):
        """Subtract a number from the current memory value."""
        self.memory -= value
        return self.memory

    def multiply(self, value):
        """Multiply the current memory value by a number."""
        self.memory *= value
        return self.memory

    def divide(self, value):
        """Divide the current memory value by a number."""
        if value == 0:
            raise ValueError("Cannot divide by zero.")
        self.memory /= value
        return self.memory

    def take_root(self, value):
        """Take the nth root of the current memory value."""
        if value == 0:
            raise ValueError("Cannot take the 0th root.")
        self.memory **= (1 / value)
        return self.memory

    def reset_memory(self):
        """Reset the calculator's memory to 0."""
        self.memory = 0

            
        
    
class Calculator:
    def __init__(self):
        """Initialise the calculator with memory set to 0."""
        self.memory = 0

    def add(self, x):
        """Add a number to the memory."""
        self.memory += x

    def subtract(self, x):
        """Subtract a number from the memory."""
        self.memory -= x

    def multiply(self, x):
        """Multiply the memory by a number"""
        self.memory *= x

    def divide(self, x):
        """Divide the memory by a number, unless that number is 0"""

        if x != 0:
            self.memory /= x
        else:
            raise ZeroDivisionError("Cannot divide by zero")

    def take_root(self, n: int) -> None:
        """Take the x-th root of the memory."""
        if self.memory >= 0:
            self.memory = self.memory ** (1 / n)
        elif n % 2 == 1:
            self.memory = -(abs(self.memory) ** (1 / n))
        else:
            raise ValueError("Cannot take an even root of a negative number")
            

    def reset(self):
        """Reset the memory to zero"""
        self.memory = 0

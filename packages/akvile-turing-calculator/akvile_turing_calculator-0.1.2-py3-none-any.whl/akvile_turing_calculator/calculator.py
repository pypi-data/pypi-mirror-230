class Calculator:
    """
    A basic calculator class that provides arithmetic operations and memory management.

    Attributes:
        memory (float): Stores the current value or result of the calculator.
    """

    def __init__(self) -> None:
        """Initializes a new instance of the Calculator with memory set to zero."""
        self.memory: float = 0.0

    def check_input_type(self, value: int | float) -> None:
        """
        Validates if the provided value is of type int or float, excluding boolean values.

        Args:
            value (int | float): The value to be checked.

        Raises:
            TypeError: If the value is not of type int or float, or if it's a boolean.
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError("Value must be int or float.")

    def add(self, value: int | float) -> float:
        """
        Adds the provided value to the calculator's memory.

        Args:
            value (int | float): The number to be added to the calculator's memory.

        Returns:
            float: The updated value of the calculator's memory after addition.

        Raises:
            TypeError: If the provided value is neither an integer nor a float.
        """
        self.check_input_type(value)
        self.memory += value
        return self.memory

    def subtract(self, value: int | float) -> float:
        """
        Subtracts the provided value from the calculator's memory.

        Args:
            value (int | float): The number to be subtracted from the calculator's memory.

        Returns:
            float: The updated value of the calculator's memory after subtraction.

        Raises:
            TypeError: If the provided value is neither an integer nor a float.
        """
        self.check_input_type(value)
        self.memory -= value
        return self.memory

    def multiply(self, value: int | float) -> float:
        """
        Multiplies the calculator's memory by the provided value.

        Args:
            value (int | float): The number by which the calculator's memory is multiplied.

        Returns:
            float: The updated value of the calculator's memory after multiplication.

        Raises:
            TypeError: If the provided value is neither an integer nor a float.
        """
        self.check_input_type(value)
        self.memory *= value
        return self.memory

    def divide(self, value: int | float) -> float:
        """
        Divides the calculator's memory by the provided value.

        Args:
            value (int | float): The number by which the calculator's memory is divided by.

        Returns:
            float: The updated value of the calculator's memory after division.

        Raises:
            TypeError: If the provided value is neither an integer nor a float.
            ZeroDivisionError: If the provided value is 0.
        """
        self.check_input_type(value)
        self.memory /= value
        return self.memory

    def root(self, n: int | float) -> float:
        """
        Takes the nth root of the calculator's memory.

        Args:
            n (int | float): The degree of the root to be applied to the calculator's memory.

        Returns:
            float: The updated value of the calculator's memory after taking the nth root.

        Raises:
            TypeError: If the provided value for 'n' is neither an integer nor a float.
            ZeroDivisionError: If the provided value is 0.
        """
        self.check_input_type(n)
        self.memory = self.memory ** (1 / n)
        return self.memory

    def reset(self) -> None:
        """Resets the calculator's memory to zero."""
        self.memory = 0.0

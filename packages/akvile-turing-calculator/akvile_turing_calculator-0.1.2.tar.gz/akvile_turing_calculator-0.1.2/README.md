# Calculator Project

A simple calculator module that provides basic arithmetic operations and memory management.

## Structure

```
.
├── akvile_turing_calculator/
│   ├── __init__.py
│   └── calculator.py
├── tests/
│   ├── __init__.py
│   ├── test_add.py
│   ├── test_divide.py
│   ├── test_multiply.py
│   ├── test_reset.py
│   ├── test_root.py
│   └── test_subtract.py
├── LICENSE
├── README.md
├── requirements.txt
├── pyproject.toml
└── poetry.lock
```

## Features

- Basic arithmetic operations: addition, subtraction, multiplication, division, and nth root.
- Memory management: store and use results from previous calculations.
- Type validation: ensures that the inputs are of appropriate types.

## Installation

### Poetry

To install with poetry use `poetry add akvile-turing-calculator`

### pip

To install with pip use `pip install akvile-turing-calculator`

## Usage

python

```
from akvile_turing_calculator import Calculator

calc = Calculator()
print(calc.add(5))          # Outputs: 5.0
print(calc.subtract(2))     # Outputs: 3.0
print(calc.multiply(4))     # Outputs: 12.0
print(calc.divide(3))       # Outputs: 4.0
print(calc.root(2))         # Outputs: 2.0
calc.reset()                # Resets memory to 0.0
```

## Testing

Tests are located in the `tests/` directory and can be run using `pytest`.

To run all tests use `pytest tests/`.

## Contributing

1. Fork the repository.
2. Create a new branch for your features or fixes.
3. Write tests that cover your changes.
4. Submit a pull request and provide a detailed description of your changes.

## License

This project is licensed under the terms of the [LICENSE](./LICENSE) file.

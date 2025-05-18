
# Modulo Three Calculator using Finite State Machine

This project implements a Finite State Machine (FSM) to calculate the remainder when a binary number is divided by 3.

## Features

- Generic FSM implementation that can be extended for other problems
- Specific ModThreeFSM implementation for modulo three calculation
- Thorough unit tests covering all edge cases
- Clean, object-oriented design with proper separation of concerns

## Requirements

- Python 3.6+

## Installation

No installation required. Just clone the repository and run the files.

## Usage

```python
from mod_three_fsm import ModThreeFSM

fsm = ModThreeFSM()
remainder = fsm.calculate_remainder("1101")  # Returns 1 (13 % 3 = 1)

Testing Command
python -m pytest tests/
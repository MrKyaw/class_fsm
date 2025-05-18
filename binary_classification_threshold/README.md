

# Threshold Selector

## Overview
This project selects the best threshold for a binary classification model such that the **recall is at least 0.9**. If multiple thresholds meet this condition, the one with **highest precision** is selected.

## Project Structure
- `src/threshold_selector.py`: Core class and logic.
- `tests/test_threshold_selector.py`: Unit tests with edge cases and coverage.
- `requirements.txt`: Dependencies.

## Example Usage
```python
from src.threshold_selector import ThresholdSelector

thresholds = [0.1, 0.2, 0.3]
stats = [
    (90, 5, 10, 5),  # TP, TN, FP, FN
    (80, 10, 8, 12),
    (70, 15, 5, 10)
]

selector = ThresholdSelector(thresholds, stats)
print("Best threshold:", selector.best_threshold())


-------


# Binary Classification Threshold Optimizer

This solution finds the best threshold for a binary classification model that meets a specified recall requirement.

## Features

- Finds the threshold with highest precision where recall >= specified minimum
- Comprehensive input validation
- Detailed logging
- Well-tested with unit tests covering edge cases

## Installation

1. Clone this repository
2. Ensure Python 3.7+ is installed
3. Install required packages:
   ```bash
   pip install pytest

Testing Command
python -m pytest tests/
# Binary Classification Threshold Optimizer

![Python Version](https://img.shields.io/badge/python-3.108%2B-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

An optimized solution for selecting classification thresholds that balance recall and precision requirements.

## Features

- 🔍 **Recall-Precision Optimization**: Finds thresholds meeting minimum recall while maximizing precision
- 🛡️ **Input Validation**: Automatic checking for:
  - Valid metric values (non-negative integers)
  - Threshold uniqueness
  - Proper recall range (0 ≤ min_recall ≤ 1)
- 📊 **Production Ready**:
  - Comprehensive logging (DEBUG to ERROR levels)
  - Type hints throughout codebase
  - Immutable data structures
- ✔️ **Test Coverage**: 100% unit test coverage including edge cases

## Installation

### From Source
```bash
git clone https://github.com/MrKyaw/class_fsm.git   
cd class_fsm/binary_classification_threshold
pip install -e .
```

### Dependencies
pip install pytest numpy  # Only needed for development

### Usage
# Basic Usage
from threshold_optimizer import ThresholdOptimizer, ClassificationMetrics

# Define your metrics
metrics = [
    ClassificationMetrics(
        threshold=0.5,
        true_positives=80,
        false_positives=20,
        true_negatives=60,
        false_negatives=40
    )
]

optimizer = ThresholdOptimizer(metrics)
best_threshold = optimizer.find_optimal(min_recall=0.85)

### Tuple Input Format (Legacy Support)
thresholds = [0.1, 0.2, 0.3]
stats = [
    (90, 5, 10, 5),  # (TP, TN, FP, FN)
    (80, 10, 8, 12),
    (70, 15, 5, 10)
]

optimizer = ThresholdOptimizer.from_tuples(thresholds, stats)
print("Best threshold:", optimizer.find_optimal())

### Project Structure
binary_classification_threshold/
├── src/
│   └── threshold_optimizer/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_threshold_optimizer.py
├── pyproject.toml
└── README.md

### Development
# Running Tests
python -m pytest tests/ -v

# Code Quality
flake8 src/           # Style checking
mypy src/             # Type checking
pylint src/           # Code analysis

# Building Docs
pdoc --html src/threshold_optimizer -o docs/
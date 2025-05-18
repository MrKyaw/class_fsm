

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.threshold_optimizer import ClassificationMetrics, ThresholdOptimizer

class TestClassificationMetrics:
    def test_recall_calculation(self):
        metrics = ClassificationMetrics(
            threshold=0.5,
            true_positives=50,
            false_negatives=50,
            true_negatives=0,
            false_positives=0
        )
        assert metrics.recall == 0.5
        
    def test_precision_calculation(self):
        metrics = ClassificationMetrics(
            threshold=0.5,
            true_positives=50,
            false_positives=50,
            true_negatives=0,
            false_negatives=0
        )
        assert metrics.precision == 0.5

class TestThresholdOptimizer:
    def test_find_best_threshold(self):
        metrics = [
            ClassificationMetrics(0.1, 90, 50, 50, 10),
            ClassificationMetrics(0.2, 85, 60, 40, 15),
            ClassificationMetrics(0.3, 80, 70, 30, 20),
        ]
        optimizer = ThresholdOptimizer(metrics)
        assert optimizer.find_best_threshold(0.8) == 0.3
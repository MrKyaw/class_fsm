
# import unittest
# from src.threshold_selector import ThresholdSelector

# class TestThresholdSelector(unittest.TestCase):
#     def test_best_threshold_found(self):
#         thresholds = [0.1, 0.2, 0.3, 0.4]
#         stats = [
#             (90, 10, 5, 5),   # recall = 0.947
#             (85, 12, 3, 15),  # recall = 0.85
#             (70, 20, 5, 10),  # recall = 0.875
#             (60, 30, 2, 6)    # recall = 0.909
#         ]
#         selector = ThresholdSelector(thresholds, stats)
#         self.assertEqual(selector.best_threshold(), 0.4)

#     def test_no_threshold_meets_recall(self):
#         thresholds = [0.1, 0.2]
#         stats = [
#             (50, 30, 10, 15),  # recall = 0.769
#             (40, 40, 5, 20)    # recall = 0.667
#         ]
#         selector = ThresholdSelector(thresholds, stats)
#         self.assertIsNone(selector.best_threshold())

#     def test_precision_tiebreaker(self):
#         thresholds = [0.1, 0.2]
#         stats = [
#             (90, 10, 10, 5),  # recall = 0.947, precision = 0.9
#             (90, 10, 5, 5)    # recall = 0.947, precision = 0.947
#         ]
#         selector = ThresholdSelector(thresholds, stats)
#         self.assertEqual(selector.best_threshold(), 0.2)

# if __name__ == "__main__":
#     unittest.main()

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
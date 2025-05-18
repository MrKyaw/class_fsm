
"""
Authors : Kyaw Kyaw Oo
Emails : kyaw.tech@gmail.com
Started Date : May 18, 2025
Description : Script to optimize the decision threshold for binary classification tasks, enhancing model precision or recall trade-offs. Includes ROC curve evaluation and threshold tuning utilities.
Released Date : May 18, 2025
CopyRight@2025 by Kyaw Kyaw Oo
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

@dataclass
class ClassificationMetrics:
    """Stores classification metrics at a specific threshold.
    
    Example:
        >>> metrics = ClassificationMetrics(
        ...     threshold=0.5,
        ...     true_positives=80,
        ...     false_positives=20,
        ...     true_negatives=60,
        ...     false_negatives=40
        ... )
        >>> metrics.recall
        0.6666666666666666
        >>> metrics.precision
        0.8
    """
    threshold: float
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int

    @property
    def recall(self) -> float:
        """Calculate recall (true positive rate).
        
        Returns:
            float: Recall value between 0.0 and 1.0. Returns 0.0 if denominator is zero.
        """
        denominator = self.true_positives + self.false_negatives
        result = self.true_positives / denominator if denominator else 0.0
        logger.debug(f"Calculated recall: {result} (TP: {self.true_positives}, FN: {self.false_negatives})")
        return result

    @property
    def precision(self) -> float:
        """Calculate precision.
        
        Returns:
            float: Precision value between 0.0 and 1.0. Returns 0.0 if denominator is zero.
        """
        denominator = self.true_positives + self.false_positives
        result = self.true_positives / denominator if denominator else 0.0
        logger.debug(f"Calculated precision: {result} (TP: {self.true_positives}, FP: {self.false_positives})")
        return result

    @property
    def f1_score(self) -> float:
        """Calculate F1 score (harmonic mean of precision and recall).
        
        Returns:
            float: F1 score between 0.0 and 1.0. Returns 0.0 if precision + recall is zero.
        """
        p = self.precision
        r = self.recall
        result = 2 * (p * r) / (p + r) if (p + r) else 0.0
        logger.debug(f"Calculated F1 score: {result} (Precision: {p}, Recall: {r})")
        return result

class ThresholdOptimizer:
    """Finds the optimal threshold based on classification metrics.
    
    Example:
        >>> metrics = [
        ...     ClassificationMetrics(0.5, 80, 60, 20, 40),
        ...     ClassificationMetrics(0.6, 70, 70, 10, 50)
        ... ]
        >>> optimizer = ThresholdOptimizer(metrics)
        >>> best_threshold = optimizer.find_best_threshold(min_recall=0.6)
    """
    
    def __init__(self, metrics_list: List[ClassificationMetrics]):
        """Initialize the ThresholdOptimizer with a list of classification metrics.
        
        Args:
            metrics_list: List of ClassificationMetrics objects for different thresholds
            
        Raises:
            ValueError: If metrics_list is empty or contains invalid data
            TypeError: If metrics_list contains non-ClassificationMetrics objects
        """
        logger.info("Initializing ThresholdOptimizer with %d metrics", len(metrics_list))
        self.metrics_list = metrics_list
        self._validate_metrics()
        logger.debug("ThresholdOptimizer initialized successfully")
        
    def _validate_metrics(self):
        """Validate input metrics."""
        logger.debug("Validating metrics list")
        
        if not self.metrics_list:
            logger.error("Empty metrics list provided")
            raise ValueError("Metrics list cannot be empty")
            
        seen_thresholds = set()
        for i, metrics in enumerate(self.metrics_list):
            logger.debug("Validating metric %d with threshold %.2f", i, metrics.threshold)
            
            if not isinstance(metrics, ClassificationMetrics):
                logger.error("Invalid metric type at index %d: %s", i, type(metrics))
                raise TypeError("All items must be ClassificationMetrics instances")
            
            if metrics.threshold in seen_thresholds:
                logger.error("Duplicate threshold %.2f found at index %d", metrics.threshold, i)
                raise ValueError(f"Duplicate threshold found: {metrics.threshold}")
            seen_thresholds.add(metrics.threshold)
            
            if any(val < 0 for val in [metrics.true_positives, metrics.true_negatives, 
                                     metrics.false_positives, metrics.false_negatives]):
                logger.error("Negative metric values found at index %d", i)
                raise ValueError("All metric counts must be non-negative")
        
        logger.debug("All metrics validated successfully")

    def find_best_threshold(self, min_recall: float = 0.9) -> Optional[float]:
        """Find threshold with highest precision where recall >= min_recall.
        
        Args:
            min_recall: Minimum recall requirement (default: 0.9)
            
        Returns:
            Optional[float]: Best threshold meeting requirements, or None if none found
            
        Raises:
            ValueError: If min_recall is not between 0 and 1
        """
        logger.info("Finding best threshold with min_recall >= %.2f", min_recall)
        
        if not 0 <= min_recall <= 1:
            logger.error("Invalid min_recall value: %.2f", min_recall)
            raise ValueError("min_recall must be between 0 and 1")
            
        logger.debug("Filtering candidates meeting recall requirement")
        candidates = [m for m in self.metrics_list if m.recall >= min_recall]
        
        if not candidates:
            logger.warning("No thresholds found with recall >= %.2f (from %d total thresholds)", 
                         min_recall, len(self.metrics_list))
            return None
            
        best = max(candidates, key=lambda x: x.precision)
        logger.info("Found optimal threshold: %.2f (Recall: %.3f, Precision: %.3f)", 
                   best.threshold, best.recall, best.precision)
        logger.debug("Candidate thresholds considered: %s", 
                   [(m.threshold, m.recall, m.precision) for m in candidates])
        
        return best.threshold
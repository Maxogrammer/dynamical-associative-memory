"""
Abstract base class for dynamic neural networks.
Defines the interface expected by the solver.
"""

from abc import ABC, abstractmethod
import numpy as np


class DynamicNetwork(ABC):
    """
    Base class for models defined by ODEs (Ordinary Differential Equations).
    """

    def __init__(self, size: int):
        """
        Args:
            size: Flattened size of the input vector (e.g., 1024 for 32x32).
        """
        self.size = size
        self.patterns = None

    @abstractmethod
    def train(self, patterns: list[np.ndarray]) -> None:
        """
        Loads patterns into the network's memory (calculates weights or stores vectors).
        
        Args:
            patterns: List of 1D numpy arrays.
        """
        pass

    @abstractmethod
    def dynamics(self, state: np.ndarray) -> np.ndarray:
        """
        Calculates the time derivative of the state vector (dq/dt).
        
        Args:
            state: Current state vector.
            
        Returns:
            Derivative vector of the same shape.
        """
        pass

    def get_overlap(self, state: np.ndarray, pattern_idx: int) -> float:
        """
        Calculates similarity (overlap) between state and a specific pattern.
        Normalized to [-1, 1] range.
        """
        if self.patterns is None:
            return 0.0
        
        target = self.patterns[pattern_idx]
        dot_product = np.dot(state, target)
        norm_product = np.linalg.norm(state) * np.linalg.norm(target)
        
        if norm_product == 0:
            return 0.0
            
        return dot_product / norm_product
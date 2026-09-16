import numpy as np
from .base import DynamicNetwork

class SynergeticComputer(DynamicNetwork):
    """
    Haken's model with Adjoint Vectors and Non-Linear Attention.
    """

    # Инициализирует Синергетический компьютер
    # Вход: size (размер), lambda_val (внимание), B (насыщение), C (конкуренция)
    # Выход: Новый экземпляр класса
    def __init__(self, size: int, lambda_val: float = 1.0, B: float = 1.0, C: float = 1.0):
        super().__init__(size)
        self.lambda_val = lambda_val
        self.B = B
        self.C = C
        self.prototypes = None
        self.adjoints = None

    # Обучает модель: нормирует прототипы и вычисляет сопряженные векторы
    # Вход: patterns (список векторов)
    # Выход: None
    def train(self, patterns: list[np.ndarray]) -> None:
        self.patterns = patterns
        clean_patterns = []
        for p in patterns:
            norm = np.linalg.norm(p)
            if norm > 0:
                clean_patterns.append(p / norm)
            else:
                clean_patterns.append(p)
        
        V = np.vstack(clean_patterns).T
        self.prototypes = V
        self.adjoints = np.linalg.pinv(V).T

    # Вычисляет производную состояния (динамика параметров порядка)
    # Вход: state (текущий вектор состояния)
    # Выход: Вектор производной dq/dt
    def dynamics(self, state: np.ndarray) -> np.ndarray:
        if self.prototypes is None:
            return np.zeros_like(state)

        overlaps = self.adjoints.T @ state
        positive_overlaps = np.maximum(overlaps, 0.0)
        attention_gain = np.square(positive_overlaps)

        attraction = self.prototypes @ (self.lambda_val * attention_gain)
        
        q_sq = np.dot(state, state)
        saturation = self.B * state * q_sq
        
        sum_overlaps_sq = np.sum(overlaps ** 2)
        competition = self.C * state * sum_overlaps_sq
        
        dqdt = attraction - saturation - competition
        return dqdt

    # Вычисляет проекцию состояния на сопряженный вектор паттерна (Overlap)
    # Вход: state (вектор), pattern_idx (индекс эталона)
    # Выход: Число (амплитуда проекции)
    def get_overlap(self, state: np.ndarray, pattern_idx: int) -> float:
        if self.adjoints is None:
            return 0.0
        return np.dot(self.adjoints[:, pattern_idx], state)
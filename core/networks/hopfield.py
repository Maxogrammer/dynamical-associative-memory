import numpy as np
from .base import DynamicNetwork

class HopfieldNetwork(DynamicNetwork):
    """
    Continuous Hopfield model with Projection Rule.
    """

    # Инициализирует сеть Хопфилда с заданными параметрами
    # Вход: size (размер вектора), decay (затухание), beta (обратная температура)
    # Выход: Новый экземпляр класса
    def __init__(self, size: int, decay: float = 1.0, beta: float = 10.0):
        super().__init__(size)
        self.weights = None
        self.decay = decay
        self.beta = beta
        self.adjoints = None
    
    # Обучает сеть используя правило проекции (псевдоинверсию)
    # Вход: patterns (список векторов)
    # Выход: None (обновляет веса и сопряженные векторы)
    def train(self, patterns: list[np.ndarray]) -> None:
        self.patterns = patterns

        X = np.vstack(patterns).T
        X_pinv = np.linalg.pinv(X)
        self.weights = X @ X_pinv
        np.fill_diagonal(self.weights, 0)

        self.adjoints = X_pinv.T

    # Вычисляет производную состояния по времени (уравнение Хопфилда)
    # Вход: state (текущий вектор состояния)
    # Выход: Вектор производной dq/dt
    def dynamics(self, state: np.ndarray) -> np.ndarray:
        activation = np.tanh(self.beta * state)
        input_current = self.weights @ activation
        dudt = -self.decay * state + input_current
        return dudt

    # Вычисляет проекцию состояния на сопряженный вектор паттерна (Overlap)
    # Вход: state (вектор), pattern_idx (индекс эталона)
    # Выход: Число (амплитуда проекции)
    def get_overlap(self, state: np.ndarray, pattern_idx: int) -> float:
        if self.adjoints is None:
            return 0.0

        return np.dot(self.adjoints[:, pattern_idx], state)
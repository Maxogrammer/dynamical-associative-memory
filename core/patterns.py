"""
Module for generating and manipulating 32x32 binary patterns.
Includes functions to create standard letters (T, L, X) and add noise.
"""

import numpy as np


class PatternGenerator:
    """Generates 32x32 binary patterns (-1, 1)."""
    
    SIZE = 32
    N = SIZE * SIZE

    # Создает пустой холст (заполненный -1)
    # Вход: Нет
    # Выход: Двумерный массив numpy (32x32)
    @staticmethod
    def _create_blank() -> np.ndarray:
        """Creates a blank -1 (black) canvas."""
        return -1 * np.ones((PatternGenerator.SIZE, PatternGenerator.SIZE))

    # Генерирует изображение буквы T
    # Вход: Нет
    # Выход: Одномерный массив numpy (вектор 1024)
    @staticmethod
    def get_letter_t() -> np.ndarray:
        """Generates letter T."""
        img = PatternGenerator._create_blank()
        # Horizontal bar
        img[5:10, 6:26] = 1
        # Vertical bar
        img[5:27, 13:19] = 1
        return img.flatten()

    # Генерирует изображение буквы L
    # Вход: Нет
    # Выход: Одномерный массив numpy (вектор 1024)
    @staticmethod
    def get_letter_l() -> np.ndarray:
        """Generates letter L."""
        img = PatternGenerator._create_blank()
        # Vertical bar
        img[5:27, 6:11] = 1
        # Horizontal bar (bottom)
        img[22:27, 6:26] = 1
        return img.flatten()

    # Генерирует изображение буквы X
    # Вход: Нет
    # Выход: Одномерный массив numpy (вектор 1024)
    @staticmethod
    def get_letter_x() -> np.ndarray:
        """Generates letter X."""
        img = PatternGenerator._create_blank()
        for i in range(5, 27):
            # Main diagonal
            if 5 <= i < 27:
                start_col = i
                img[i, max(0, start_col-2):min(32, start_col+3)] = 1
            # Anti-diagonal
            anti_col = 31 - i
            if 5 <= anti_col < 27:
                img[i, max(0, anti_col-2):min(32, anti_col+3)] = 1
        return img.flatten()

    # Возвращает словарь всех доступных паттернов
    # Вход: Нет
    # Выход: Словарь {строка: вектор}
    @staticmethod
    def get_all_patterns() -> dict[str, np.ndarray]:
        """Returns a dictionary of all available patterns."""
        return {
            "T": PatternGenerator.get_letter_t(),
            "L": PatternGenerator.get_letter_l(),
            "X": PatternGenerator.get_letter_x()
        }

    # Инвертирует случайную часть пикселей в паттерне (шум)
    # Вход: pattern (вектор), noise_level (число от 0.0 до 1.0)
    # Выход: Зашумленный вектор
    @staticmethod
    def apply_noise(pattern: np.ndarray, noise_level: float) -> np.ndarray:
        """
        Inverts a percentage of pixels in the pattern.
        
        Args:
            pattern: 1D numpy array (flattened image).
            noise_level: Float between 0.0 and 1.0 (e.g., 0.3 for 30%).
            
        Returns:
            Noisy copy of the pattern.
        """
        noisy_pattern = pattern.copy()
        n_pixels = len(pattern)
        n_flips = int(n_pixels * noise_level)
        
        # Randomly choose indices to flip
        indices = np.random.choice(n_pixels, n_flips, replace=False)
        noisy_pattern[indices] *= -1
        
        return noisy_pattern
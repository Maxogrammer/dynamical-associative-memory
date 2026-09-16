"""
Helper functions for image transformation and data shaping.
Responsible for converting flat vectors back to 2D images and binarization.
"""

import numpy as np

# Преобразует плоский вектор состояния обратно в 2D матрицу изображения
# Вход: vector (1D массив), size (ширина изображения)
# Выход: 2D массив numpy
def vector_to_image(vector: np.ndarray, size: int = 32) -> np.ndarray:
    """
    Reshapes a 1D state vector back into a 2D image matrix.
    
    Args:
        vector: 1D numpy array (length N).
        size: Width/Height of the image (default 32).
        
    Returns:
        2D numpy array (size x size).
    """

    if vector.size != size * size:
        size = int(np.sqrt(vector.size))
        
    return vector.reshape((size, size))

# Преобразует непрерывные значения состояния в дискретные {-1, 1}
# Вход: state (вектор)
# Выход: Бинарный вектор
def binarize_state(state: np.ndarray) -> np.ndarray:
    """
    Converts continuous state values to discrete binary values {-1, 1}.
    Used for final verification and 'hard' visualization.
    
    Args:
        state: Continuous vector (from Hopfield/Haken).
        
    Returns:
        Binary vector where x in {-1, 1}.
    """

    binary = np.sign(state)
    binary[binary == 0] = 1 
    return binary

# Нормирует значения вектора в диапазон [0, 1] для отображения в matplotlib
# Вход: state (вектор)
# Выход: Нормированный вектор
def normalize_for_display(state: np.ndarray) -> np.ndarray:
    """
    Normalizes continuous values to [0, 1] range for Matplotlib grayscale cmap.
    Logic:
        -1 (Black) -> 0.0
        +1 (White) -> 1.0
        Intermediate values scaled linearly.
    """
    clipped = np.clip(state, -1.5, 1.5)
    
    normalized = (clipped + 1) / 2.0
    return normalized
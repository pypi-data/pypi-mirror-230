from typing import Any, List, Tuple

import numpy as np

import pct_tools_ext


def gradient_descent(
    x: np.ndarray[Any, np.float32],
    step_size: float,
    matrix_filenames: List[str],
    vector_filenames: List[str],
) -> Tuple[np.ndarray[Any, np.float32], float]:
    """Compute gradient descent step.

    Args:
        x: A vector.
        step_size: The step size to be used in the descent.
        matrix_filenames: The filenames of the matrices.
        vector_filenames: The filenames of the vectors.

    Returns:
        A tuple that contains the updated vector and the sum of squared residuals.
    """
    return pct_tools_ext.gradient_descent(x, step_size, matrix_filenames, vector_filenames)

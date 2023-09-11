from typing import Any, List

import numpy as np

import pct_tools_ext


def compute_ATAx(x: np.ndarray[Any, np.float32], filenames: List[str]) -> np.ndarray[Any, np.float32]:
    """Compute the multiplication A.T * A * x.

    This is used in the computation of the largest eigenvalue of the matrix A via the power method.

    Args:
        x: A column vector of shape (m, 1).
        filenames: Names of the files the compressed matrices are stored in.

    Returns:
        The resulting vector of shape (m, 1).
    """
    return pct_tools_ext.compute_ATAx(x, filenames)

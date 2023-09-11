import pct_tools_ext


def subsample_matrix_vector_pair(
    input_path: str, projection: str, output_path: str, subsampling_ratio: float
) -> None:
    """Subsample matrix and b-vector for a given projection.

    Args:
        input_path: The path to the input matrices.
        projection: The projection to subsample.
        output_path: The path to the output matrices.
        subsampling_ratio: The subsampling ratio.
    """
    return pct_tools_ext.subsample_matrix_vector_pair(input_path, projection, output_path, subsampling_ratio)

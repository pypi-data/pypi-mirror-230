import numpy as np

import pct_tools_ext


def compute_matrix_elements(
    x: np.ndarray[np.float32],
    y: np.ndarray[np.float32],
    z: np.ndarray[np.float32],
    x_boundaries: np.ndarray[np.float32],
    y_boundaries: np.ndarray[np.float32],
    z_boundaries: np.ndarray[np.float32],
    img_shape: tuple,
    coordinate_origin: tuple,
    pixel_width: float,
    slice_thickness: float,
) -> np.ndarray[np.float32]:
    """Compute the matrix elements for a given proton trajectory.

    Args:
        x: The x-coordinates of the proton trajectories.
        y: The y-coordinates of the proton trajectories.
        z: The z-coordinates of the proton trajectories.
        x_boundaries: The x-coordinates of the boundaries of the voxels.
        y_boundaries: The y-coordinates of the boundaries of the voxels.
        z_boundaries: The z-coordinates of the boundaries of the voxels.
        img_shape: The shape of the image.
        coordinate_origin: The origin of the image.
        pixel_width: The width of the pixels.
        slice_thickness: The thickness of the slices.

    Returns:
        The 3D array of matrix elements for the given proton trajectory.
    """
    return pct_tools_ext.compute_matrix_elements(
        x,
        y,
        z,
        x_boundaries,
        y_boundaries,
        z_boundaries,
        img_shape,
        coordinate_origin,
        pixel_width,
        slice_thickness,
    )


def compute_matrix_elements_block(
    filename: str,
    x: np.ndarray[np.float32],
    y: np.ndarray[np.float32],
    z: np.ndarray[np.float32],
    x_boundaries: np.ndarray[np.float32],
    y_boundaries: np.ndarray[np.float32],
    z_boundaries: np.ndarray[np.float32],
    img_shape: tuple,
    coordinate_origin: tuple,
    pixel_width: float,
    slice_thickness: float,
) -> None:
    """Compute the matrix elements for a given block of proton trajectories.

    Args:
        filename: The filename of the output file.
        x: The x-coordinates of the proton trajectories.
        y: The y-coordinates of the proton trajectories.
        z: The z-coordinates of the proton trajectories.
        x_boundaries: The x-coordinates of the boundaries of the voxels.
        y_boundaries: The y-coordinates of the boundaries of the voxels.
        z_boundaries: The z-coordinates of the boundaries of the voxels.
        img_shape: The shape of the image.
        coordinate_origin: The origin of the image.
        pixel_width: The width of the pixels.
        slice_thickness: The thickness of the slices.
    """
    return pct_tools_ext.compute_matrix_elements_block(
        filename,
        x,
        y,
        z,
        x_boundaries,
        y_boundaries,
        z_boundaries,
        img_shape,
        coordinate_origin,
        pixel_width,
        slice_thickness,
    )

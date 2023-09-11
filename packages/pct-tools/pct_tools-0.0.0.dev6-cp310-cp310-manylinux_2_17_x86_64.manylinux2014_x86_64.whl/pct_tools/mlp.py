from __future__ import annotations

import numpy as np

import pct_tools_ext


def compute_mlp(
    phantom: str,
    z: np.ndarray[np.float32],
    h_in: float,
    theta_in: float,
    h_out: float,
    theta_out: float,
) -> np.ndarray[np.float32]:
    """Compute the most likley proton trajectory for a set of parameters.

    Args:
        phantom: The phantom to use.
        z: The z-coordinates of the proton trajectories.
        h_in: The transverse position at the entry detector.
        theta_in: The proton direction at the entry detector.
        h_out: The transverse position at the exit detector.
        theta_out: The proton direction at the exit detector.

    Returns:
        Array of most likely transverse positions along trajectory.
    """

    return pct_tools_ext.compute_mlp(phantom, z, h_in, theta_in, h_out, theta_out)

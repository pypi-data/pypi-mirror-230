"""Labels module for RoiLabel."""
from dataclasses import dataclass

import numpy as np


@dataclass
class RoiLabel:
    """Class object for storing needed ROI label attributes."""

    label: str
    index: int
    color: str
    RGB: list
    num_voxels: int = 0
    volume: float = 0.0

    def calc_volume(self, affine: np.ndarray):
        """Calculate volume by num_voxels and affine.

        Args:
            affine: Affine matrix
        """
        self.volume = self.num_voxels * np.abs(np.linalg.det(affine[:3, :3]))

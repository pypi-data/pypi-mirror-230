"""ROI Tools used by the run.py script.

This module represents functionality used by the `run.py` script for readability
and encapsulation.  References to `prior art` are given where appropriate.
Areas for future implementation are noted for ease of prospective implementation.
"""

import logging
import os
import os.path as op
import re
import typing as t
from collections import OrderedDict

import numpy as np
from skimage import draw

rgba_regex = ".*\((?P<R>\d+),\s+?(?P<G>\d+),\s+?(?P<B>\d+),\s+?(?P<A>\d+?\.\d+?)\)"
rgba_regex = re.compile(rgba_regex)

log = logging.getLogger(__name__)


def poly2mask(
    vertex_row_coords: list, vertex_col_coords: list, shape: tuple
) -> np.ndarray:
    """poly2mask converts polygon vertex coordinates into a filled mask.

    Origin of this code was in a scikit-image issue:
        https://github.com/scikit-image/scikit-image/issues/1103#issuecomment-52378754

    Args:
        vertex_row_coords (list): x-coordinates of the vertices
        vertex_col_coords (list): y-coordinates of the vertices
        shape (tuple): The size of the two-dimensional array to fill the
            polygon

    Returns:
        numpy.Array: Two-Dimensional numpy array of boolean values: True
            for within the polygon, False for outside the polygon
    """
    fill_row_coords, fill_col_coords = draw.polygon(
        vertex_row_coords, vertex_col_coords, shape
    )
    mask = np.zeros(shape, dtype=bool)
    mask[fill_row_coords, fill_col_coords] = True
    return mask


def freehand2mask(
    roi_points: list, shape: tuple, axes_flips: tuple, swap_axes: bool = False
) -> np.ndarray:
    """Create a binary mask for the polygon described in roi_points.

    Args:
        roi_points (list): Points representing vertices of the freehand polygon.
        shape (tuple): The size of the two-dimensional array to fill.
        axes_flips (tuple): Indicates if the affine flips each axes, x or y.
        swap_axes (bool, optional): If the x and y axes need to be swapped.
            Defaults to False.

    Returns:
        numpy.Array: Two-Dimensional numpy array of boolean values: True
            for within the polygon, False for outside the polygon
    """
    x_flip, y_flip = axes_flips

    # Initialize x,y coordinates for each polygonal point
    X = []
    Y = []
    if isinstance(roi_points, list):
        for h in roi_points:
            if x_flip:  # orientation_char == "x":
                X.append(shape[0] - h["x"])
            else:
                X.append(h["x"])
            if y_flip:
                Y.append(shape[1] - h["y"])
            else:
                Y.append(h["y"])

    # We loop back to the original point to form a closed polygon
    X.append(X[0])
    Y.append(Y[0])

    # If these coordinates need to be swapped
    if swap_axes:
        Z = X
        X = Y
        Y = Z

    # If this slice already has data (i.e. this label was used in an ROI
    # perpendicular to the current slice) we need to have the logical or
    # of that data and the new data
    return poly2mask(X, Y, shape)


def rectangle2mask(
    start: tuple, end: tuple, shape: tuple, axes_flips: tuple, swap_axes: bool = False
) -> np.ndarray:
    """rectangle2mask converts rectangle coordinates into a two-dimensional mask.

    Args:
        start (tuple): Upper left coordinate of bounding box
        end (tuple): Lower right coordinate of bounding box
        shape (tuple): The size of the two-dimensional array to fill
        axes_flips (tuple): Indicates if the affine flips each axes, x or y.
        swap_axes (bool, optional): If the x and y axes need to be swapped.
            Defaults to False.

    Returns:
        numpy.Array: Two-Dimensional numpy array of boolean values: True
            for within the rectangle, False for outside the rectangle
    """
    x_flip, y_flip = axes_flips

    if x_flip:
        start["x"] = shape[0] - start["x"]
        end["x"] = shape[0] - end["x"]

    if y_flip:
        start["y"] = shape[1] - start["y"]
        end["y"] = shape[1] - end["y"]

    # Convert bounding box into the clockwise-rendered coordinates of a rectangle
    vertex_row_coords = [start["x"], end["x"], end["x"], start["x"], start["x"]]
    vertex_col_coords = [start["y"], start["y"], end["y"], end["y"], start["y"]]
    # If these coordinates need to be swapped
    if swap_axes:
        vertex_swp_coords = vertex_row_coords
        vertex_row_coords = vertex_col_coords
        vertex_col_coords = vertex_swp_coords
    # Pass to poly2mask
    return poly2mask(vertex_row_coords, vertex_col_coords, shape)


def ellipse2mask(
    start: tuple, end: tuple, shape: tuple, axes_flips: tuple, swap_axes: bool = False
) -> np.ndarray:
    """ellipse2mask converts ellipse parameters into a two-dimensional mask.

    Args:
        start (tuple): Upper left coordinate of bounding box
        end (tuple): Lower right coordinate of bounding box
        shape (tuple): The size of the two-dimensional array to fill
        axes_flips (tuple): Indicates if the affine flips each axes, x or y.
        swap_axes (bool, optional): If the x and y axes need to be swapped.
            Defaults to False.

    Returns:
        numpy.Array: Two-Dimensional numpy array of boolean values: True
            for within the ellipse, False for outside the ellipse
    """
    x_flip, y_flip = axes_flips

    if x_flip:
        start["x"] = shape[0] - start["x"]
        end["x"] = shape[0] - end["x"]

    if y_flip:
        start["y"] = shape[1] - start["y"]
        end["y"] = shape[1] - end["y"]

    r_radius, c_radius = ((end["x"] - start["x"]) / 2, (end["y"] - start["y"]) / 2)
    r_center, c_center = (start["x"] + r_radius, start["y"] + c_radius)

    if swap_axes:
        r_radius, c_radius = c_radius, r_radius
        r_center, c_center = c_center, r_center

    fill_row_coords, fill_col_coords = draw.ellipse(
        r_center, c_center, r_radius, c_radius, shape
    )

    mask = np.zeros(shape, dtype=bool)
    mask[fill_row_coords, fill_col_coords] = True

    return mask


def calculate_ROI_volume(
    all_labels: OrderedDict, affine: np.ndarray, task_id: t.Optional[str]
):
    """Calculate the volume of each ROI by task.

    Args:
        all_labels: The dictionary containing ROI info, with task_id as a key
        affine: Affine matrix for the image
        task_id: 24 char BSON id if task related, else None
    """
    task_labels = all_labels[task_id]
    if len(task_labels) > 0:
        for _, label_object in task_labels.items():
            label_object.calc_volume(affine)


def output_ROI_info(
    output_dir: os.PathLike, all_labels: OrderedDict, task_id: t.Optional[str]
):
    """Output the ROI info to a CSV file.

    Args:
        output_dir: Path to output directory
        all_labels: Dictionary of all labels, with task_id as a key
        task_id: 24 char BSON id if task related, else None
    """
    task_labels = all_labels[task_id]

    # Change "None" to "non_task" for filename clarity
    if not task_id:
        task_id = "non_task"

    if len(task_labels) > 0:
        lines = []
        lines.append("label,index,voxels,volume (mm^3)\n")
        for label in task_labels:
            index = task_labels[label].index
            voxels = task_labels[label].num_voxels
            volume = task_labels[label].volume
            lines.append("{},{},{},{}\n".format(label, index, voxels, volume))
        csv_file = open(op.join(output_dir, str(task_id) + "_ROI_info.csv"), "w")
        csv_file.writelines(lines)
        csv_file.close()
    else:
        log.warning("There were no labels to process.")

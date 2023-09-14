"""Generators - Process 3 of 4.

This process actually generates the ROI image.  Due to some functionality that 
this code needs to have, the generator will contain a converter.  Therefore it
is the generators responsibility to not only create the ROI images but also
CALL the converter. 

Responsibilities:
1. based on user input (binary, bitmask, combine, etc), generate images of the ROI
2. generate the "labels" object to track mask size and bit value, etc.
3. generate the name of the new file to be saved
2. call the converter


Full process:
1. Prep
2. Collect
3. Create
4. Convert

"""
import logging
import os
import re
import typing as t
from abc import ABC, abstractmethod
from collections import OrderedDict
from pathlib import Path

import nibabel as nib
import numpy as np
import pydicom

import fw_gear_mask_exporter.roi_tools as roi_tools
from fw_gear_mask_exporter.objects.Labels import RoiLabel
from fw_gear_mask_exporter.workers import Converters, Preppers

log = logging.getLogger(__name__)

rgba_regex = ".*\(\s*(?P<R>\d+),\s*(?P<G>\d+),\s*(?P<B>\d+),\s*(?P<A>\d+?\.\d+?)\)"
rgba_regex = re.compile(rgba_regex)


class BaseCreator(ABC):
    """Generic Creator class

    Raises:
        Exception: Raises if unsupported filetype
    """

    # Type key set on each base class to identify which class to instantiate
    type_ = None

    def __init__(
        self,
        prepper: Preppers.BasePrepper,
        base_file_name: str,
        combine: str,
        bitmask: bool,
        converter: Converters.BaseConverter,
    ):
        """Initializes BaseCreator class object.

        Args:
            prepper: Prepper instance
            base_file_name: Base filename of input file
            combine: Whether to save masks as individual, combined, or both
            bitmask: Whether or not to output binary masks
            converter: Converter instance
        """
        self.orig_dir = prepper.orig_dir
        self.roi_dirs = prepper.roi_dirs
        self.base_file_name = base_file_name
        self.combine = combine
        self.bitmask = bitmask
        self.converter = converter
        self.shape = prepper.shape
        self.prepper = prepper

        self.max_labels = 31
        self.dtype = np.uint8
        self.bits = 8
        self.labels = {}

    def get_task_labels(
        self, roi_info_by_task: dict, task_id: t.Optional[str]
    ) -> OrderedDict:
        """Extracts label-name along with bitmasked index and RGBA
        color code for each distinct label in the ROI collection.

        Args:
            roi_info_by_task: Equivalent to `roi_info[task_id]`
            task_id: 24 char BSON id if connected to task, else None

        Returns:
            OrderedDict: the label object populated with ROI attributes
        """
        # dictionary for labels, index, R, G, B, A
        task_labels = OrderedDict()

        # React OHIF Viewer
        roi_list = [
            individual_roi
            for roi_type_list in roi_info_by_task.values()
            for individual_roi in roi_type_list
        ]

        roi_color = "fbbc05"

        for roi in roi_list:
            if roi.get("location"):
                if roi["location"] not in task_labels.keys():
                    # HAHAHA HAVE FUN WITH THIS PART!
                    # ok ok kidding.  So the way flywheel stores the color of the ROI is by this metadata tag "color"
                    # The value of this key is a string, that resembles the default below, "rgba(<R>, <G>, <B>, <A>)".
                    # This part takes that string, parses out the garbage that should not be there, and extracts the
                    # RGBA values (that is, Red, Green, Blue, Alpha).
                    # I also save it as a hex value because the old code did it that way and I don't want to mess things
                    # up.
                    roi_color = roi.get("color", "rgba(187, 192, 5, 0.2)")
                    rgba = rgba_regex.match(roi_color)
                    rgba = [
                        int(rgba.group("R")),
                        int(rgba.group("G")),
                        int(rgba.group("B")),
                        float(rgba.group("A")),
                    ]

                    task_labels[roi["location"]] = RoiLabel(
                        index=int(2 ** (len(task_labels))),
                        RGB=rgba,
                        color=f"#{hex(rgba[0])[2:]}{hex(rgba[1])[2:]}{hex(rgba[2])[2:]}",
                        label=roi["location"],
                    )

            else:
                log.warning(
                    "There is an ROI without a label. To include this ROI in the "
                    "output, please attach a label."
                )
        self.labels[task_id] = task_labels
        return task_labels

    def set_bit_level(self, labels: dict):
        """Sets self.bits according to label length if not combining and binary masks are okay.

        Args:
            labels: Dictionary with ROI labels
        """
        # If we're not combining and binary masks are ok, we don't need to bitmask, we'll leave at default 8 bit
        if self.combine in ["combined", "both"] or self.bitmask:
            if len(labels) < 8:
                self.dtype = np.uint8
                self.bits = 8
            elif len(labels) < 16:
                self.dtype = np.uint16
                self.bits = 16
            elif len(labels) < 32:
                self.dtype = np.uint32
                self.bits = 32

            elif len(labels) > self.max_labels:
                log.exception(
                    f"Due to the maximum integer length ({self.max_labels+1} bits), we can "
                    f"only keep track of a maximum of {self.max_labels} ROIs with a bitmasked "
                    f"combination. You have {len(labels)} ROIs. Exiting."
                )
                os.sys.exit(1)

    def generate_name(self, task_id: t.Optional[str], label: str) -> str:
        """Create name to be used for output filename

        Args:
            task_id: 24 char BSON id if connected to task, else None
            label: ROI label or "ALL" if generating combined output filename

        Returns:
            str: output_filename for creation of output file
        """
        # If task_id == None, change to non_task for clarity
        if not task_id or task_id == "None":
            task_id = "non_task"

        # Remove non alphanumeric characters from potential filename
        label_out = re.sub("[^0-9a-zA-Z]+", "_", label)

        base = self.base_file_name
        for suffix in [".nii.gz", ".nii", ".dicom.zip", ".zip", ".dicom"]:
            if base.endswith(suffix):
                base = base.removesuffix(suffix)

        base_name = re.sub("[^0-9a-zA-Z]+", "_", base)

        output_filename = f"ROI_{task_id}_{label_out}_{base_name}"

        return output_filename

    @abstractmethod
    def create(self, roi_info_by_task: dict, task_id: t.Optional[str]):
        """Create method handled within type-specific class."""

    @classmethod
    def factory(
        cls,
        type_: str,
        prepper: Preppers.BasePrepper,
        base_file_name: str,
        combine: str,
        bitmask: bool,
        converter: Converters.BaseConverter,
    ):
        """Return an instantiated Creator.

        Args:
            type_: Input file type. Currently only DICOM supported
            prepper: BasePrepper class object
            base_file_name: Base file name of input file
            combine: Whether to save masks as individual, combined, or both
            bitmask: Whether or not to output binary masks
            converter: BaseConverter class object

        Raises:
            NotImplementedError: Raised if file type not supported

        Returns:
            Creator subclass
        """
        for sub in cls.__subclasses__():
            if type_.lower() == sub.type_:
                return sub(
                    prepper,
                    base_file_name,
                    combine,
                    bitmask,
                    converter,
                )
        # If no type_ matches a sub.type_, log exception and exit.
        log.exception("File type %s not supported.", type_)
        os.sys.exit(1)


class DicomCreator(BaseCreator):
    """Creator class for DICOM input files"""

    type_ = "dicom"

    def __init__(
        self,
        prepper: Preppers.BasePrepper,
        base_file_name: str,
        combine: str,
        bitmask: bool,
        converter: Converters.BaseConverter,
    ):
        """Initialize DicomCreator class object

        Args:
            prepper: BasePrepper class object
            base_file_name: Base file name of input file
            combine: Whether to save masks as individual, combined, or both
            bitmask: Whether or not to output binary masks
            converter: BaseConverter class object
        """
        super().__init__(
            prepper,
            base_file_name,
            combine,
            bitmask,
            converter,
        )

        self.dicoms = prepper.dicoms

    def update_dicoms_and_shape(self):
        """Retrieve dicoms and shape from prepper."""
        self.dicoms = self.prepper.get_dicoms()
        self.shape = self.prepper.get_shape()

    def create(self, roi_info_by_task: dict, task_id: t.Optional[str]) -> OrderedDict:
        """Updates dicoms and shape, then retrieves task labels
        and makes data array.

        Args:
            roi_info_by_task: `roi_info[task_id]`
            task_id: 24 char BSON id if connected to task, else None

        Returns:
            OrderedDict: Label object populated with ROI attributes
        """
        self.update_dicoms_and_shape()
        task_labels = self.get_task_labels(roi_info_by_task, task_id)

        self.make_data(task_labels, roi_info_by_task, task_id)
        return task_labels

    def make_data(
        self,
        task_labels: dict,
        roi_info_by_task: dict,
        task_id: t.Optional[str],
    ):
        """From ROI info, labels, and task_id, creates the data
        needed for producing the ROI mask output and sends it
        to the converter for conversion.

        Args:
            task_labels: Collected labels, `{label_name: label_object}`
            roi_info_by_task: Equivalent to `roi_info[task_id]`
            task_id: 24 char BSON id if connected to task, else None
        """
        self.set_bit_level(task_labels)
        len_labels = len(task_labels)

        if len_labels > 0:
            log.info("Found %s ROI labels.", len_labels)
        else:
            log.error("Found NO ROI labels.")
            return

        # Check for whether to save individuals, combined, or both
        if self.combine in ["individual", "both"]:
            for label_name, label_object in task_labels.items():
                log.info("Label: %s", label_name)
                data = self.label2data(label_name, roi_info_by_task)

                label_object.num_voxels = np.count_nonzero(data)
                data = data.astype(self.dtype)
                if self.bitmask:
                    data *= task_labels[label_name].index

                self.save_to_roi_dir(data, task_id)
                output_filename = self.generate_name(task_id, label_name)
                log.info("Saving to %s.", output_filename)
                self.converter.convert(output_filename, task_id)

        if self.combine in ["combined", "both"]:
            data = np.zeros(self.shape, dtype=self.dtype)
            for label in task_labels:
                label_data = self.label2data(label, roi_info_by_task)
                label_data = label_data.astype(self.dtype)
                label_data *= task_labels[label].index
                data += label_data

            self.save_to_roi_dir(data, task_id)
            output_filename = self.generate_name(task_id, "ALL")
            self.converter.convert(output_filename, task_id)

    def label2data(self, label: str, roi_info_by_task: dict) -> np.ndarray:
        """From given label and roi_info, returns fill_roi_dicom_slice data

        Args:
            label: ROI location label
            roi_info_by_task: `roi_info[task_id]`

        Returns:
            np.ndarray: Return values of fill_roi_dicom_slice with given args
        """
        data = np.zeros(self.shape, dtype=bool)
        for roi_type in roi_info_by_task:
            for roi in roi_info_by_task[roi_type]:
                if roi.get("location") == label:
                    data = self.fill_roi_dicom_slice(
                        data,
                        roi["SOPInstanceUID"],
                        roi["handles"],
                        dicoms=self.dicoms,
                        roi_type=roi_type,
                    )

        return data

    def save_to_roi_dir(self, data: np.ndarray, task_id: t.Optional[str]):
        """Using Pydicom, save data as DICOM

        Args:
            data: Array created by label2data()
            task_id: 24 char BSON id if connected to task, else None
        """
        data = data.astype(self.dtype)
        dicom_sops = self.dicoms.bulk_get("SOPInstanceUID")

        for dicom_info in self.dicoms:
            sop = dicom_info.SOPInstanceUID
            slice_idx = dicom_sops.index(sop)
            dicom_file = Path(dicom_info.filepath)
            dicom_data = pydicom.read_file(dicom_file)
            file_name = str(task_id) + "_" + dicom_file.name
            dicom_out = self.roi_dirs[task_id] / file_name

            arr = data[:, :, slice_idx]
            arr = arr.flatten()
            # If the dicom starts as compressed we need to decompress it before saving
            # an array of uncompressed data
            if not dicom_data.is_decompressed:
                try:
                    dicom_data.decompress()
                except Exception as exc:
                    log.warning(
                        "Could not decompress dicom. "
                        "Please use the 'dicom-fixer' gear."
                    )
                    log.exception(exc)
                    raise exc

            dicom_data.BitsAllocated = self.bits
            dicom_data.BitsStored = self.bits
            dicom_data.HighBit = self.bits - 1

            dicom_data.PixelData = arr.tobytes()
            dicom_data.save_as(dicom_out)

    @staticmethod
    def fill_roi_dicom_slice(
        data: np.ndarray,
        sop: str,
        roi_handles,
        roi_type: str = "FreehandRoi",
        dicoms=None,
        reactOHIF: bool = True,
    ) -> np.ndarray:
        """Takes the current state of the full data array, adds the data
        values related to the args passed, and returns updated data.

        Args:
            data: Array passed between this and label2data
            sop: SOPInstanceUID value
            roi_handles: Points or start/end for ROI
            roi_type: Type of ROI annotation. Defaults to "FreehandRoi".
            dicoms: Dicom files. Defaults to None.
            reactOHIF: Defaults to True.

        Returns:
            np.ndarray: Array created by current slice
        """
        dicom_sops = dicoms.bulk_get("SOPInstanceUID")
        slice_idx = dicom_sops.index(sop)

        swap_axes = True
        flips = [False, False]

        orientation_slice = data[:, :, slice_idx]

        if roi_type == "FreehandRoi":
            if reactOHIF:
                roi_points = roi_handles["points"]
            else:
                roi_points = roi_handles

            # If this slice already has data (i.e. this label was used in an ROI
            # perpendicular to the current slice) we need to have the logical or
            # of that data and the new data

            orientation_slice[:, :] = np.logical_or(
                roi_tools.freehand2mask(
                    roi_points, orientation_slice.shape, flips, swap_axes
                ),
                orientation_slice[:, :],
            )

        elif roi_type == "RectangleRoi":
            start = roi_handles["start"]
            end = roi_handles["end"]

            # If this slice already has data (i.e. this label was used in an ROI
            # perpendicular to the current slice) we need to have the logical or
            # of that data and the new data
            orientation_slice[:, :] = np.logical_or(
                roi_tools.rectangle2mask(
                    start, end, orientation_slice.shape, flips, swap_axes
                ),
                orientation_slice[:, :],
            )

        elif roi_type == "EllipticalRoi":
            start = roi_handles["start"]
            end = roi_handles["end"]

            # If this slice already has data (i.e. this label was used in an ROI
            # perpendicular to the current slice) we need to have the logical or
            # of that data and the new data
            orientation_slice[:, :] = np.logical_or(
                roi_tools.ellipse2mask(
                    start, end, orientation_slice.shape, flips, swap_axes
                ),
                orientation_slice[:, :],
            )
        data[:, :, slice_idx] = orientation_slice

        return data


class NiftiCreator(BaseCreator):
    """Creator class for NIfTI input files"""

    type_ = "nifti"

    def __init__(
        self,
        prepper: Preppers.BasePrepper,
        base_file_name: str,
        combine: str,
        bitmask: bool,
        converter: Converters.BaseConverter,
    ):
        """Initialize NiftiCreator class object

        Args:
            prepper: BasePrepper class object
            base_file_name: Base file name of input file
            combine: Whether to save masks as individual, combined, or both
            bitmask: Whether or not to output binary masks
            converter: BaseConverter class object
        """
        super().__init__(
            prepper,
            base_file_name,
            combine,
            bitmask,
            converter,
        )

        self.nifti = prepper.nifti

    def update_nifti_and_shape(self):
        """Retrieve nifti and shape from prepper."""
        self.nifti = self.prepper.get_nifti()
        self.shape = self.prepper.get_shape()

    def create(self, roi_info_by_task: dict, task_id: t.Optional[str]) -> OrderedDict:
        """Updates nifti and shape, then retrieves task labels
        and makes data array.

        Args:
            roi_info_by_task: `roi_info[task_id]`
            task_id: 24 char BSON id if connected to task, else None

        Returns:
            OrderedDict: Label object populated with ROI attributes
        """
        self.update_nifti_and_shape()
        task_labels = self.get_task_labels(roi_info_by_task, task_id)

        self.make_data(task_labels, roi_info_by_task, task_id)
        return task_labels

    def label2data(self, label: str, roi_info_by_task: dict) -> np.ndarray:
        """From given label and roi_info, returns fill_roi_nifti_slice data

        Args:
            label: ROI location label
            roi_info_by_task: `roi_info[task_id]`

        Returns:
            np.ndarray: Return values of fill_roi_dicom_slice with given args
        """
        data = np.zeros(self.shape, dtype=bool)
        for roi_type in roi_info_by_task:
            for roi in roi_info_by_task[roi_type]:
                if roi.get("location") == label:
                    data = self.fill_roi_nifti_slice(
                        data,
                        self.shape,
                        self.nifti.affine,
                        roi["SeriesInstanceUID"],
                        roi["sliceNumber"],
                        roi["handles"],
                        roi_type=roi_type,
                    )

        return data

    def save_to_roi_dir(self, data: np.ndarray, task_id: t.Optional[str], label: str):
        """Using Nibabel, save data as compressed NIfTI

        Args:
            data: Array created by label2data()
            task_id: 24 char BSON id if connected to task, else None
            label: Task label
        """
        affine = self.prepper.get_affine()
        data = data.astype(self.dtype)
        mask_image = nib.Nifti1Image(data, affine, header=self.nifti.header)
        file_name = f"{self.generate_name(str(task_id), label)}.nii.gz"
        nifti_out = self.roi_dirs[task_id] / file_name
        nib.nifti1.save(mask_image, nifti_out)

    @staticmethod
    def fill_roi_nifti_slice(
        data: np.ndarray,
        shape: t.Tuple,
        affine: np.ndarray,
        plane: str,
        slice_num: int,
        roi_handles: dict,
        roi_type: str = "FreehandRoi",
        reactOHIF: bool = True,
    ) -> np.ndarray:
        """Takes the current state of the full data array, adds the data
        values related to the args passed, and returns updated data.

        Args:
            data: Array passed between this and label2data
            shape: Tuple representation of NIfTI shape
            affine: Input nifti affine
            plane: Sagittal/Axial/Coronal, as stored in SeriesInstanceUID
            slice_num: one-indexed slice identifier, as stored in sliceNumber
            roi_handles: Points or start/end for ROI
            roi_type: Type of ROI annotation. Defaults to "FreehandRoi".
            reactOHIF: Defaults to True.

        Returns:
            np.ndarray: Updated data array
        """

        orientation = nib.aff2axcodes(affine)
        x, y, z = shape
        swap_axes = False
        slice_position = {"x": slice(x), "y": slice(y), "z": slice(z)}
        if plane == "Sagittal":
            flips = [True, True]
            if orientation[0] == "R":
                slice_position["x"] = slice_num - 1
            else:  # Orientation[0] == "L"
                slice_position["x"] = -slice_num
        elif plane == "Coronal":
            if orientation[1] == "A":
                slice_position["y"] = -slice_num
                flips = [False, True]
            elif orientation[1] == "P":
                slice_position["y"] = slice_num - 1
                flips = [True, True]
            elif orientation[2] == "A":
                slice_position["z"] = -slice_num
                flips = [False, True]
            else:  # orientation[2] == "P"
                slice_position["z"] = slice_num - 1
                flips = [True, True]
        else:  # plane == "Axial"
            if orientation[2] == "S":
                slice_position["z"] = -slice_num
                flips = [False, True]
            elif orientation[2] == "I":
                slice_position["z"] = slice_num - 1
                flips = [False, True]
            elif orientation[1] == "S":
                slice_position["y"] = -slice_num
                flips = [True, False]
            else:  # orientation[1] == "I"
                slice_position["y"] = slice_num - 1
                flips = [True, False]

        orientation_slice = data[
            slice_position["x"], slice_position["y"], slice_position["z"]
        ]

        if roi_type == "FreehandRoi":
            if reactOHIF:
                roi_points = roi_handles["points"]
            else:
                roi_points = roi_handles

            # If this slice already has data (i.e. this label was used in an ROI
            # perpendicular to the current slice) we need to have the logical or
            # of that data and the new data
            orientation_slice[:, :] = np.logical_or(
                roi_tools.freehand2mask(
                    roi_points, orientation_slice.shape, flips, swap_axes
                ),
                orientation_slice[:, :],
            )

        elif roi_type == "RectangleRoi":
            start = roi_handles["start"]
            end = roi_handles["end"]

            # If this slice already has data (i.e. this label was used in an ROI
            # perpendicular to the current slice) we need to have the logical or
            # of that data and the new data
            orientation_slice[:, :] = np.logical_or(
                roi_tools.rectangle2mask(
                    start, end, orientation_slice.shape, flips, swap_axes
                ),
                orientation_slice[:, :],
            )

        elif roi_type == "EllipticalRoi":
            start = roi_handles["start"]
            end = roi_handles["end"]

            # If this slice already has data (i.e. this label was used in an ROI
            # perpendicular to the current slice) we need to have the logical or
            # of that data and the new data
            orientation_slice[:, :] = np.logical_or(
                roi_tools.ellipse2mask(
                    start, end, orientation_slice.shape, flips, swap_axes
                ),
                orientation_slice[:, :],
            )

        data[
            slice_position["x"], slice_position["y"], slice_position["z"]
        ] = orientation_slice

        return data

    def make_data(
        self,
        task_labels: dict,
        roi_info_by_task: dict,
        task_id: t.Optional[str],
    ):
        """From ROI info, labels, and task_id, creates the data
        needed for producing the ROI mask output and sends it
        to the converter for conversion.

        Args:
            task_labels: Collected labels, `{label_name: label_object}`
            roi_info_by_task: Equivalent to `roi_info[task_id]`
            task_id: 24 char BSON id if connected to task, else None
        """
        self.set_bit_level(task_labels)
        len_labels = len(task_labels)

        if len_labels > 0:
            log.info("Found %s ROI labels.", len_labels)
        else:
            log.error("Found NO ROI labels.")
            return

        # Store all individual masks to decrease repeat work
        all_data = []

        for label_name, label_object in task_labels.items():
            log.info("Label: %s", label_name)
            data = self.label2data(label_name, roi_info_by_task)

            label_object.num_voxels = np.count_nonzero(data)
            data = data.astype(self.dtype)
            if self.bitmask:
                data *= task_labels[label_name].index

            all_data.append(data)
            if self.combine in ["individual", "both"]:
                self.save_to_roi_dir(data, task_id, label_name)

        if self.combine in ["combined", "both"]:
            data = np.zeros(self.shape, dtype=self.dtype)
            for mask in all_data:
                data += mask

            self.save_to_roi_dir(data, task_id, "ALL")

        self.converter.convert(task_id)

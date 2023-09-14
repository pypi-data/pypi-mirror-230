"""Preppers - Process 1 of 4.

These are designed to prepare any local data for roi creation.  

This typically means the following:
    1. copy the original data (nifti or dicom) to a "working" directory.
    (/flywheel/v0/work/original_image)
    2. create a task-specific directory for storing the mask images.
    (/flywheel/v0/work/{task_id}_roi_image)

    For dicoms, this means either unzipping a zipped file or copying in a full
    directory.  For niftis this will mean just copying the file.
 
Responsibilities:
1. prepare an "original" working directory with a copy of the data
2. prepare empty {task_id}_roi_image directories for storing created data

Full process:
1. Prep
2. Collect
3. Create
4. Convert

"""
import logging
import os
import shutil
import typing as t
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

import nibabel as nib
import numpy as np
from fw_file.dicom import DICOMCollection
from fw_file.dicom.utils import sniff_dcm

log = logging.getLogger(__name__)


class BasePrepper(ABC):
    """Generic BasePrepper class."""

    # Type key set on each base class to identify which class to instantiate
    type_ = None

    def __init__(self, work_dir: os.PathLike, input_file_path: os.PathLike):
        """Initializes BasePrepper

        Args:
            work_dir: Path to work directory
            input_file_path: Path to input file
        """
        if work_dir is None:
            work_dir = ""

        self.work_dir = Path(work_dir)
        self.roi_dirs = {}
        self.orig_dir = self.work_dir / "original_image"
        self.input_file_path = input_file_path

        self.shape = None
        self.affine = None

    @abstractmethod
    def prep(self):
        """Prep method handled within type-specific class."""

    @abstractmethod
    def get_affine(self):
        """Get_affine method handled within type-specific class."""

    def make_task_dirs(self, task_id: t.Optional[str]):
        """Creates subdirectories by task_id in work_dir.

        Args:
            task_id: 24 char BSON id if task-related, None if non-task-related.
        """

        roi_dir_name = str(task_id) + "_roi_image"
        self.roi_dirs[task_id] = self.work_dir / roi_dir_name

        if not os.path.exists(self.roi_dirs[task_id]):
            os.mkdir(self.roi_dirs[task_id])

    @classmethod
    def factory(cls, type_: str, work_dir: os.PathLike, input_file_path: os.PathLike):
        """Return an instantiated prepper based on type."""
        for sub in cls.__subclasses__():
            if type_.lower() == sub.type_:
                return sub(work_dir, input_file_path)

        # If no type_ matches a sub.type_, log exception and exit.
        log.exception("File type %s not supported.", type_)
        os.sys.exit(1)


class PrepDicom(BasePrepper):
    """Prepper for DICOM files"""

    type_ = "dicom"

    def __init__(self, work_dir: os.PathLike, input_file_path: os.PathLike):
        super().__init__(work_dir, input_file_path)
        self.dicoms = {}

    def get_dicoms(self):
        """Returns dicoms."""
        return self.dicoms

    def get_shape(self):
        """Returns [rows, cols, len(dicoms)] as shape."""
        return self.shape

    def prep(self):
        """Prepper for dicoms.

        If the dicom is zipped, unzip to `workdir/original_image`
         - if unzipped, copy the directory.
        Creates subdirectories according to task_id list.
        """
        self.move_dicoms_to_workdir()
        self.populate_dicoms()
        self.check_IOP_tag()
        self.get_affine()

    def move_dicoms_to_workdir(self):
        """Moves DICOM file to work_dir; unzips DICOM if archived."""
        # if archived, unzip dicom into work/dicom/

        if zipfile.is_zipfile(self.input_file_path):
            self.orig_dir.mkdir(parents=True, exist_ok=True)
            dcms = DICOMCollection.from_zip(self.input_file_path)
            dcms.to_dir(self.orig_dir)

        else:
            if not sniff_dcm(self.input_file_path):  # single-dicom
                log.warning(
                    "Input is missing file signature, "
                    "attempting to read as a single dicom."
                )

            if not os.path.exists(self.orig_dir):
                os.mkdir(self.orig_dir)

            shutil.move(self.input_file_path.as_posix(), self.orig_dir.as_posix())

    def populate_dicoms(self) -> DICOMCollection:
        """Saves dicoms to self.dicoms and sets self.shape.

        Returns:
            dicoms: DICOM files as collected.
        """

        dicoms = DICOMCollection.from_dir(self.orig_dir)
        self.dicoms = dicoms

        try:
            # May be more robust to check pixel array sizes if Rows or Columns is
            # missing, but also might want to know if size of image changes across archive.
            rows = self.dicoms.get("Rows")
            cols = self.dicoms.get("Columns")
        except ValueError:
            log.warning(
                f"Row or column values not consistent over all DICOM files. Exiting."
            )
            os.sys.exit(1)

        self.shape = [rows, cols, len(self.dicoms)]
        log.info("DICOM shape: %s", self.shape)

        return dicoms

    def get_affine(self) -> np.ndarray:
        """Using DICOM information, create np.array for affine.

        Returns:
            np.array: Affine
        """

        # If 3D DICOM, use the 3D affine.
        if self.dicoms.get("SpacingBetweenSlices"):
            sbs = self.dicoms.get("SpacingBetweenSlices")
        # Else, use the 2D affine.
        else:
            sbs = 1.0

        pixelspacing = self.dicoms[0].get("PixelSpacing")
        if not pixelspacing:
            pixelspacing = self.dicoms[0].get("ImagerPixelSpacing", [1, 1])

        self.affine = np.array(
            [
                [1 * sbs, 0, 0],
                [0, 1 * pixelspacing[0], 0],
                [0, 0, 1 * pixelspacing[1]],
            ]
        )

        return self.affine

    def check_IOP_tag(self):
        """Checks for ImageOrientationPatient tag. If tag is not present,
        logs a warning that the created mask will not be able to be
        overlaid on top of the original DICOM file in the Flywheel viewer.
        """
        if not self.dicoms.get("ImageOrientationPatient"):
            log.warning(
                "ImageOrientationPatient tag not found on input DICOM. "
                "NIfTI mask will not be compatible with being overlaid "
                "on the original DICOM in the Flywheel viewer."
            )


class PrepNifti(BasePrepper):
    """Prepper for NIfTI files."""

    type_ = "nifti"

    def __init__(self, work_dir: os.PathLike, input_file_path: os.PathLike):
        super().__init__(work_dir, input_file_path)
        self.nifti = {}

    def prep(self):
        """Load NIfTI and set self.shape"""
        self.nifti = nib.load(self.input_file_path.as_posix())

        self.shape = self.nifti.shape
        log.info("NIfTI shape: %s", self.shape)

        return self.nifti

    def get_nifti(self):
        """Returns loaded NIfTI."""
        return self.nifti

    def get_shape(self):
        """Returns loaded NIfTI's shape."""
        return self.shape

    def get_affine(self):
        """Returns loaded NIfTI's affine"""
        self.affine = self.nifti.affine

        return self.affine

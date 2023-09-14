"""Conversion module."""

import logging
import os
from dataclasses import dataclass

log = logging.getLogger(__name__)

NIFTI_TYPE = "nii"
NRRD_TYPE = "nrrd"


@dataclass
class MethodTypes:
    """Generic MethodTypes class for Conversion"""

    method: str
    valid_source: list
    valid_dest: list

    def validate(self, source: str, dest: str):
        """Checks whether source and dest are compatible with conversion type

        Args:
            source: Original filetype
            dest: Requested output filetype

        Raises:
            Exception: Invalid source if source not in valid_source
            Exception: Invalid destination if dest not in valid_dest

        Returns:
            True if valid configuration
        """
        if source.lower() not in self.valid_source:
            log.exception("Invalid source %s for method %s", source, self.method)
            os.sys.exit(1)

        if dest.lower() not in self.valid_dest:
            log.exception("Invalid destination %s for method %s", dest, self.method)
            os.sys.exit(1)

        log.info(
            "Export set as %s to %s, conversion method %s.",
            source,
            dest,
            self.method,
        )
        return True


dcm2niix_valid_source = ["dicom"]
dcm2niix_valid_dest = ["nifti", "nrrd"]
METHOD_DCM2NIIX = MethodTypes(
    method="dcm2niix",
    valid_source=dcm2niix_valid_source,
    valid_dest=dcm2niix_valid_dest,
)


niix2niix_valid_source = ["nifti"]
niix2niix_valid_dest = ["nifti"]
METHOD_NIIX2NIIX = MethodTypes(
    method="niix2niix",
    valid_source=niix2niix_valid_source,
    valid_dest=niix2niix_valid_dest,
)


@dataclass
class ConversionType:
    """Generic ConversionType class for storing conversion configuration and validity"""

    source: str = ""
    dest: str = ""
    method_name: str = ""
    method: MethodTypes = MethodTypes
    ext: str = ""

    def __post_init__(self):
        """Sets method and ext."""
        if self.method_name == "dcm2niix":
            self.method = METHOD_DCM2NIIX
        elif self.method_name == "niix2niix":
            self.method = METHOD_NIIX2NIIX

        lookup = {NIFTI_TYPE: ["nifti", "nii", ".nii"], NRRD_TYPE: ["nrrd", ".nrrd"]}

        for e, vals in lookup.items():
            if self.dest.lower() in vals:
                self.ext = e
                break

    def validate(self):
        """Checks validity of configuration

        Returns:
            bool: True if valid configuration
        """
        return self.method.validate(self.source, self.dest)

    def describe(self):
        """Outputs description of conversion configuration

        Returns:
            str: Method source to dest
        """
        return f"{self.method.method} {self.source} to {self.dest}"

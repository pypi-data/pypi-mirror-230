"""Converter - Process 4 of 4.

Responsible for converting the working roi directory from one format to another.
This will undoubtedly become more and more complicated as more things get added...
For example, nifti to dicom will require a lot of affine information and stuff...
If we can't directly recover that data from the original file, then things will
have to get passed in which will increase complexity.

For now I'm focusing on dicom to other formats.  Future problems are for future David.

I learned this technique to kind of split up responsibilities, and when I read the tutorials
and watch videos of simple examples it seems so straightforward and good.  Then I try to
implement it, and i have all these cases where thigns from one part of the code depend
on things from other parts of the code, and it just gets complicated.  So while I started off
with the intention to simplify, I always end up with this monstrosity of a code block by the
end, and I wonder if I actually succeeded or not.  This happens a lot.
But I do think I'm getting better, idk.


Full process:
1. Prep
2. Collect
3. Create
4. Convert

"""

import logging
import os
import subprocess as sp
import typing as t
from abc import ABC, abstractmethod

from fw_gear_mask_exporter.objects import Conversion
from fw_gear_mask_exporter.objects.Conversion import (
    NIFTI_TYPE,
    NRRD_TYPE,
    ConversionType,
)
from fw_gear_mask_exporter.workers import Preppers

log = logging.getLogger()

DCM2NIIX_PATH = "dcm2niix"


class BaseConverter(ABC):
    """Generic converter class object, for use with type-specific converters."""

    type_ = None

    def __init__(
        self,
        prepper: Preppers.BasePrepper,
        output_dir: os.PathLike,
        conversion: t.Optional[Conversion.ConversionType] = None,
        additional_args: t.Optional[str] = None,
    ):
        """Initializes Converter class object.

        Args:
            prepper: instantiated Prepper class object
            output_dir: output directory for converted file(s)
            conversion: instantiated Conversion class object. Optional, defaults to None.
            additional_args: additional command options for conversion. Optional, defaults to None.
        """
        self.prepper = prepper
        self.output_dir = output_dir
        self.conversion = conversion
        self.additional_args = additional_args

        self.ext = self.conversion.ext

    @abstractmethod
    def convert(self, output_filename: str):
        """Handled in conversion type-specific class object."""

    @classmethod
    def factory(
        cls,
        type_: str,
        prepper: Preppers.BasePrepper,
        output_dir: os.PathLike,
        conversion: Conversion.ConversionType,
        additional_args: t.Optional[str] = None,
    ):
        """Return an instantiated converter.

        Args:
            type_: conversion method (currently only dcm2niix supported)
            prepper: instantiated prepper class object
            output_dir: output directory for converted file(s)
            conversion: instantiated Conversion class object
            additional_args: additional command options for conversion. Optional, defaults to None.

        Returns:
            instantiated converter class object
        """
        for sub in cls.__subclasses__():
            if type_.lower() == sub.type_:
                return sub(
                    prepper=prepper,
                    output_dir=output_dir,
                    conversion=conversion,
                    additional_args=additional_args,
                )

        # If no type_ matches a sub.type_, log exception and exit.
        log.exception("File type %s not supported.", type_)
        os.sys.exit(1)


class dcm2niix(BaseConverter):
    """dcm2niix specific converter methods."""

    type_ = "dcm2niix"

    def run_command(self, command: list):
        """Executes the given command and waits for completion.

        Args:
            command: Command as list of elements, built by make_command
        """
        pr = sp.Popen(command)
        pr.wait()

    def convert(
        self,
        output_filename: str,
        task_id: t.Optional[str],
    ):
        """Converts DICOMs as specified.

        Args:
            output_filename: Name to save output under
            task_id: 24 char BSON string if task, else None if non-task
        """

        command = self.make_command(output_filename, task_id)
        self.run_command(command)

    def make_command(
        self,
        output_filename: str,
        task_id: t.Optional[str],
    ) -> list:
        """Builds the command as configured.

        Args:
            output_filename: Name to save output under
            task_id: 24 char BSON string if task, else None if non-task

        Returns:
            list: Elements required to execute command as configured
        """
        nrrd_cmd = [""]
        compression_cmd = [""]
        if self.conversion.ext == NRRD_TYPE:
            nrrd_cmd = ["-e", "y"]
        elif self.conversion.ext == NIFTI_TYPE:
            compression_cmd = ["-z", "y"]

        add_cmds = [""]
        if self.additional_args:
            add_cmds = self.additional_args.split()

        command = [
            DCM2NIIX_PATH,
            "-o",
            self.output_dir.as_posix(),
            "-f",
            output_filename,
            "-b",
            "n",
            *compression_cmd,
            *nrrd_cmd,
            *add_cmds,
            self.prepper.roi_dirs[task_id].as_posix(),
        ]
        command = [c for c in command if c]
        log.info("dcm2niix command: %s", (" ".join(command)))
        return command


class niix2niix(BaseConverter):
    """NIfTI-NIfTI passthrough converter class"""

    type_ = "niix2niix"

    def run_command(self, command: list):
        """Executes the given command and waits for completion.

        Args:
            command: Command as list of elements, built by make_command
        """
        pr = sp.Popen(command)
        pr.wait()

    def convert(
        self,
        output_filename: t.Optional[str] = None,
        task_id: t.Optional[str] = None,
    ):
        """Instead of converting, moves all files from task_id work directory to
        the output directory.

        Args:
            output_filename: Name to save output under, else None if pass-through
            task_id: 24 char BSON string if task, else None if non-task
        """

        command = self.make_command(task_id)
        self.run_command(command)

    def make_command(
        self,
        task_id: t.Optional[str],
    ) -> list:
        """Builds the command as configured.

        Args:
            task_id: 24 char BSON string if task, else None if non-task

        Returns:
            list: Elements required to execute command as configured
        """

        command = [
            "cp",
            "-r",
            f"{self.prepper.roi_dirs[task_id].as_posix()}/.",
            self.output_dir.as_posix(),
        ]

        command = [c for c in command if c]
        log.info("Command: %s", (" ".join(command)))
        return command

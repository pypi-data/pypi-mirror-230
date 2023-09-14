"""Parser module to parse gear config.json"""
import logging
import sys
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext
from fw_client import FWClient

from fw_gear_mask_exporter.objects.Files import FileObject

log = logging.getLogger(__name__)


def parser(gear_context: GearToolkitContext) -> tuple[bool, dict]:
    """Parses context's config.json file to be used by gear

    Args:
        gear_context: to provide configuration information

    Returns:
        debug: Debug configuration, default False
        gear_args: Arguments needed for the gear to run as configured, including
            * annotations_scope: Whether to save task, non-task, or both
            * save_combined_output: Whether or not to combine output into single file, default False
            * save_binary_masks: Whether or not to output binary masks, default True
            * save_nrrd: Save as .nrrd instead of .nii
            * additional_args: Additional arguments to be passed to converter
            * input_file_path: Path to input
            * work_dir: Path to work directory
            * output_dir: Path to output directory
            * file_obj: Input file as FileObject
            * fw: FWClient instance, logged in with api-key
    """

    debug = gear_context.config.get("debug")
    gear_args = {
        "annotations_scope": gear_context.config.get("annotations-scope", "both"),
        "save_combined_output": gear_context.config.get(
            "save-combined-output", "individual"
        ),
        "save_binary_masks": gear_context.config.get("save-binary-masks", False),
        "save_nrrd": gear_context.config.get("save-nrrd", False),
        "additional_args": gear_context.config.get("additional-args", None),
        "input_file_path": Path(gear_context.get_input_path("input-file")),
        "work_dir": Path(gear_context.work_dir),
        "output_dir": Path(gear_context.output_dir),
    }

    input_file_obj = gear_context.get_input("input-file")
    input_file_id = input_file_obj["object"]["file_id"]
    fw_file = gear_context.client.get_file(input_file_id)
    file_obj = FileObject(gear_args["input_file_path"], fw_file)
    gear_args["file_obj"] = file_obj

    gear_args["fw"] = FWClient(
        api_key=gear_context.get_input("api-key")["key"],
        read_timeout=100,
        connect_timeout=100,
    )

    return debug, gear_args

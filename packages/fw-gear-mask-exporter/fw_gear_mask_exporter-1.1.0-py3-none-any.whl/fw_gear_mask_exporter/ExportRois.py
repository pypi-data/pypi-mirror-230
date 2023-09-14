"""ExportRois module."""
import logging
import os
import typing as t

from fw_client import FWClient

from fw_gear_mask_exporter.MeasurementExporter import MeasurementExport
from fw_gear_mask_exporter.objects.Files import FileObject
from fw_gear_mask_exporter.roi_tools import calculate_ROI_volume, output_ROI_info

log = logging.getLogger(__name__)


def main(
    annotations_scope: str,
    save_combined_output: str,
    save_binary_masks: bool,
    save_nrrd: bool,
    additional_args: t.Optional[str],
    input_file_path: os.PathLike,
    work_dir: os.PathLike,
    output_dir: os.PathLike,
    file_obj: FileObject,
    fw: FWClient,
):
    """Passes configuration to MeasurementExporter, using the gear_args dict
    created by parser.py, and processes the file.

    Args:
        annotations_scope: Whether to save task, non-task, or both
        save_combined_output: Whether to save masks as individual, combined, or both
        save_binary_masks: Whether or not to output binary masks, default True
        save_nrrd: Whether or not to output .nrrd
        additional_args: Any additional arguments to be passed to the converter
        input_file_path: Path to input
        work_dir: Path to work directory
        output_dir: Path to output directory
        file_obj: Input as FileObject
        fw: FWClient instance, logged in with api-key

    Returns:
        0 on success
    """

    exporter = MeasurementExport(
        file_obj=file_obj,
        work_dir=work_dir,
        output_dir=output_dir,
        input_file_path=input_file_path,
        annotations_scope=annotations_scope,
        save_nrrd=save_nrrd,
        additional_args=additional_args,
        combine=save_combined_output,
        bitmask=save_binary_masks,
        fw=fw,
    )

    exporter.process_file()
    all_labels = exporter.creator.labels
    affine = exporter.prepper.affine

    for task_id in exporter.collector.all_task_ids:
        # Calculate the voxel and volume of each ROI by label
        calculate_ROI_volume(all_labels, affine, task_id)

        # Output csv file with ROI index, label, num of voxels, and ROI volume
        output_ROI_info(output_dir, all_labels, task_id)

    return 0

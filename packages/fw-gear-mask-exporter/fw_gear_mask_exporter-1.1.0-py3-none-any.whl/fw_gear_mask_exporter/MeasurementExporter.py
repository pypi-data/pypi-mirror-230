"""MeasurementExport module."""
import logging
import os
import typing as t

from fw_client import FWClient

from fw_gear_mask_exporter.objects import Conversion
from fw_gear_mask_exporter.objects.Files import FileObject
from fw_gear_mask_exporter.workers import Collectors, Converters, Creators, Preppers

log = logging.getLogger(__name__)


class MeasurementExport:
    """Exports measurements from files on Flywheel."""

    def __init__(
        self,
        file_obj: FileObject,
        work_dir: os.PathLike,
        output_dir: os.PathLike,
        input_file_path: os.PathLike,
        annotations_scope: str,
        save_nrrd: bool,
        additional_args: t.Optional[str],
        combine: str,
        bitmask: bool,
        fw: FWClient,
    ):
        """Initializes MeasurementExport

        Args:
            file_obj: Input file as FileObject
            work_dir: Path to work directory
            output_dir: Path to output directory
            input_file_path: Path to input file
            annotations_scope: Whether to save task-only, non-task-only, or both
            save_nrrd: Whether to output a NRRD file
            additional_args: Any additional arguments to be passed to the converter
            combine: Whether to save masks as individual, combined, or both
            bitmask: Whether or not to output binary masks
        """

        self.file_object = file_obj
        self.orig_file_type = self.file_object.file_type

        log.info("Generating workers...")

        # Conversion object is like a pre-check of valid input/output/conversion software types
        self.conversion = self.generate_conversion(
            orig_file_type=self.file_object.file_type,
            save_nrrd=save_nrrd,
        )

        self.prepper = self.generate_prepper(
            work_dir=work_dir,
            input_file_path=input_file_path,
            orig_file_type=self.orig_file_type,
        )

        self.collector = self.generate_collector(
            orig_dir=self.prepper.orig_dir,
            file_object=self.file_object,
            orig_file_type=self.orig_file_type,
            output_dir=output_dir,
            fw=fw,
            scope=annotations_scope,
        )

        self.converter = self.generate_converter(
            conversion=self.conversion,
            prepper=self.prepper,
            output_dir=output_dir,
            additional_args=additional_args,
        )

        self.creator = self.generate_creator(
            converter=self.converter,
            file_object=self.file_object,
            prepper=self.prepper,
            combine=combine,
            bitmask=bitmask,
        )

        log.info("Worker generation complete.")

    def get_affine(self):
        """Returns affine as stored in the prepper.

        Returns:
            np.ndarray: Affine
        """
        return self.prepper.get_affine()

    @staticmethod
    def generate_conversion(
        orig_file_type: str, save_nrrd: bool
    ) -> Conversion.ConversionType:
        """Creates ConversionType class object

        Args:
            orig_file_type: Original filetype, currently only "dicom" valid
            save_nrrd: Whether or not to save as NRRD.

        Returns:
            conversion: ConversionType, with .validate and .describe methods.
        """
        dest_file_type = "nrrd" if save_nrrd else "nifti"
        conversion_type = "dcm2niix" if orig_file_type == "dicom" else "niix2niix"
        conversion = Conversion.ConversionType(
            orig_file_type, dest_file_type, conversion_type
        )
        _valid = conversion.validate()
        return conversion

    @staticmethod
    def generate_prepper(
        work_dir: os.PathLike,
        input_file_path: os.PathLike,
        orig_file_type: str,
    ) -> Preppers.BasePrepper:
        """Creates prepper based on original filetype

        Args:
            work_dir: Path to work directory
            input_file_path: Path to input file
            orig_file_type: Original filetype, "dicom" or "nifti"

        Returns:
            Prepper based on input filetype
        """
        return Preppers.BasePrepper.factory(orig_file_type, work_dir, input_file_path)

    @staticmethod
    def generate_collector(
        orig_dir: os.PathLike,
        file_object: FileObject,
        orig_file_type: str,
        output_dir: os.PathLike,
        fw: FWClient,
        scope: bool,
    ) -> Collectors.BaseCollector:
        """Creates collector based on original filetype

        Args:
            file_object: File of which to collect ROIs
            orig_dir: From prepper.orig_dir
            output_dir: Directory in which outputs will be placed
            fw: Flywheel client, logged in with api-key
            scope: annotations scope, task-only, non-task-only, both

        Returns:
            Collector, DicomRoiCollector or NiftiRoiCollector
        """
        return Collectors.BaseCollector.factory(
            type_=orig_file_type,
            orig_dir=orig_dir,
            file_object=file_object,
            output_dir=output_dir,
            fw=fw,
            scope=scope,
        )

    @staticmethod
    def generate_converter(
        conversion: Conversion.ConversionType,
        prepper: Preppers.BasePrepper,
        output_dir: os.PathLike,
        additional_args: t.Optional[str],
    ) -> Converters.BaseConverter:
        """Creates converter based on original filetype (Only DICOM currently supported)

        Args:
            conversion: Conversion class object
            prepper: Prepper class object
            output_dir: Path to output directory
            additional_args: Additional arguments to pass through converter (optional)

        Returns:
            Converter
        """
        return Converters.BaseConverter.factory(
            type_=conversion.method_name,
            prepper=prepper,
            output_dir=output_dir,
            conversion=conversion,
            additional_args=additional_args,
        )

    @staticmethod
    def generate_creator(
        converter: Converters.BaseConverter,
        file_object: FileObject,
        prepper: Preppers.BasePrepper,
        combine: bool,
        bitmask: bool,
    ) -> Creators.BaseCreator:
        """Creates creator based on original filetype

        Args:
            converter: Converter class object
            file_object: File of which to collect ROIs
            prepper: Prepper class object
            combine: Whether or not to combine output into single file
            bitmask: Whether or not to output binary masks

        Returns:
            Creator
        """
        return Creators.BaseCreator.factory(
            type_=file_object.file_type,
            prepper=prepper,
            base_file_name=file_object.base_name,
            combine=combine,
            bitmask=bitmask,
            converter=converter,
        )

    def process_file(self):
        """Follows the necessary prep for filetype,
        collects all ROIs and sorts them by task_id,
        then iterates through task_ids to process the entire file.
        """
        self.prepper.prep()
        self.collector.collect()
        for task_id in self.collector.all_task_ids:
            self.process_task(task_id)

    def process_task(self, task_id: t.Optional[str]):
        """Processes individual task within the file.

        Args:
            task_id: 24 char BSON id if connected to task, else None
        """
        if task_id:
            log.info("Processing task_id %s", task_id)
        else:
            log.info("Processing non-task annotations.")

        self.prepper.make_task_dirs(task_id)
        self.creator.create(self.collector.roi_info[task_id], task_id)


"""
Overview:

MeasurementExporter:
    - file_object - holds the file and info on it
    - roi_object - holds the roi and generates the roi.  Will have a "roi_generator" object, which
        can be a "dicom ROI generator", or a "nifti roi generator".  
        For dicoms, there needs to be some mapping between which slice goes to which dicom object.
        This isn't necessary for niftis as it's 1:1.  Therefor, I think the dicom_ROI_Generator should 
        have this property and store it when it gets created.  Later, the ROI_object will be passed into the 
        "ROI exporter", which will know where to look and can handle that.
    - ROI_exporter - probably the workhorse of this class.  This will have to be the one that's unique for 
        each kind of export.  dcm2niix exporter, slicer exporter, plastimatch exporter, dicom2nifti exporter,
        nifti2nifti exporter.
        takes: roi_object, file_object
        returns: nothing but saves the roi file out. 
    - output_type
    

ROI_generator:
    - generates the ROI's from a source file
    will either be dicom generator or nifti generator, each with a "generate()" function.

"""


# Notes:
"""
1. I think self.labels.num_voxels is wrong...wait no JK I think it's correct
2. Working on the collector - it needs 
   a. collect all ROI's related to the given image and
   b. to make the ROI label list
   
   I think this is done well in the original code, but possible room
   for improvement?

3. The collector will need to pass the label/ohif metadata object
back out to the orchestrator I think, because NEXT is the generator,
which will rely on those to move forward.  The generator simply
Generates ROI images in the original image format.
4. Finally the converter.  THE CONVERTER IS A PROPERTY OF THE GENERATOR.
Or maybe it should be generator is part of the converter... But they should be nested
since they need to work together.  If multiple binary labels exist, it will need to:
 a. make the mask iimage for label 1 in the original image format and save
 b. convert that to the desired image format
 c. repeat for all labels.
So this has to be self-contained, it can't loop the right way otherwise.
"""

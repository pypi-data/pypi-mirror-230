import pytest
from pathlib import Path


@pytest.mark.skipif(True, reason='no live test to be performed')
def test_temp():
    db_path = Path('tests/output/test_temp.db')
    archive_path = Path('tests/input/temp')
    target_path = Path('tests/output/convert_temp')

    main(db_path, archive_path, target_path, max_workers=2)


import tempfile
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import SimpleITK as sitk
import pytest

from dicomselect import DICOMImageReader
from picai_prep import atomic_file_copy


def check_dicom_slices(reader: "DICOMImageReader") -> Tuple[bool, str]:
    """
    Check if the DICOM slices from a reader likely make up a single 3D volume.

    This function verifies if all the DICOM slices have matching metadata values required
    for them to form a single 3D volume. Specifically, it checks for consistency in:
    - PatientID
    - StudyInstanceUID
    - SeriesInstanceUID
    - ImageOrientationPatient
    - PixelSpacing
    - FrameOfReferenceUID
    - InstanceNumber (checking if they are consecutive)
    - SequenceName

    Parameters:
    - reader (DICOMImageReader): The DICOM image reader object that iterates through the metadata of DICOM slices.

    Returns:
    - Tuple[bool, str]: A tuple where the first element is a boolean indicating whether all checks passed
                        (True if the slices likely make up a single 3D volume, False otherwise),
                        and the second element is a descriptive message string.

    Example:
    reader = DICOMImageReader("/path/to/dicom/files")
    is_valid, message = check_dicom_slices(reader)
    if is_valid:
        print("DICOM slices likely make up a single 3D volume.")
    else:
        print(f"Error: {message}")
    """

    # Initial values
    series_instance_uid = None
    patient_id = None
    study_instance_uid = None
    image_orientation_patient = None
    pixel_spacing = None
    frame_of_reference_uid = None
    instance_numbers = []
    sequence_name = None

    # Loop through each DICOM file
    for index in range(len(reader)):
        metadata = reader._get_metadata(index)

        # Checking Patient ID
        current_patient_id = metadata["patient_id"]
        if patient_id is None:
            patient_id = current_patient_id
        elif patient_id != current_patient_id:
            return False, "Mismatch in PatientID."

        # Checking Study Instance UID
        current_study_instance_uid = metadata["study_instance_uid"]
        if study_instance_uid is None:
            study_instance_uid = current_study_instance_uid
        elif study_instance_uid != current_study_instance_uid:
            return False, "Mismatch in StudyInstanceUID."

        # Checking Series Instance UID
        current_series_instance_uid = metadata["series_instance_uid"]
        if series_instance_uid is None:
            series_instance_uid = current_series_instance_uid
        elif series_instance_uid != current_series_instance_uid:
            return False, "Mismatch in SeriesInstanceUID."

        # Checking Image Orientation Patient
        current_image_orientation_patient = metadata["image_orientation_patient"]
        if image_orientation_patient is None:
            image_orientation_patient = current_image_orientation_patient
        elif image_orientation_patient != current_image_orientation_patient:
            return False, "Mismatch in ImageOrientationPatient."

        # Checking Pixel Spacing
        current_pixel_spacing = metadata["pixel_spacing"]
        if pixel_spacing is None:
            pixel_spacing = current_pixel_spacing
        elif pixel_spacing != current_pixel_spacing:
            return False, "Mismatch in PixelSpacing."

        # Checking Frame of Reference UID
        current_frame_of_reference_uid = metadata["frame_of_reference_uid"]
        if frame_of_reference_uid is None:
            frame_of_reference_uid = current_frame_of_reference_uid
        elif frame_of_reference_uid != current_frame_of_reference_uid:
            return False, "Mismatch in FrameOfReferenceUID."

        # Collecting Instance Numbers
        instance_numbers.append(int(metadata["instance_number"]))

        # Checking Sequence Names
        current_sequence_names = metadata["sequence_name"]
        if sequence_name is None:
            sequence_name = current_sequence_names
        elif sequence_name != current_sequence_names:
            return False, "Mismatch in SequenceName."

    # Check if Instance Numbers are consecutive
    if sorted(instance_numbers) != list(range(min(instance_numbers), max(instance_numbers) + 1)):
        return False, "Instance Numbers are not consecutive."

    return True, "All checks passed. The DICOM slices likely make up a single 3D volume."


def construct_multiple_volumes(dicom_dir: Union[Path, str], splitting_tag: str = "0018|0024") -> Dict[str, Any]:
    """
    Construct multiple volumes from DICOM files in a directory, grouping them based on a splitting tag.

    The function reads DICOM files from the specified directory and groups them into separate volumes based on
    the value of the specified splitting tag. Each volume is read separately, and a validity check is performed
    on the DICOM slices.

    Parameters:
    - dicom_dir (Union[Path, str]): The directory containing the DICOM files to be processed.
    - splitting_tag (str, optional): The DICOM tag used to split the files into separate volumes.
                                     Defaults to "0018|0024".

    Returns:
    - Dict[str, Any]: A dictionary where keys are the splitting values and values are dictionaries containing:
        - "image": The constructed volume image (SimpleITK.Image).
        - "valid": A boolean indicating whether the DICOM slices are valid.
        - "message": A message string providing details in case the DICOM slices are not valid.

    Example:
    result = construct_multiple_volumes("/path/to/dicom/files")
    for splitting_value, volume_info in result.items():
        print(f"Splitting value: {splitting_value}, Valid: {volume_info['valid']}, Message: {volume_info['message']}")
        image = volume_info["image"]
        # Process the image ...
    """

    dicom_dir = Path(dicom_dir)
    file_reader = sitk.ImageFileReader()

    result: Dict[str, Any] = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        scan_folders = {}

        for path_src in dicom_dir.glob("*.dcm"):
            file_reader.SetFileName(str(path_src))
            file_reader.LoadPrivateTagsOn()
            file_reader.ReadImageInformation()
            splitting_value: str = file_reader.GetMetaData(splitting_tag)

            # make folders for each splitting value
            dir_dst = tmpdir / splitting_value
            dir_dst.mkdir(exist_ok=True)
            scan_folders[splitting_value] = dir_dst

            # copy DICOM slice to temporary directory
            path_dst = dir_dst / path_src.name
            atomic_file_copy(path_src, path_dst)

        # read each scan individually
        for splitting_value, dir_dst in scan_folders.items():
            reader = DICOMImageReader(dir_dst, verify_dicom_filenames=False)
            valid, message = check_dicom_slices(reader=reader)
            img = reader.image
            result[splitting_value] = {
                "image": img,
                "valid": valid,
                "message": message,
            }

    return result


import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Union

import numpy as np
from dicomselect import Database, DICOMImageReader


def include_if_sufficient_unique_values(
        scans: Union[sitk.Image, Dict[str, sitk.Image]],
        min_unique_values: int = 100,
) -> Union[sitk.Image, Dict[str, sitk.Image]]:
    if isinstance(scans, sitk.Image):
        if len(np.unique(sitk.GetArrayFromImage(scans))) >= min_unique_values:
            return scans
        else:
            return False

    scans = {
        k: v
        for k, v in scans.items()
        if len(np.unique(sitk.GetArrayFromImage(v))) >= min_unique_values
    }
    if len(scans) == 0:
        return False

    return scans


def postprocess_func(reader: DICOMImageReader, verbose: int = 0) -> Union[sitk.Image, bool]:
    # Check if DICOM slices are valid
    valid, message = check_dicom_slices(reader=reader)
    if valid:
        # Folder likely contains a single 3D volume
        return include_if_sufficient_unique_values(reader.image)
    elif verbose >= 1:
        print(f"Trying to divide DICOM slices in multiple volumes (after {message})")

    # Check if folder contains multiple sequences
    path = reader.path
    if not path.is_dir() and path.suffix == ".zip":
        # unzip to temporary folder
        with tempfile.TemporaryDirectory() as tempdir, zipfile.ZipFile(path) as zf:
            if not zf.namelist():
                raise RuntimeError("dicom zip is empty")

            zf.extractall(tempdir)
            scans = construct_multiple_volumes(dicom_dir=tempdir)
    else:
        scans = construct_multiple_volumes(dicom_dir=path)

    if verbose >= 2:
        for splitting_value, volume_info in scans.items():
            print(
                f"Splitting value: {splitting_value}, Valid: {volume_info['valid']}, Message: {volume_info['message']}")

    # Select valid scans
    scans = {f"_{k}": v["image"] for k, v in scans.items() if v["valid"]}
    return include_if_sufficient_unique_values(scans)


def main(
        db_path: Union[Path, str],
        archive_dir: Union[Path, str],
        target_dir: Union[Path, str],
        max_workers: int = 8,
):
    """Convert scans from DICOM to MHA."""

    # Set up paths
    db_path = Path(db_path)
    target_dir = Path(target_dir)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Set up DICOM database
    db = Database(db_path)
    if not db_path.exists():
        print(f"Creating new database at {db_path}")
        db.create(archive_dir, max_workers=max_workers)

    # Select scans to convert to MHA
    cursor = db.open()
    query = cursor.where(
        "series_description",
        "LIKE",
        [r"%localizer%", r"%Localizer%", r"loc%", r"%loc", r"%SURVEY%", r"SURV%"],
        invert=True
    ).where(
        "samples_per_pixel",
        "=",
        1,  # grayscale, exclude vector images (77 occurrences)
    ).where(
        "modality",
        "=",
        "MR",  # exclude OT and SC (3 occurences)
    ).where(
        "mr_acquisition_type",
        "IN",
        ["2D", "3D"],  # exclude unknown (4717 occurences)
    ).where(
        "imaged_nucleus",
        "!=",
        "SPECT",  # exclude SPECT (1 occurence)
    ).where(
        "manufacturer",
        "IN",
        [
            "SIEMENS",
            "Philips Medical Systems",
            "GE MEDICAL SYSTEMS",
            "Philips Healthcare",
            "Siemens Healthcare",
            "Siemens",
            "Siemens Healthineers",
            "Siemens HealthCare GmbH",
            "Philips",
        ],  # include typical manufacturers (Siemens, Philips, GE)
        # exclude unknown, Agfa, Hitachi, Toshiba, Merge, Vital, Marconi, Barco, Terarecon, Telemis
        # also exclude things that look like a Study ID (e.g. 1.3.12.2.1107.5.2.5.10550.5.0.4629194367471299)
        # excludes, in total, 2231 occurrences
    ).where(
        "patients_age",
        "BETWEEN",
        [18, 100],
        # exclude patients younger than 18 (21853 occurrences, of which 1580 younger than 1), older than 100 (46 occurrences, all aged 113)
    ).where(
        "study_description",
        "LIKE",
        [r"MY%", r"AI%", r"% CT %", r"CT %", r"DL %", r"US %", r"Samenvattende studie%"],
        invert=True,  # exclude CT, US, DL, AI, MY, Samenvattende studie
    )

    exclude_columns = (
        "image_orientation_patient", "patient_id", "imaging_frequency", "study_date",
        "window_width", "window_center", "patients_birth_date",
    )
    exclude_args = {
        "exclude_all_distinct": True,
        "exclude_none_distinct": True
    }

    dicomconvert_plan = query.info().exclude(*exclude_columns, **exclude_args).to_string()
    with open(db_path.with_name("dicomconvert_plan.txt"), "w") as f:
        f.write(dicomconvert_plan)

    # Make conversion plan
    plan = db.plan(r"{patient_id}/{patient_id}_{study_instance_uid}_{series_instance_uid}", query)
    plan.target_dir = target_dir
    plan.extension = ".mha"

    # Save conversion plan
    with open(db_path.with_name("conversion_plan.txt"), "w") as f:
        f.write(plan.to_string())

    # Execute conversion plan
    plan.execute(postprocess_func=postprocess_func)
    db.close()

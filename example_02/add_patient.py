from datetime import datetime
import glob
import hashlib
import os
from typing import List, Tuple

from absl import app
from absl import flags
from absl.flags._flagvalues import FlagValues

import patient_info_pb2

SUBJECTS = {
    "podcast": [
        "661",
        "662",
        "717",
        "723",
        "737",
        "741",
        "742",
        "743",
        "763",
        "798",
    ],
    "tfs": ["625", "676", "7170", "798", "7986"],
}

ELECTRODE_FOLDER_MAP = {
    "podcast": dict.fromkeys(
        SUBJECTS["podcast"],
        "preprocessed_all",
    ),
    "tfs": dict.fromkeys(["625", "676"], "preprocessed")
    | dict.fromkeys(["7170"], "preprocessed_v2")
    | dict.fromkeys(["798"], "preprocessed_allElec"),
}

DATUM_FILE_MAP = {
    "podcast": dict.fromkeys(
        SUBJECTS["podcast"],
        "*trimmed.txt",
    ),
    "tfs": dict.fromkeys(["625", "676"], "*trimmed.txt")
    | dict.fromkeys(["7170", "798"], "*_datum_trimmed.txt"),
}


FLAGS = flags.FLAGS
flags.DEFINE_string("project", None, "Project ID")
flags.DEFINE_string("subject", None, "Subject ID")
flags.DEFINE_string("data_dir", None, "Data directory")

# Required flag.
flags.mark_flag_as_required("project")
flags.mark_flag_as_required("subject")
flags.mark_flag_as_required("data_dir")


def get_out_filename(project: str, subject: str, data_dir: str) -> str:
    """
    Generates the output filename for a given project and subject.

    Args:
        project: The name of the project.
        subject: The subject of the data.
        data_dir: The directory where the data is stored.

    Returns:
        The output filename with a timestamp.

    """
    parent_dir = os.path.dirname(os.path.normpath(data_dir))
    out_filename = os.path.join(parent_dir, f"{project}_{subject}.pb")
    # out_filename = add_timestamp_to_filename(out_filename)

    return out_filename


def add_timestamp_to_filename(filename: str) -> str:
    """
    Adds a timestamp to the given filename.

    Args:
        filename: The filename to add a timestamp to.

    Returns:
        The filename with a timestamp appended.

    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename_with_timestamp = f"{filename}_{timestamp}"
    return filename_with_timestamp


def calculate_checksum(
    file_path: str, algorithm: str = "sha256", buffer_size: int = 65536
) -> str:
    """Calculate the checksum of a file.

    Args:
        file_path (str): The path of the file.
        algorithm (str, optional): The hashing algorithm to use. Defaults to
          "sha256".
        buffer_size (int, optional): The buffer size for reading the file.
          Defaults to 65536.

    Returns:
        str: The checksum of the file.
    """
    hasher = hashlib.new(algorithm)
    with open(file_path, "rb") as file:
        buffer = file.read(buffer_size)
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = file.read(buffer_size)
    return hasher.hexdigest()


def extract_integer_suffix(filename: str) -> int:
    """
    Extracts the integer suffix of a given filename.

    Args:
        filename (str): The name of the file.

    Returns:
        int: The integer suffix of the filename.
    """
    return int(os.path.splitext(filename)[0].split("_")[-1])


def get_conversations(data_dir: str) -> List[str]:
    """
    Get a sorted list of conversation names from the given data directory.

    Args:
        data_dir: The path to the data directory.

    Returns:
        A sorted list of conversation names.
    """
    return sorted(glob.glob(os.path.join(data_dir, "*")))[:3]


def get_electrode_folder(project: str, data_dir: str, conversation: str) -> str:
    """
    Returns the path to the electrode folder for a given project, data directory, and conversation.

    Args:
        project (str): The name of the project.
        data_dir (str): The directory where the data is stored.
        conversation (str): The name of the conversation.

    Returns:
        str: The path to the electrode folder.
    """
    electrode_folder = ELECTRODE_FOLDER_MAP[project][os.path.basename(data_dir)]
    return os.path.join(data_dir, conversation, electrode_folder)


def validate_flags(flags: FlagValues) -> Tuple[str, str, str]:
    """
    Validates the given flags.

    Args:
        flags (argparse.Namespace): The flags to be validated.

    Raises:
        ValueError: If the project is invalid.
        ValueError: If the subject is invalid.
        ValueError: If the data directory is not found.

    Returns:
        Tuple[str, str, str]: A tuple containing the validated project, subject, and data directory.
    """
    project: str = flags.project
    subject: str = flags.subject
    data_dir: str = flags.data_dir

    if project not in SUBJECTS:
        raise ValueError(f"Invalid project: {project}")

    if subject not in SUBJECTS[project]:
        raise ValueError(f"Invalid subject: {subject}")

    data_dir = os.path.join(data_dir, subject)
    if not os.path.isdir(data_dir):
        raise ValueError(f"Data directory not found: {data_dir}")

    return project, subject, data_dir


def get_datum_name_and_checksum(
    project: str, subject: str, conversation: str
) -> Tuple[str, str]:
    """
    Get the name and checksum of a datum file for a given project, subject, and conversation.

    Args:
        project: The name of the project.
        subject: The name of the subject.
        conversation: The path to the conversation directory.

    Returns:
        A tuple containing the name of the datum file and its checksum.
    """
    datum_file = ""
    datum_checksum = ""

    if os.path.isdir(os.path.join(conversation, "misc")):
        datum_prefix = DATUM_FILE_MAP[project][subject]
    else:
        return datum_file, datum_checksum

    datum_files = glob.glob(os.path.join(conversation, "misc", datum_prefix))

    if len(datum_files) == 1:
        datum_file = datum_files[0]
    else:
        return datum_file, datum_checksum

    datum_checksum = calculate_checksum(datum_file)

    return datum_file, datum_checksum


def main(_):
    """Demonstrates using the protocol buffer API."""
    project, subject, data_dir = validate_flags(FLAGS)

    patient_info = patient_info_pb2.PatientInfo()

    patient = patient_info.patients.add()
    
    if project == "podcast":
        patient.project_type = patient_info_pb2.PODCAST
    else:
        patient.project_type = patient_info_pb2.TFS
    patient.patient_id = subject

    conversations = get_conversations(data_dir)

    for conversation_path in conversations[:2]:
        conversation = patient.conversations.add()
        conversation.name = os.path.basename(conversation_path)

        datum_name, datum_checksum = get_datum_name_and_checksum(
            project, subject, conversation_path
        )
        conversation.datum.name = os.path.basename(datum_name)
        conversation.datum.checksum = datum_checksum

        electrode_folder = get_electrode_folder(project, data_dir, conversation_path)
        electrode_file_list = sorted(
            glob.glob(os.path.join(electrode_folder, "*.mat")),
            key=extract_integer_suffix,
        )
        for electrode_file in electrode_file_list[:2]:
            electrode_checksum = calculate_checksum(electrode_file)

            electrode = conversation.datum.electrodes.add()
            electrode.name = os.path.basename(electrode_file)
            electrode.checksum = electrode_checksum

    # Write the extracted patient info back to disk.
    # out_filename = get_out_filename(project, subject, data_dir)
    out_filename = f"{project}_{subject}.pb"
    with open(out_filename, "wb") as f:
        f.write(patient_info.SerializeToString())

if __name__ == "__main__":
    app.run(main)

import glob
import hashlib
import json
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from absl import app, flags

import data_pb2

EXCLUDE_WORDS = ["sp", "{lg}", "{ns}", "{LG}", "{NS}", "SP"]

NON_WORDS = ["hm", "huh", "mhm", "mm", "oh", "uh", "uhuh", "um"]

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

CONVERSATIONS_MAP = {
    "podcast": dict.fromkeys(
        SUBJECTS["podcast"],
        1,
    ),
    "tfs": dict.fromkeys(["625", "676", "7170", "798"], [54, 78, 24, 15]),
}


FLAGS = flags.FLAGS
flags.DEFINE_string("project", None, "Project ID")
flags.DEFINE_string("subject", None, "Subject ID")
flags.DEFINE_string("data_dir", None, "Data directory")

# Required flag.
flags.mark_flag_as_required("project")
flags.mark_flag_as_required("subject")
flags.mark_flag_as_required("data_dir")


def calculate_checksum(file_path, algorithm="sha256", buffer_size=65536):
    """Calculate checksum of a file."""
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


def create_sample_message(
    my_message: data_pb2.Data, project: str, subject: str, data_dir
) -> data_pb2.Data:
    """
    Creates a sample message by updating the `electrode_checksums` field in `my_message` with new values.

    Args:
        my_message: The original message object.
        project: The project name.
        subject: The subject name.

    Returns:
        The updated message object with the `electrode_checksums` field modified.
    """
    checksums = my_message.outer_map["electrode_checksums"]

    electrode_checksums = get_electrode_checksums(project, data_dir)
    for key, value in electrode_checksums.items():
        middle_entry = checksums.middle_map[key]

        for k, v in value.items():
            inner_entry = middle_entry.inner_map[k]
            inner_entry.inner_value = v

    return my_message


def convert_map_to_dict(data: data_pb2.Data, outer_map) -> Dict[str, Dict[str, str]]:
    """
    Convert a map object to a nested dictionary.

    Args:
        data (Map): The map object to convert.

    Returns:
        dict: The nested dictionary representation of the map object.
    """
    nested_dict: Dict[str, Dict[str, str]] = {}
    for outer_entry in getattr(data, outer_map):
        inner_dict = {
            entry.inner_key: entry.inner_value for entry in outer_entry.inner_map
        }
        nested_dict[outer_entry.outer_key] = inner_dict
    return nested_dict


def get_conversations(data_dir: str) -> List[str]:
    """
    Get a sorted list of conversation names from the given data directory.

    Args:
        data_dir: The path to the data directory.

    Returns:
        A sorted list of conversation names.
    """
    return sorted(glob.glob(os.path.join(data_dir, "*")))[:3]


def get_num_conversations(data_dir: str) -> int:
    """
    Returns the number of conversations in the given data directory.

    Args:
        data_dir (str): The path to the data directory.

    Returns:
        int: The number of conversations.
    """
    conversations = get_conversations(data_dir)
    num_conversations = len(conversations)
    return num_conversations


def get_num_electrodes(data_dir: str, subject: str) -> List[int]:
    """
    Get the number of electrodes for each conversation in the given data directory
    for the specified subject.

    Args:
        data_dir (str): The directory containing the data.
        subject (str): The subject name.

    Returns:
        List[int]: A list of integers representing the number of electrodes for each conversation.
    """
    num_electrodes = []
    conversations = get_conversations(data_dir)
    for conversation in conversations:
        electrode_folder = get_electrode_folder(data_dir, subject, conversation)
        if os.path.isdir(electrode_folder):
            num_electrodes.append(len(os.listdir(electrode_folder)))
    return num_electrodes


def get_datum_checksums(project: str, data_dir: str, subject: str) -> Dict[str, str]:
    """
    Calculates the checksum for each datum file in the given project, data directory, and subject.

    Args:
        project (str): The name of the project.
        data_dir (str): The path to the data directory.
        subject (str): The subject of the datum files.

    Returns:
        dict: A dictionary where the keys are conversation names and the values are the checksums of the corresponding datum files.
    """
    datum_file_dict = {}

    for conversation in get_conversations(data_dir):
        full_path = os.path.join(data_dir, conversation)

        if os.path.isdir(os.path.join(full_path, "misc")):
            datum_prefix = DATUM_FILE_MAP[project][subject]

            datum_files = glob.glob(os.path.join(full_path, "misc", datum_prefix))

            if len(datum_files) == 1:
                datum_file = datum_files[0]

                checksum = calculate_checksum(datum_file)

                datum_file_dict[conversation] = checksum

    return datum_file_dict


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


def get_electrode_list(project: str, data_dir: str) -> Dict[str, List[str]]:
    """
    Get a dictionary containing the list of electrodes for each conversation.

    Args:
        project (str): The project name.
        data_dir (str): The directory where the conversations are stored.

    Returns:
        Dict[str, List[str]]: A dictionary where the keys are conversation names
        and the values are sorted lists of electrode names.
    """
    conversations = get_conversations(data_dir)
    electrode_list = {
        conversation: sorted(
            os.listdir(get_electrode_folder(project, data_dir, conversation)),
            key=extract_integer_suffix,
        )
        for conversation in conversations
    }
    return electrode_list


def get_electrode_count(project: str, data_dir: str) -> int:
    """
    Get the count of electrodes in a project.

    Parameters:
        project (str): The name of the project.
        data_dir (str): The directory where the project data is stored.

    Returns:
        int: The count of electrodes in the project.
    """
    return len(get_electrode_list(project, data_dir))


def get_electrode_checksums(project: str, data_dir: str) -> dict:
    """
    Returns a dictionary containing checksums for each electrode in each conversation.

    Args:
        project (str): The name of the project.
        data_dir (str): The directory where the data is stored.

    Returns:
        dict: A dictionary containing checksums for each electrode in each conversation.
    """
    electrode_checksums = defaultdict(dict)

    for conversation, electrode_list in get_electrode_list(project, data_dir).items():
        for electrode in electrode_list[:4]:
            electrode_folder = get_electrode_folder(project, data_dir, conversation)
            full_electrode_path = os.path.join(electrode_folder, electrode)
            electrode_checksums[conversation][electrode] = calculate_checksum(
                full_electrode_path
            )

    return electrode_checksums


def add_outer_map_entry(
    my_message: data_pb2.Data,
    outer_map: str,
    outer_key: str,
    inner_key: Any,
    inner_value: Any,
) -> None:
    """
    Adds an entry to the outer map of the given message.

    Args:
        my_message (MessageType): The message to modify.
        outer_map (str): The name of the outer map attribute in the message.
        outer_key (Any): The key to use for the outer map entry.
        inner_key (Any): The key to use for the inner map entry.
        inner_value (Any): The value to use for the inner map entry.
    """
    outer_entry = next(
        (
            entry
            for entry in getattr(my_message, outer_map)
            if entry.outer_key == outer_key
        ),
        None,
    )
    if outer_entry is None:
        outer_entry = getattr(my_message, outer_map).add(outer_key=outer_key)
    outer_entry.inner_map.add(inner_key=inner_key, inner_value=inner_value)


def pb_message_to_dict(pb_message) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Convert a protobuf message to a nested dictionary.

    Args:
    pb_message: The protobuf message to convert.

    Returns:
    A nested dictionary representing the protobuf message.
    """
    result_dict = {}

    for outer_key, outer_entry in pb_message.outer_map.items():
        outer_dict = {}

        for middle_key, middle_entry in outer_entry.middle_map.items():
            inner_dict = {}

            for inner_key, inner_entry in middle_entry.inner_map.items():
                inner_dict[inner_key] = inner_entry.inner_value

            outer_dict[middle_key] = inner_dict

        result_dict[outer_key] = outer_dict

    return result_dict


def validate_flags(FLAGS):
    project = FLAGS.project
    subject = FLAGS.subject
    data_dir = FLAGS.data_dir

    if project not in SUBJECTS:
        raise ValueError(f"Invalid project: {project}")

    if subject not in SUBJECTS[project]:
        raise ValueError(f"Invalid subject: {subject}")

    data_dir = os.path.join(data_dir, subject)
    if not os.path.isdir(data_dir):
        raise ValueError(f"Data directory not found: {data_dir}")

    return project, subject, data_dir


def pretty_print_message(message):
    print(json.dumps(pb_message_to_dict(message), indent=2))
    print(json.dumps(convert_map_to_dict(message, "outer_map1"), indent=2))
    print(json.dumps(convert_map_to_dict(message, "outer_map2"), indent=2))


def main(_):
    project, subject, data_dir = validate_flags(FLAGS)

    data = data_pb2.Data()
    data.subject_id = subject

    conversations = get_conversations(data_dir)
    data.num_conversations = len(conversations)

    # Adding conversations
    for idx, conversation in enumerate(conversations):
        add_outer_map_entry(
            data, "outer_map1", "conversations", f"{idx:03}", conversation
        )

    # Adding datum checksums
    for k, v in get_datum_checksums(project, data_dir, subject).items():
        add_outer_map_entry(data, "outer_map1", "datum_checksums", k, v)

    # Adding electrode counts
    for k, v in get_electrode_list(project, data_dir).items():
        add_outer_map_entry(data, "outer_map2", "electrode_counts", k, len(v))

    # Adding electrode checksums
    sample_message = create_sample_message(data, project, subject, data_dir)

    # Print the serialized message
    print("Serialized Message:")
    print(sample_message)

    pretty_print_message(sample_message)


if __name__ == "__main__":
    app.run(main)

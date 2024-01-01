from absl import app
from absl import flags

import patient_info_pb2

FLAGS = flags.FLAGS
flags.DEFINE_string("input_file", None, "Input file to deserialize")
flags.mark_flag_as_required("input_file")


from typing import Any


def list_patient(patient_info: patient_info_pb2.PatientInfo) -> None:
    """
    Print information about patients and their conversations.

    Args:
        patient_info: The patient information.

    Returns:
        None
    """
    for patient in patient_info.patients:

        if patient.project_type == patient_info_pb2.PODCAST:
            project_type = "podcast"
        else:
            project_type = "tfs"

        print("Project:", project_type)
        print("Patient ID:", patient.patient_id)

        for conversation in patient.conversations:
            print("  Folder name:", conversation.name)
            print("    Datum:", conversation.datum.name)
            print("    Checksum:", conversation.datum.checksum)
            for electrode in conversation.datum.electrodes:
                print("      Electrode:", electrode.name)
                print("        Checksum:", electrode.checksum)


def main(_):
    # Reads the patient information from a file and prints the information.
    input_file = FLAGS.input_file
    patient_info = patient_info_pb2.PatientInfo()

    with open(input_file, "rb") as f:
        patient_info.ParseFromString(f.read())

    list_patient(patient_info)


if __name__ == "__main__":
    app.run(main)

from absl import app
from absl import flags

import patientinfo_pb2

FLAGS = flags.FLAGS
flags.DEFINE_string("input_file", None, "Input file to deserialize")
flags.mark_flag_as_required("input_file")


from typing import List, Any

def list_patient(patient_info: Any) -> None:
    """
    Print information about patients and their conversations.

    Args:
        patient_info: The patient information.

    Returns:
        None
    """
    for patient in patient_info.patient:
        print("Project:", patient.project)
        print("Patient ID:", patient.id)
        print("Number of folders:", patient.number_of_folders)
        for conversation in patient.conversation:
            print("  Folder name:", conversation.name)
            print("    Datum:", conversation.datum.name)
            print("    Checksum:", conversation.datum.checksum)
            for electrode in conversation.datum.electrode:
                print("      Electrode:", electrode.name)
                print("        Checksum:", electrode.checksum)


def main(_):
    # Reads the patient information from a file and prints the information.
    input_file = FLAGS.input_file
    patient_info = patientinfo_pb2.PatientInfo()

    with open(input_file, "rb") as f:
        patient_info.ParseFromString(f.read())

    list_patient(patient_info)


if __name__ == "__main__":
    app.run(main)

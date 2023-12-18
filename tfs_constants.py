DATA_DIR = "/projects/HASSON/247/data"
PODCAST_DATA_DIR = DATA_DIR + "/podcast-data"
TFS_DATA_DIR = DATA_DIR + "/conversations-car"

DATA_DIR_MAP = {
    "podcast": PODCAST_DATA_DIR,
    "tfs": TFS_DATA_DIR,
}

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

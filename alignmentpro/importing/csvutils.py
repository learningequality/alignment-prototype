import csv
import json
import os
import requests

from django.conf import settings


# HIGH LEVEL API
################################################################################


def load_curriculum_list(gsheet_id, gid):
    """
    Load the curriculum list from google sheets based on gsheet_id and gid.
    Returns list of dicts for further processing.
    """
    filename = "{}_{}.csv".format(gsheet_id, gid)

    if not os.path.exists(settings.CURRICULUM_DOCS_CSVS_DIR):
        os.makedirs(settings.CURRICULUM_DOCS_CSVS_DIR)
    filepath = os.path.join(settings.CURRICULUM_DOCS_CSVS_DIR, filename)
    csvfilepath = save_gsheet_to_local_csv(gsheet_id, gid, csvfilepath=filepath)
    raw_curriculum_list = load_curriculum_csv(csvfilepath)

    curriculum_list = []
    for row in raw_curriculum_list:
        if row[DEPTH_KEY]:
            row["level"] = len(row[DEPTH_KEY])
            curriculum_list.append(row)
        else:
            print("Skipping row", list(row.values()))
    return curriculum_list


# CURRICULUM SPEADHSEET STRUCTURE v0
################################################################################

DEPTH_KEY = "Depth"
IDENTIFIER_KEY = "Identifier"
KIND_KEY = "Kind"
TITLE_KEY = "Title"
TIME_UNITS_KEY = "Units of time"
NOTES_KEY = "Notes and modification attributes"

SPREADSHEET_HEADER_V0 = [
    DEPTH_KEY,
    IDENTIFIER_KEY,
    KIND_KEY,
    TITLE_KEY,
    TIME_UNITS_KEY,
    NOTES_KEY,
]


KEYS_TO_FIELDS = {
    IDENTIFIER_KEY: "identifier",
    KIND_KEY: "kind",
    TITLE_KEY: "title",
    TIME_UNITS_KEY: "time_units",
    NOTES_KEY: "notes",
}


# CSV CURRICULUM DOC LOADERS
################################################################################


def save_gsheet_to_local_csv(gsheet_id, gid, csvfilepath="curriculum.csv"):
    GSHEETS_BASE = "https://docs.google.com/spreadsheets/d/"
    SHEET_CSV_URL = GSHEETS_BASE + gsheet_id + "/export?format=csv&gid=" + gid
    print(SHEET_CSV_URL)
    response = requests.get(SHEET_CSV_URL)
    response.raise_for_status()
    csv_data = response.content.decode("utf-8")
    with open(csvfilepath, "w") as csvfile:
        csvfile.write(csv_data)
        print("Succesfully saved " + csvfilepath)
    return csvfilepath


def load_curriculum_csv(csvfilepath):
    csv_path = csvfilepath  # download_structure_csv()
    curriculum_list = []
    with open(csv_path, "r") as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=SPREADSHEET_HEADER_V0)
        started = False
        for row in reader:
            if started:
                curriculum_list.append(row)
            else:
                if (
                    row[DEPTH_KEY] == DEPTH_KEY
                    and row[IDENTIFIER_KEY] == IDENTIFIER_KEY
                ):
                    started = True
        return curriculum_list

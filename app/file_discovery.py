import os
import re

RESULTS_ROOT = r"C:\Users\olive\OneDrive\Documents\UNI\MP Enviroment\F1\F1 Premier Data\Results\UK Private Motor"


# Converts DD values extracted from folder names into a standard format.
# Example: "13820" or "138 20" -> "138.20"
def normalise_dd(dd_text):
    digits = re.sub(r"\D", "", dd_text)

    if len(digits) == 5:
        return f"{digits[:3]}.{digits[3:]}"
    return dd_text


def find_all_dd_versions():
    dd_versions = set()

    if not os.path.exists(RESULTS_ROOT):
        return []

    # look through all manually named result folders under UK Private Motor
    for top_folder in os.listdir(RESULTS_ROOT):
        top_path = os.path.join(RESULTS_ROOT, top_folder)

        if not os.path.isdir(top_path):
            continue

        # now look inside at the variant folders
        for inner_folder in os.listdir(top_path):
            inner_path = os.path.join(top_path, inner_folder)

            if not os.path.isdir(inner_path):
                continue

            dd_match = re.search(r"dd\s*(\d+\s*\d+)", inner_folder.lower())
            if dd_match:
                dd_versions.add(normalise_dd(dd_match.group(1)))

    return sorted(dd_versions)


def find_dd_versions(folder_keywords):
    dd_versions = set()

    if not os.path.exists(RESULTS_ROOT):
        return []

    for top_folder in os.listdir(RESULTS_ROOT):
        top_path = os.path.join(RESULTS_ROOT, top_folder)

        if not os.path.isdir(top_path):
            continue

        folder_name = top_folder.lower()

        if not any(word in folder_name for word in folder_keywords):
            continue

        for inner_folder in os.listdir(top_path):
            inner_path = os.path.join(top_path, inner_folder)

            if not os.path.isdir(inner_path):
                continue

            dd_match = re.search(r"dd\s*(\d+\s*\d+)", inner_folder.lower())
            if dd_match:
                dd_versions.add(normalise_dd(dd_match.group(1)))

    return sorted(dd_versions)

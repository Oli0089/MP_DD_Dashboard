import os
import re

RESULTS_ROOT = (
    r"C:\Users\olive\OneDrive\Documents\UNI\MP Enviroment\F1"
    r"\F1 Premier Data\Results\UK Private Motor"
)

BROKER_OUTPUT_FILE = "CDLIHP_BrokerOutputs2.CSV"


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


def find_variants_for_dd(folder_keywords, dd_version):
    found_variants = set()
    best_folder_path = None
    best_score = 0

    if not os.path.exists(RESULTS_ROOT):
        return []

    dd_search = dd_version.replace(".", " ")

    # find the best matching top folder first
    for top_folder in os.listdir(RESULTS_ROOT):
        top_path = os.path.join(RESULTS_ROOT, top_folder)

        if not os.path.isdir(top_path):
            continue

        folder_name = top_folder.lower()

        score = 0
        for word in folder_keywords:
            if word in folder_name:
                score += 1

        if score > best_score:
            best_score = score
            best_folder_path = top_path

    # no matching folder found
    minimum_score = len(folder_keywords)

    if not best_folder_path or best_score < minimum_score:
        return []

    # now look inside the best matching folder for the selected DD
    for inner_folder in os.listdir(best_folder_path):
        inner_path = os.path.join(best_folder_path, inner_folder)

        if not os.path.isdir(inner_path):
            continue

        inner_folder_lower = inner_folder.lower()

        if f"dd{dd_search}" not in inner_folder_lower:
            continue

        if inner_folder_lower.startswith("ca "):
            found_variants.add("CA")
        elif inner_folder_lower.startswith("cv "):
            found_variants.add("CV")
        elif inner_folder_lower.startswith("cx "):
            found_variants.add("CX")

    return sorted(found_variants)


def build_comparison_file_pairs(folder_keywords, previous_dd, latest_dd):
    comparison_pairs = {
        "CA": {"previous": None, "latest": None},
        "CV": {"previous": None, "latest": None},
        "CX": {"previous": None, "latest": None}
    }

    if not os.path.exists(RESULTS_ROOT):
        return comparison_pairs

    best_folder_path = None
    best_score = 0

    # find the best matching top folder
    for top_folder in os.listdir(RESULTS_ROOT):
        top_path = os.path.join(RESULTS_ROOT, top_folder)

        if not os.path.isdir(top_path):
            continue

        folder_name = top_folder.lower()
        score = 0

        for word in folder_keywords:
            if word in folder_name:
                score += 1

        if score > best_score:
            best_score = score
            best_folder_path = top_path

    minimum_score = len(folder_keywords)

    if not best_folder_path or best_score < minimum_score:
        return comparison_pairs

    # look inside the matched folder for previous/latest DD variant folders
    for inner_folder in os.listdir(best_folder_path):
        inner_path = os.path.join(best_folder_path, inner_folder)

        if not os.path.isdir(inner_path):
            continue

        inner_folder_lower = inner_folder.lower()

        variant = None
        if inner_folder_lower.startswith("ca "):
            variant = "CA"
        elif inner_folder_lower.startswith("cv "):
            variant = "CV"
        elif inner_folder_lower.startswith("cx "):
            variant = "CX"

        if not variant:
            continue

        csv_path = os.path.join(inner_path, BROKER_OUTPUT_FILE)

        if not os.path.exists(csv_path):
            continue

        if f"dd{previous_dd.replace('.', ' ')}" in inner_folder_lower:
            comparison_pairs[variant]["previous"] = csv_path

        if f"dd{latest_dd.replace('.', ' ')}" in inner_folder_lower:
            comparison_pairs[variant]["latest"] = csv_path

    return comparison_pairs

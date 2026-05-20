import csv


def read_csv_rows(file_path):
    """
    Read a CSV file into a list of rows.
    Uses latin-1 to avoid decode issues with F1 output files.
    """
    rows = []

    with open(file_path, "r", encoding="latin-1", newline="") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            rows.append(row)

    return rows


def compare_csv_files(previous_file, latest_file):
    """
    Compare two CSV files cell by cell.

    Returns a simple result showing:
    - pass/fail
    - number of differences found
    """
    previous_rows = read_csv_rows(previous_file)
    latest_rows = read_csv_rows(latest_file)

    max_rows = max(len(previous_rows), len(latest_rows))
    differences = []

    for row_index in range(max_rows):
        previous_row = (
            previous_rows[row_index]
            if row_index < len(previous_rows)
            else []
        )

        latest_row = (
            latest_rows[row_index]
            if row_index < len(latest_rows)
            else []
        )

        max_cols = max(len(previous_row), len(latest_row))

        for col_index in range(max_cols):
            previous_value = (
                previous_row[col_index]
                if col_index < len(previous_row)
                else ""
            )

            latest_value = (
                latest_row[col_index]
                if col_index < len(latest_row)
                else ""
            )

            if previous_value != latest_value:
                differences.append(
                    {
                        "row": row_index + 1,
                        "column": col_index + 1,
                        "previous": previous_value,
                        "latest": latest_value,
                    }
                )

        return {
            "passed": len(differences) == 0,
            "difference_count": len(differences),
            "differences": differences,
        }


def compare_swh_variants(comparison_file_pairs):
    """
    Compare all paired files for one SWH transaction.

    Expects input in the format:
    {
        "CA": {"previous": "...", "latest": "..."},
        "CV": {"previous": "...", "latest": "..."},
        "CX": {"previous": None, "latest": "..."}
    }
    """
    variant_results = {}

    for variant, file_pair in comparison_file_pairs.items():
        previous_file = file_pair.get("previous")
        latest_file = file_pair.get("latest")

        if not previous_file or not latest_file:
            variant_results[variant] = {
                "status": "missing",
                "passed": False,
                "difference_count": None,
                "differences": [],
            }
            continue

        compare_result = compare_csv_files(previous_file, latest_file)

        variant_results[variant] = {
            "status": "passed" if compare_result["passed"] else "failed",
            "passed": compare_result["passed"],
            "difference_count": compare_result["difference_count"],
            "differences": compare_result["differences"],
        }

    overall_passed = all(
        result["status"] == "passed"
        for result in variant_results.values()
    )

    return {
        "overall_status": "passed" if overall_passed else "failed",
        "variant_results": variant_results,
    }

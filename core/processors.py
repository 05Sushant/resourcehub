import csv
from io import StringIO


def infer_column_type(values):
    non_empty_values = [
        value for value in values
        if value != ""
    ]

    if not non_empty_values:
        return "string"

    try:
        for value in non_empty_values:
            int(value)
        return "integer"
    except ValueError:
        pass

    try:
        for value in non_empty_values:
            float(value)
        return "float"
    except ValueError:
        return "string"

def profile_csv(csv_content):
    reader = csv.DictReader(StringIO(csv_content))

    if not reader.fieldnames:
        raise ValueError("CSV file must contain headers.")

    rows = list(reader)

    columns_info = []

    for column in reader.fieldnames:
        values = [row[column] for row in rows]

        columns_info.append(
            {
                "name": column,
                "type": infer_column_type(values),
            }
        )

    return {
        "rows": len(rows),
        "columns": len(reader.fieldnames),
        "columns_info": columns_info,
    }

def execute_operation(operation, input_file, parameters):
    if operation == "PROFILE":
        return profile_csv(input_file)

    raise ValueError(
        f"Operation is not implemented: {operation}"
    )

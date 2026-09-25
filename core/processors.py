import csv
from io import BytesIO, StringIO

from PIL import Image


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


def resize_image(image_bytes, width, height):
    """Resize *image_bytes* to (width x height) and return PNG bytes."""
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError("width and height must be integers.")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive integers.")

    with Image.open(BytesIO(image_bytes)) as img:
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        output = BytesIO()
        resized.save(output, format="PNG")
        return output.getvalue()


def execute_operation(operation, input_file, parameters):
    if operation == "PROFILE":
        return profile_csv(input_file)

    if operation == "RESIZE":
        width = parameters.get("width")
        height = parameters.get("height")
        return resize_image(input_file, width, height)

    raise ValueError(
        f"Operation is not implemented: {operation}"
    )

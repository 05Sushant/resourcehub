from io import BytesIO
import pandas as pd

from core.schemas import (
    CSVAnalysis,
    CSVProfile,
    CSVValidationResult,
    ColumnAnalysis,
    ColumnProfile,
    NumericStatistics,
    ValidationError,
)

from PIL import Image


def infer_column_type(series):
    non_missing = series.dropna()

    if non_missing.empty:
        return "string"

    numeric_values = pd.to_numeric(
        non_missing,
        errors="coerce",
    )

    numeric_count = int(numeric_values.notna().sum())
    total_count = len(non_missing)

    numeric_ratio = numeric_count / total_count

    if numeric_ratio <= 0.5:
        return "string"

    valid_numeric_values = numeric_values.dropna()

    if (valid_numeric_values % 1 == 0).all():
        return "integer"

    return "float"

def profile_csv(csv_content):
    from io import StringIO

    df = pd.read_csv(StringIO(csv_content))

    if df.columns.empty:
        raise ValueError("CSV file must contain headers.")

    columns_info = []

    for column in df.columns:
        series = df[column]

        column_type = infer_column_type(series)

        missing_count = int(series.isna().sum())

        non_missing = series.dropna()

        converted = pd.to_numeric(
            non_missing,
            errors="coerce",
        )

        if column_type in ("integer", "float"):
            unknown_count = int(converted.isna().sum())
        else:
            unknown_count = 0

        unique_count = int(
            series.nunique(dropna=True)
        )

        columns_info.append(
            ColumnProfile(
                name=column,
                type=column_type,
                missing=missing_count,
                unknown=unknown_count,
                unique=unique_count,
            )
        )

    result = CSVProfile(
        rows=len(df),
        columns=len(df.columns),
        columns_info=columns_info,
    )

    return result.model_dump()

def analyze_csv(csv_content):
    from io import StringIO

    df = pd.read_csv(StringIO(csv_content))

    if df.columns.empty:
        raise ValueError("CSV file must contain headers.")

    columns_info = []

    for column in df.columns:
        series = df[column]

        column_type = infer_column_type(series)

        missing_count = int(series.isna().sum())

        non_missing = series.dropna()

        converted = pd.to_numeric(
            non_missing,
            errors="coerce",
        )

        if column_type in ("integer", "float"):
            unknown_count = int(converted.isna().sum())
        else:
            unknown_count = 0

        unique_count = int(
            series.nunique(dropna=True)
        )

        statistics = None

        if column_type in ("integer", "float"):
            valid_numeric = converted.dropna()

            if not valid_numeric.empty:
                statistics = NumericStatistics(
                    min=float(valid_numeric.min()),
                    max=float(valid_numeric.max()),
                    mean=float(valid_numeric.mean()),
                )

        columns_info.append(
            ColumnAnalysis(
                name=column,
                type=column_type,
                missing=missing_count,
                unknown=unknown_count,
                unique=unique_count,
                statistics=statistics,
            )
        )

    result = CSVAnalysis(
        rows=len(df),
        columns=len(df.columns),
        columns_info=columns_info,
    )

    return result.model_dump()

def validate_csv(csv_content, expected_schema):
    from io import StringIO

    expected_schema = expected_schema["columns"]

    df = pd.read_csv(StringIO(csv_content))

    if df.columns.empty:
        raise ValueError("CSV file must contain headers.")

    errors = []

    expected_columns = set(expected_schema.keys())
    actual_columns = set(df.columns)

    # Check for missing expected columns.
    for column in expected_columns - actual_columns:
        errors.append(
            ValidationError(
                column=column,
                message="Expected column is missing.",
            )
        )

    # Check for unexpected extra columns.
    for column in actual_columns - expected_columns:
        errors.append(
            ValidationError(
                column=column,
                message="Unexpected column.",
            )
        )

    # Validate values in columns that exist in both schemas.
    for column, expected_type in expected_schema.items():

        if column not in df.columns:
            continue

        series = df[column]

        if expected_type == "string":
            for index, value in series.items():

                if pd.isna(value):
                    continue

                if not isinstance(value, str):
                    errors.append(
                        ValidationError(
                            column=column,
                            row=index + 2,
                            message="Expected string.",
                        )
                    )

            continue

        if expected_type not in ("integer", "float"):
            errors.append(
                ValidationError(
                    column=column,
                    message=f"Unsupported expected type: {expected_type}.",
                )
            )
            continue

        for index, value in series.items():

            # Missing numeric value.
            if pd.isna(value):
                errors.append(
                    ValidationError(
                        column=column,
                        row=index + 2,
                        message=f"Expected {expected_type}, but value is missing.",
                    )
                )
                continue

            numeric_value = pd.to_numeric(
                value,
                errors="coerce",
            )

            # Non-numeric value.
            if pd.isna(numeric_value):
                errors.append(
                    ValidationError(
                        column=column,
                        row=index + 2,
                        message=f"Expected {expected_type}.",
                    )
                )
                continue

            # Integer columns cannot contain decimal values.
            if (
                expected_type == "integer"
                and numeric_value % 1 != 0
            ):
                errors.append(
                    ValidationError(
                        column=column,
                        row=index + 2,
                        message="Expected integer.",
                    )
                )

    result = CSVValidationResult(
        valid=len(errors) == 0,
        errors=errors,
    )

    return result.model_dump()


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

def grayscale_image(image_bytes):
    from io import BytesIO

    try:
        image = Image.open(BytesIO(image_bytes))
    except Exception as exc:
        raise ValueError("Invalid image file.") from exc

    grayscale = image.convert("L")

    output = BytesIO()
    grayscale.save(output, format="PNG")

    return output.getvalue()

def execute_operation(operation, input_data, parameters):
    from core.operations import get_operation

    operation_config = get_operation(operation)

    processor = operation_config["processor"]

    if operation == "RESIZE":
        return processor(
            input_data,
            parameters["width"],
            parameters["height"],
        )

    if operation == "VALIDATE":
        return processor(
            input_data,
            parameters,
        )

    return processor(input_data)

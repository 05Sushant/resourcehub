from core.processors import (
    analyze_csv,
    grayscale_image,
    profile_csv,
    resize_image,
    validate_csv,
)


OPERATIONS = {
    "PROFILE": {
        "resource_type": "CSV_ANALYTICS",
        "processor": profile_csv,
        "input_type": "text",
    },
    "ANALYZE": {
        "resource_type": "CSV_ANALYTICS",
        "processor": analyze_csv,
        "input_type": "text",
    },
    "VALIDATE": {
        "resource_type": "CSV_ANALYTICS",
        "processor": validate_csv,
        "input_type": "text",
    },
    "RESIZE": {
        "resource_type": "IMAGE_PROCESSING",
        "processor": resize_image,
        "input_type": "binary",
    },
    "GRAYSCALE": {
        "resource_type": "IMAGE_PROCESSING",
        "processor": grayscale_image,
        "input_type": "binary",
    },
}

def get_operation(operation):
    try:
        return OPERATIONS[operation]
    except KeyError:
        raise ValueError(
            f"Unknown operation: {operation}"
        )


def validate_operation(resource_type, operation):
    operation_config = OPERATIONS.get(operation)

    if operation_config is None:
        return False

    return operation_config["resource_type"] == resource_type
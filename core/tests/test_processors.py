from django.test import SimpleTestCase

from core.processors import (
    analyze_csv,
    execute_operation,
    profile_csv,
    resize_image,
    grayscale_image,
    validate_csv,
)

class CSVProfileTest(SimpleTestCase):

    def test_profile_csv_returns_dataset_structure(self):
        csv_content = (
            "name,age,salary\n"
            "Alice,25,50000\n"
            "Bob,30,60000\n"
        )

        result = profile_csv(csv_content)

        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["columns"], 3)

        self.assertEqual(
            result["columns_info"],
            [
                {
                    "name": "name",
                    "type": "string",
                    "missing": 0,
                    "unknown": 0,
                    "unique": 2,
                },
                {
                    "name": "age",
                    "type": "integer",
                    "missing": 0,
                    "unknown": 0,
                    "unique": 2,
                },
                {
                    "name": "salary",
                    "type": "integer",
                    "missing": 0,
                    "unknown": 0,
                    "unique": 2,
                },
            ],
        )

    def test_profile_csv_handles_empty_dataset(self):
        csv_content = "name,age\n"

        result = profile_csv(csv_content)

        self.assertEqual(result["rows"], 0)
        self.assertEqual(result["columns"], 2)

    def test_profile_csv_rejects_csv_without_headers(self):
        csv_content = ""

        with self.assertRaises(ValueError):
            profile_csv(csv_content)

    def test_profile_csv_detects_decimal_and_negative_numbers(self):
        csv_content = (
            "temperature,balance\n"
            "-12.5,-500\n"
            "25.75,1000\n"
        )

        result = profile_csv(csv_content)

        self.assertEqual(
            result["columns_info"],
            [
                {
                    "name": "temperature",
                    "type": "float",
                    "missing": 0,
                    "unknown": 0,
                    "unique": 2,
                },
                {
                    "name": "balance",
                    "type": "integer",
                    "missing": 0,
                    "unknown": 0,
                    "unique": 2,
                },
            ],
        )

    def test_profile_csv_ignores_empty_values_when_inferring_type(self):
        csv_content = (
            "name,age,salary\n"
            "Alice,25,50000\n"
            "Bob,,60000\n"
            "Charlie,30,\n"
        )

        result = profile_csv(csv_content)

        self.assertEqual(
            result["columns_info"],
            [
                {
                    "name": "name",
                    "type": "string",
                    "missing": 0,
                    "unknown": 0,
                    "unique": 3,
                },
                {
                    "name": "age",
                    "type": "integer",
                    "missing": 1,
                    "unknown": 0,
                    "unique": 2,
                },
                {
                    "name": "salary",
                    "type": "integer",
                    "missing": 1,
                    "unknown": 0,
                    "unique": 2,
                },
            ],
        )

    def test_profile_csv_treats_all_empty_column_as_string(self):
        csv_content = (
            "name,notes\n"
            "Alice,\n"
            "Bob,\n"
        )

        result = profile_csv(csv_content)

        self.assertEqual(
            result["columns_info"],
            [
                {
                    "name": "name",
                    "type": "string",
                    "missing": 0,
                    "unknown": 0,
                    "unique": 2,
                },
                {
                    "name": "notes",
                    "type": "string",
                    "missing": 2,
                    "unknown": 0,
                    "unique": 0,
                },
            ],
        )

    def test_execute_operation_runs_profile(self):
        csv_content = (
            "name,age\n"
            "Alice,25\n"
            "Bob,30\n"
        )

        result = execute_operation(
            "PROFILE",
            csv_content,
            {},
        )

        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["columns"], 2)

    def test_profile_csv_preserves_numeric_type_with_unknown_values(self):
        csv_content = (
            "age\n"
            "21\n"
            "22\n"
            "unknown\n"
            "23\n"
            "24\n"
        )

        result = profile_csv(csv_content)

        self.assertEqual(
            result["columns_info"],
            [
                {
                    "name": "age",
                    "type": "integer",
                    "missing": 0,
                    "unknown": 1,
                    "unique": 5,
                },
            ],
        )


    def test_profile_csv_treats_column_as_string_when_numeric_values_do_not_dominate(
        self,
    ):
        csv_content = (
            "value\n"
            "21\n"
            "hello\n"
            "world\n"
        )

        result = profile_csv(csv_content)

        self.assertEqual(
            result["columns_info"],
            [
                {
                    "name": "value",
                    "type": "string",
                    "missing": 0,
                    "unknown": 0,
                    "unique": 3,
                },
            ],
        )

    def test_analyze_csv_returns_numeric_statistics(self):
        csv_content = (
            "name,age,salary\n"
            "Alice,25,50000\n"
            "Bob,30,60000\n"
            "Charlie,35,70000\n"
        )

        result = analyze_csv(csv_content)

        self.assertEqual(result["rows"], 3)
        self.assertEqual(result["columns"], 3)

        self.assertEqual(
            result["columns_info"][0],
            {
                "name": "name",
                "type": "string",
                "missing": 0,
                "unknown": 0,
                "unique": 3,
                "statistics": None,
            },
        )

        self.assertEqual(
            result["columns_info"][1],
            {
                "name": "age",
                "type": "integer",
                "missing": 0,
                "unknown": 0,
                "unique": 3,
                "statistics": {
                    "min": 25.0,
                    "max": 35.0,
                    "mean": 30.0,
                },
            },
        )

    def test_analyze_csv_ignores_unknown_numeric_values(self):
        csv_content = (
            "age\n"
            "20\n"
            "unknown\n"
            "30\n"
            "40\n"
        )

        result = analyze_csv(csv_content)

        self.assertEqual(
            result["columns_info"][0],
            {
                "name": "age",
                "type": "integer",
                "missing": 0,
                "unknown": 1,
                "unique": 4,
                "statistics": {
                    "min": 20.0,
                    "max": 40.0,
                    "mean": 30.0,
                },
            },
        )

    def test_execute_operation_runs_analyze(self):
        csv_content = (
            "age\n"
            "20\n"
            "30\n"
        )

        result = execute_operation(
            "ANALYZE",
            csv_content,
            {},
        )

        self.assertEqual(result["rows"], 2)
        self.assertEqual(
            result["columns_info"][0]["statistics"]["mean"],
            25.0,
        )

    def test_validate_csv_accepts_valid_data(self):
        csv_content = (
            "name,age,salary\n"
            "Alice,25,50000.5\n"
            "Bob,30,60000.0\n"
        )

        result = validate_csv(
            csv_content,
            {
                "columns": {
                    "name": "string",
                    "age": "integer",
                    "salary": "float",
                }
            },
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_validate_csv_rejects_invalid_integer(self):
        csv_content = (
            "name,age\n"
            "Alice,25\n"
            "Bob,unknown\n"
        )

        result = validate_csv(
            csv_content,
            {
                "columns": {
                    "name": "string",
                    "age": "integer",
                }
            },
        )

        self.assertFalse(result["valid"])

        self.assertEqual(
            result["errors"],
            [
                {
                    "column": "age",
                    "row": 3,
                    "message": "Expected integer.",
                }
            ],
        )

    def test_validate_csv_rejects_missing_numeric_value(self):
        csv_content = (
            "name,age\n"
            "Alice,25\n"
            "Bob,\n"
        )

        result = validate_csv(
            csv_content,
            {
                "columns": {
                    "name": "string",
                    "age": "integer",
                }
            },
        )

        self.assertFalse(result["valid"])

        self.assertEqual(
            result["errors"],
            [
                {
                    "column": "age",
                    "row": 3,
                    "message": "Expected integer, but value is missing.",
                }
            ],
        )

    def test_validate_csv_rejects_decimal_for_integer(self):
        csv_content = (
            "age\n"
            "25\n"
            "25.5\n"
        )

        result = validate_csv(
            csv_content,
            {
                "columns": {
                    "age": "integer",
                }
            },
        )

        self.assertFalse(result["valid"])

        self.assertEqual(
            result["errors"],
            [
                {
                    "column": "age",
                    "row": 3,
                    "message": "Expected integer.",
                }
            ],
        )

    def test_validate_csv_rejects_missing_column(self):
        csv_content = (
            "name,age\n"
            "Alice,25\n"
        )

        result = validate_csv(
            csv_content,
            {
                "columns": {
                    "name": "string",
                    "age": "integer",
                    "salary": "float",
                }
            },
        )

        self.assertFalse(result["valid"])

        self.assertEqual(
            result["errors"],
            [
                {
                    "column": "salary",
                    "row": None,
                    "message": "Expected column is missing.",
                }
            ],
        )

    def test_validate_csv_rejects_extra_column(self):
        csv_content = (
            "name,age,email\n"
            "Alice,25,a@example.com\n"
        )

        result = validate_csv(
            csv_content,
            {
                "columns": {
                    "name": "string",
                    "age": "integer",
                }
            },
        )

        self.assertFalse(result["valid"])

        self.assertEqual(
            result["errors"],
            [
                {
                    "column": "email",
                    "row": None,
                    "message": "Unexpected column.",
                }
            ],
        )

    def test_execute_operation_runs_validate(self):
        csv_content = (
            "name,age\n"
            "Alice,25\n"
            "Bob,30\n"
        )

        result = execute_operation(
            "VALIDATE",
            csv_content,
            {
                "columns": {
                    "name": "string",
                    "age": "integer",
                }
            },
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_png_bytes(width=100, height=80):
    """Create a minimal solid-colour PNG in memory and return its bytes."""
    from io import BytesIO
    from PIL import Image

    img = Image.new("RGB", (width, height), color=(255, 0, 0))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# IMAGE_PROCESSING → RESIZE processor tests
# ---------------------------------------------------------------------------

class ImageResizeProcessorTest(SimpleTestCase):

    def setUp(self):
        self.png_bytes = _make_png_bytes(width=100, height=80)

    # --- resize_image() ---

    def test_resize_image_returns_bytes(self):
        result = resize_image(self.png_bytes, 50, 40)
        self.assertIsInstance(result, bytes)

    def test_resize_image_produces_correct_dimensions(self):
        from io import BytesIO
        from PIL import Image

        result = resize_image(self.png_bytes, 50, 40)
        img = Image.open(BytesIO(result))
        self.assertEqual(img.size, (50, 40))

    def test_resize_image_rejects_zero_width(self):
        with self.assertRaises(ValueError):
            resize_image(self.png_bytes, 0, 40)

    def test_resize_image_rejects_zero_height(self):
        with self.assertRaises(ValueError):
            resize_image(self.png_bytes, 50, 0)

    def test_resize_image_rejects_negative_dimension(self):
        with self.assertRaises(ValueError):
            resize_image(self.png_bytes, -10, 40)

    def test_resize_image_rejects_non_integer_dimensions(self):
        with self.assertRaises(ValueError):
            resize_image(self.png_bytes, "50", 40)

    # --- execute_operation() dispatch ---

    def test_execute_operation_dispatches_resize(self):
        result = execute_operation(
            "RESIZE",
            self.png_bytes,
            {"width": 30, "height": 20},
        )
        self.assertIsInstance(result, bytes)

    def test_execute_operation_resize_correct_output_size(self):
        from io import BytesIO
        from PIL import Image

        result = execute_operation(
            "RESIZE",
            self.png_bytes,
            {"width": 30, "height": 20},
        )
        img = Image.open(BytesIO(result))
        self.assertEqual(img.size, (30, 20))

    def test_execute_operation_unknown_raises_value_error(self):
        with self.assertRaises(ValueError):
            execute_operation("UNKNOWN_OP", self.png_bytes, {})

    def test_grayscale_image_returns_bytes(self):
        result = grayscale_image(self.png_bytes)

        self.assertIsInstance(result, bytes)

    def test_grayscale_image_preserves_dimensions(self):
        from io import BytesIO
        from PIL import Image

        result = grayscale_image(self.png_bytes)

        img = Image.open(BytesIO(result))

        self.assertEqual(img.size, (100, 80))

    def test_grayscale_image_produces_grayscale_image(self):
        from io import BytesIO
        from PIL import Image

        result = grayscale_image(self.png_bytes)

        img = Image.open(BytesIO(result))

        self.assertEqual(img.mode, "L")

    def test_grayscale_image_rejects_invalid_image(self):
        with self.assertRaises(ValueError):
            grayscale_image(b"not an image")

    def test_execute_operation_dispatches_grayscale(self):
        result = execute_operation(
            "GRAYSCALE",
            self.png_bytes,
            {},
        )

        self.assertIsInstance(result, bytes)

    def test_execute_operation_grayscale_produces_grayscale_image(self):
        from io import BytesIO
        from PIL import Image

        result = execute_operation(
            "GRAYSCALE",
            self.png_bytes,
            {},
        )

        img = Image.open(BytesIO(result))

        self.assertEqual(img.mode, "L")

    def test_execute_operation_unknown_raises_value_error(self):
        with self.assertRaises(ValueError):
            execute_operation("UNKNOWN_OP", self.png_bytes, {})
from django.test import SimpleTestCase

from core.processors import execute_operation, profile_csv, resize_image

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
                {"name": "name", "type": "string"},
                {"name": "age", "type": "integer"},
                {"name": "salary", "type": "integer"},
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
                {"name": "temperature", "type": "float"},
                {"name": "balance", "type": "integer"},
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
                {"name": "name", "type": "string"},
                {"name": "age", "type": "integer"},
                {"name": "salary", "type": "integer"},
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
                {"name": "name", "type": "string"},
                {"name": "notes", "type": "string"},
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

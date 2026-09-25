from django.test import SimpleTestCase

from core.processors import execute_operation, profile_csv

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

from django.test import TestCase

from core.services import validate_operation


class OperationValidationTest(TestCase):

    def test_analyze_is_supported_for_csv_analytics(self):
        self.assertTrue(
            validate_operation("CSV_ANALYTICS", "ANALYZE")
        )

    def test_validate_is_supported_for_csv_analytics(self):
        self.assertTrue(
            validate_operation("CSV_ANALYTICS", "VALIDATE")
        )

    def test_profile_is_supported_for_csv_analytics(self):
        self.assertTrue(
            validate_operation("CSV_ANALYTICS", "PROFILE")
        )

    def test_resize_is_supported_for_image_processing(self):
        self.assertTrue(
            validate_operation("IMAGE_PROCESSING", "RESIZE")
        )

    def test_grayscale_is_supported_for_image_processing(self):
        self.assertTrue(
            validate_operation("IMAGE_PROCESSING", "GRAYSCALE")
        )

    def test_grayscale_is_not_supported_for_csv_analytics(self):
        self.assertFalse(
            validate_operation("CSV_ANALYTICS", "GRAYSCALE")
        )

    def test_analyze_is_not_supported_for_image_processing(self):
        self.assertFalse(
            validate_operation("IMAGE_PROCESSING", "ANALYZE")
        )

    def test_unknown_operation_is_not_supported(self):
        self.assertFalse(
            validate_operation("CSV_ANALYTICS", "UNKNOWN")
        )
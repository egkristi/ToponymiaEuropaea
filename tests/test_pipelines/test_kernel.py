"""Tests for the gold-standard kernel validation."""

from toponymia.pipelines.kernel import (
    KernelValidationResult,
    validate_kernel,
)


class TestKernelValidation:
    def test_gold_file_validates(self):
        """All gold-standard records must pass validation."""
        result = validate_kernel()
        assert result.is_valid, f"Kernel errors: {result.errors}"

    def test_gold_file_has_records(self):
        """Kernel must have at least one record."""
        result = validate_kernel()
        assert result.total_records > 0

    def test_result_counts_match(self):
        result = validate_kernel()
        assert result.total_records == result.valid_records

    def test_returns_validation_result(self):
        result = validate_kernel()
        assert isinstance(result, KernelValidationResult)

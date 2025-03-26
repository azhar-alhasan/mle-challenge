import unittest
from unittest.mock import MagicMock, patch
from pii_redactor.service.service import PIIRedactorService


class TestPIIRedactorService(unittest.TestCase):
    """Test the PII redactor service."""

    def setUp(self):
        # Create a mock PIIModel
        with patch("pii_redactor.service.service.PIIModel") as mock_model_class:
            # Configure the mock
            self.mock_model = MagicMock()
            mock_model_class.return_value = self.mock_model

            # Create service with the mock model
            self.service = PIIRedactorService("dummy_path")

    def test_redact(self):
        """Test redacting a single text."""
        text = "Please contact John Smith at john.smith@example.com."
        expected_redacted = "Please contact [NAME] at [EMAIL]."

        # Configure the mock
        self.mock_model.redact_text.return_value = expected_redacted

        # Call the service
        redacted_text = self.service.redact(text)

        # Verify the result
        self.assertEqual(redacted_text, expected_redacted)

        # Verify the mock was called correctly
        self.mock_model.redact_text.assert_called_once_with(text)

    def test_redact_batch(self):
        """Test redacting a batch of texts."""
        texts = [
            "Please contact John Smith at john.smith@example.com.",
            "My name is Jane Doe and I work for Google.",
        ]

        expected_redacted = [
            "Please contact [NAME] at [EMAIL].",
            "My name is [NAME] and I work for [ORGANIZATION].",
        ]

        # Configure the mock to return different values for different inputs
        self.mock_model.redact_text.side_effect = expected_redacted

        # Call the service
        redacted_texts = self.service.redact_batch(texts)

        # Verify the result
        self.assertEqual(redacted_texts, expected_redacted)

        # Verify the mock was called correctly
        self.assertEqual(self.mock_model.redact_text.call_count, 2)
        self.mock_model.redact_text.assert_any_call(texts[0])
        self.mock_model.redact_text.assert_any_call(texts[1])

    def test_error_handling(self):
        """Test error handling in the service."""
        text = "Test text"

        # Configure the mock to raise an exception
        self.mock_model.redact_text.side_effect = Exception("Test error")

        # Check that the exception is propagated
        with self.assertRaises(Exception):
            self.service.redact(text)

        # Also check batch processing
        with self.assertRaises(Exception):
            self.service.redact_batch([text])


if __name__ == "__main__":
    unittest.main()

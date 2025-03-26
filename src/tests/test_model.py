import unittest
import os
import tempfile
from pii_redactor.model.model import PIIModel


class TestPIIModel(unittest.TestCase):
    """Test the PII model."""

    def setUp(self):
        # Initialize a blank model
        self.model = PIIModel()

    def test_predict(self):
        """Test predicting entities."""
        text = (
            "Please contact John Smith at john.smith@example.com or call 0412 345 678."
        )

        entities = self.model.predict(text)

        # We should find at least one entity
        self.assertGreater(len(entities), 0)

        # Check entity types
        entity_types = [entity[3] for entity in entities]
        self.assertIn("EMAIL", entity_types)
        self.assertIn("PHONE_NUMBER", entity_types)

    def test_redact_text(self):
        """Test redacting text."""
        text = "Please contact John Smith at john.smith@example.com."

        redacted_text = self.model.redact_text(text)

        # The redacted text should contain placeholders
        self.assertIn("[", redacted_text)
        self.assertIn("]", redacted_text)

        # The redacted text should not contain the original entities
        self.assertNotIn("john.smith@example.com", redacted_text)

        # The non-PII text should be preserved
        self.assertIn("Please contact", redacted_text)

    def test_create_config(self):
        """Test creating a config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.cfg")

            # Create config
            result_path = self.model.create_config(config_path)

            # Check that the file exists
            self.assertTrue(os.path.exists(result_path))

            # Check that the file has content
            with open(result_path, "r") as f:
                content = f.read()
                self.assertGreater(len(content), 0)


if __name__ == "__main__":
    unittest.main()

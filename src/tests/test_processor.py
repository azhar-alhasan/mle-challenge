import unittest
import os
import json
import tempfile
from pii_redactor.data.processor import PIIDataProcessor


class TestPIIDataProcessor(unittest.TestCase):
    """Test the PII data processor."""

    def setUp(self):
        # Create a temporary test data file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_data_path = os.path.join(self.temp_dir.name, "test_data.json")
        self.test_data = [
            {
                "text": "Please contact John Smith at john.smith@example.com or 0412 345 678.",
                "redacted_text": "Please contact [NAME] at [EMAIL] or [PHONE_NUMBER].",
            },
            {
                "text": "I work at Google in Sydney.",
                "redacted_text": "I work at [ORGANIZATION] in Sydney.",
            },
        ]

        with open(self.test_data_path, "w") as f:
            json.dump(self.test_data, f)

        self.processor = PIIDataProcessor(self.test_data_path)

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_load_data(self):
        """Test loading data from a JSON file."""
        data = self.processor.load_data()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["text"], self.test_data[0]["text"])
        self.assertEqual(data[1]["redacted_text"], self.test_data[1]["redacted_text"])

    def test_find_entities_from_redacted(self):
        """Test finding entities from redacted text."""
        text = "Please contact John Smith at john.smith@example.com."
        redacted_text = "Please contact [NAME] at [EMAIL]."

        entities = self.processor.find_entities_from_redacted(text, redacted_text)

        # We should find at least one entity
        self.assertGreater(len(entities), 0)

        # Check entity labels
        entity_labels = [entity[2] for entity in entities]
        self.assertIn("NAME", entity_labels)
        self.assertIn("EMAIL", entity_labels)

    def test_create_training_data(self):
        """Test creating training data."""
        data = self.processor.load_data()
        training_data = self.processor.create_training_data(data)

        # We should have the same number of training examples as input data points
        self.assertEqual(len(training_data), len(data))

        # Each training example should be a tuple of (text, annotations)
        self.assertIsInstance(training_data[0], tuple)
        self.assertEqual(len(training_data[0]), 2)

        # The annotations should contain entities
        self.assertIn("entities", training_data[0][1])

        # There should be at least one entity in the annotations
        self.assertGreater(len(training_data[0][1]["entities"]), 0)


if __name__ == "__main__":
    unittest.main()

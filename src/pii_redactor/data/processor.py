import json
import re
import difflib
from typing import List, Dict, Any, Tuple
from sklearn.model_selection import train_test_split
import spacy
from spacy.tokens import DocBin
from spacy.training import Example

from ..config.config import PII_CATEGORIES
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PIIDataProcessor:
    """Class to process PII data for training."""

    def __init__(self, data_path: str):
        """
        Initialize the PIIDataProcessor.

        Args:
            data_path (str): Path to the JSON data file
        """
        self.data_path = data_path
        logger.info(f"Initialized PIIDataProcessor with data path: {data_path}")

    def load_data(self) -> List[Dict[str, str]]:
        """
        Load data from JSON file.

        Returns:
            List[Dict[str, str]]: List of data points with text and redacted_text
        """
        try:
            with open(self.data_path, "r") as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} data points from {self.data_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def find_entities_from_redacted(
        self, text: str, redacted_text: str
    ) -> List[Tuple[int, int, str]]:
        """
        Find entities by comparing original and redacted text.

        Args:
            text (str): Original text
            redacted_text (str): Redacted text with placeholders

        Returns:
            List[Tuple[int, int, str]]: List of (start, end, label) tuples
        """
        entities = []

        # Find placeholders in redacted text
        placeholder_positions = []
        for category in PII_CATEGORIES:
            pattern = f"\\[{category}\\]"
            for match in re.finditer(pattern, redacted_text):
                start, end = match.span()
                placeholder_positions.append((start, end, category))

        # Sort placeholders by position
        placeholder_positions.sort(key=lambda x: x[0])

        if not placeholder_positions:
            return entities

        # Align original and redacted text to find corresponding positions
        s = difflib.SequenceMatcher(None, redacted_text, text)

        # Get matching blocks
        matching_blocks = s.get_matching_blocks()

        # Map redacted positions to original text positions
        for p_start, p_end, category in placeholder_positions:
            # Find the corresponding position in original text
            orig_start = None
            orig_end = None

            # Find closest matching blocks before and after the placeholder
            before_block = None
            after_block = None

            for i, (r_pos, t_pos, length) in enumerate(matching_blocks):
                if r_pos <= p_start:
                    before_block = (r_pos, t_pos, length)
                if r_pos >= p_end and not after_block:
                    after_block = (r_pos, t_pos, length)
                    break

            if before_block and after_block:
                r_before, t_before, l_before = before_block
                r_after, t_after, l_after = after_block

                # Calculate the offset from the start of the placeholder to the closest match before
                offset_before = p_start - (r_before + l_before)

                # Calculate the position in original text
                orig_start = t_before + l_before + offset_before

                # Calculate the length of the placeholder
                placeholder_length = p_end - p_start

                # Calculate the length of the entity in original text
                entity_length = (t_after - (t_before + l_before)) - offset_before

                orig_end = orig_start + entity_length

                # Only add if we have valid positions
                if orig_start >= 0 and orig_end <= len(text) and orig_start < orig_end:
                    entities.append((orig_start, orig_end, category))

        logger.debug(f"Found {len(entities)} entities in text")
        return entities

    def create_training_data(
        self, data: List[Dict[str, str]]
    ) -> List[Tuple[str, Dict[str, List[Tuple[int, int, str]]]]]:
        """
        Convert data to spaCy training format.

        Args:
            data (List[Dict[str, str]]): List of data points with text and redacted_text

        Returns:
            List[Tuple[str, Dict[str, List[Tuple[int, int, str]]]]]: Training data in spaCy format
        """
        training_data = []

        for item in data:
            text = item["text"]
            redacted_text = item["redacted_text"]

            # Find entities by comparing original and redacted text
            entities = self.find_entities_from_redacted(text, redacted_text)

            # Use regex patterns for specific entity types as fallback
            if not entities:
                entities = []

                # Email pattern
                for match in re.finditer(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text
                ):
                    start, end = match.span()
                    entities.append((start, end, "EMAIL"))

                # Phone number pattern
                for match in re.finditer(
                    r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{4}\s?\d{3}\s?\d{3}\b",
                    text,
                ):
                    start, end = match.span()
                    entities.append((start, end, "PHONE_NUMBER"))

            training_data.append((text, {"entities": entities}))

        logger.info(f"Created {len(training_data)} training examples")
        return training_data

    def prepare_spacy_data(
        self, training_data: List[Tuple[str, Dict[str, List[Tuple[int, int, str]]]]]
    ) -> Tuple[DocBin, DocBin]:
        """
        Prepare data for spaCy training.

        Args:
            training_data (List[Tuple[str, Dict[str, List[Tuple[int, int, str]]]]]): Training data

        Returns:
            Tuple[DocBin, DocBin]: DocBin objects for training and testing
        """
        nlp = spacy.blank("en")

        # Create Example objects
        examples = []
        for text, annotations in training_data:
            doc = nlp.make_doc(text)
            ents = []
            for start, end, label in annotations["entities"]:
                span = doc.char_span(start, end, label=label)
                if span is not None:
                    ents.append(span)
            doc.ents = ents
            examples.append(Example.from_dict(doc, annotations))

        # Split into train and test
        train_examples, test_examples = train_test_split(
            examples, test_size=0.2, random_state=42
        )

        # Convert to DocBin
        train_db = DocBin()
        for example in train_examples:
            train_db.add(example.reference)

        test_db = DocBin()
        for example in test_examples:
            test_db.add(example.reference)

        logger.info(
            f"Prepared {len(train_examples)} training and {len(test_examples)} testing examples"
        )
        return train_db, test_db

    def save_spacy_data(
        self, train_db: DocBin, test_db: DocBin, train_path: str, test_path: str
    ) -> Tuple[str, str]:
        """
        Save spaCy data to disk.

        Args:
            train_db (DocBin): Training data
            test_db (DocBin): Testing data
            train_path (str): Path to save training data
            test_path (str): Path to save testing data

        Returns:
            Tuple[str, str]: Paths to saved training and testing data
        """
        try:
            train_db.to_disk(train_path)
            test_db.to_disk(test_path)
            logger.info(
                f"Saved training data to {train_path} and testing data to {test_path}"
            )
            return train_path, test_path
        except Exception as e:
            logger.error(f"Error saving spaCy data: {e}")
            raise

from typing import List
import os

from ..model.model import PIIModel
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PIIRedactorService:
    """Service for redacting PII from text."""

    def __init__(self, model_path: str):
        """
        Initialize the PIIRedactorService.

        Args:
            model_path (str): Path to the trained model
        """
        logger.info(f"Initializing PII Redactor Service with model at {model_path}")
        self.model = PIIModel(model_path)

    def redact(self, text: str) -> str:
        """
        Redact PII from a single text.

        Args:
            text (str): Input text

        Returns:
            str: Redacted text
        """
        try:
            return self.model.redact_text(text)
        except Exception as e:
            logger.error(f"Error redacting text: {e}")
            raise

    def redact_batch(self, texts: List[str]) -> List[str]:
        """
        Redact PII from a batch of texts.

        Args:
            texts (List[str]): List of input texts

        Returns:
            List[str]: List of redacted texts
        """
        try:
            return [self.redact(text) for text in texts]
        except Exception as e:
            logger.error(f"Error redacting batch: {e}")
            raise

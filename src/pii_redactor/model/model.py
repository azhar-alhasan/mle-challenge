import os
import re
import subprocess
from typing import List, Tuple, Dict, Any
import spacy

from ..config.config import PII_CATEGORIES, MODEL_CONFIG_PATH
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PIIModel:
    """Class to train and use the PII detection model."""

    def __init__(self, model_path: str = None):
        """
        Initialize the PIIModel.

        Args:
            model_path (str, optional): Path to the trained spaCy model
        """
        self.model_path = model_path
        self.using_rules = False

        # Define rules for PII detection with improved patterns
        self.rules = {
            # Address pattern should be checked first to avoid conflicts
            "ADDRESS": r"\b\d+\s+(?:[A-Z][a-z]+ )+(?:St(?:reet)?|Ave(?:nue)?|Rd|Road|Blvd|Boulevard|Ln|Lane|Dr|Drive|Ter(?:race)?|Pl(?:ace)?|Way),?(?:\s+(?:Apt|Suite|Unit)\s+[A-Za-z0-9]+)?,?\s+[A-Z][a-z]+(?:,\s+[A-Z]{2})?\s+\d{4,5}\b|\b\d+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd)",
            # Email pattern
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            # Phone number pattern
            "PHONE_NUMBER": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{4}\s?\d{3}\s?\d{3}\b",
            # More specific name pattern to avoid capturing street names
            "NAME": r"\b(?!(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Plaza|Plz|Terrace|Ter|Way)\b)[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b",
            # Organization pattern with common organizations and more general patterns
            "ORGANIZATION": r"\b(?:Google|Microsoft|Apple|Amazon|Facebook|Twitter|LinkedIn|National\s+[A-Za-z\s]+|[A-Z][a-z]+\s+(?:Inc|Corp|Corporation|Company|Co|Ltd|Limited|LLC|Association|Foundation|Organization))\b",
        }

        # Try to load model if path exists
        if model_path:
            # Check for model in the specified path
            meta_path = os.path.join(model_path, "meta.json")
            # Also check model-last subdirectory
            model_last_path = os.path.join(model_path, "model-last")
            model_last_meta_path = os.path.join(model_last_path, "meta.json")

            # Try loading from main path or model-last subdirectory
            if os.path.exists(meta_path):
                try:
                    self.nlp = spacy.load(model_path)
                    logger.info(f"Loaded NER model from {model_path}")
                    return
                except Exception as e:
                    logger.error(f"Error loading model from {model_path}: {e}")

            if os.path.exists(model_last_meta_path):
                try:
                    self.nlp = spacy.load(model_last_path)
                    self.model_path = model_last_path
                    logger.info(f"Loaded NER model from {model_last_path}")
                    return
                except Exception as e:
                    logger.error(f"Error loading model from {model_last_path}: {e}")

            # If we get here, neither path worked
            logger.error(
                f"No valid model found at {model_path} or {model_last_path}. Falling back to rule-based approach."
            )
            self.nlp = spacy.blank("en")
            self.using_rules = True
        else:
            # No model path provided
            logger.info("No model path provided. Using rule-based approach.")
            self.nlp = spacy.blank("en")
            self.using_rules = True

    def create_config(self, output_path: str = None):
        """
        Create a spaCy config file for training.

        Args:
            output_path (str, optional): Path to save the config file

        Returns:
            str: Path to the config file
        """
        if not output_path:
            output_path = MODEL_CONFIG_PATH

        # Create directories if they don't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create a simpler config that doesn't require transformer dependencies
        config = """
        [paths]
        train = null
        dev = null
        vectors = null
        
        [system]
        seed = 0
        
        [nlp]
        lang = "en"
        pipeline = ["ner"]
        batch_size = 64
        
        [components]
        
        [components.ner]
        factory = "ner"
        
        [components.ner.model]
        @architectures = "spacy.TransitionBasedParser.v2"
        state_type = "ner"
        extra_state_tokens = false
        hidden_width = 64
        maxout_pieces = 2
        use_upper = true
        nO = null
        
        [corpora]
        
        [corpora.train]
        @readers = "spacy.Corpus.v1"
        path = ${paths.train}
        max_length = 0
        
        [corpora.dev]
        @readers = "spacy.Corpus.v1"
        path = ${paths.dev}
        max_length = 0
        
        [training]
        gpu_allocator = "pytorch"
        seed = 0
        accumulate_gradient = 1
        dev_corpus = "corpora.dev"
        train_corpus = "corpora.train"
        patience = 1600
        max_steps = 5000
        eval_frequency = 200
        
        [training.optimizer]
        @optimizers = "Adam.v1"
        beta1 = 0.9
        beta2 = 0.999
        L2_is_weight_decay = true
        L2 = 0.01
        grad_clip = 1.0
        use_averages = false
        eps = 0.00000001
        
        [training.batcher]
        @batchers = "spacy.batch_by_words.v1"
        discard_oversize = true
        size = 2000
        tolerance = 0.2
        
        [initialize]
        vectors = null
        """

        with open(output_path, "w") as f:
            f.write(config.strip())

        logger.info(f"Created spaCy config at {output_path}")
        return output_path

    def train(self, train_data_path: str, test_data_path: str, output_path: str):
        """
        Train the model using spaCy CLI.

        Args:
            train_data_path (str): Path to training data
            test_data_path (str): Path to test data
            output_path (str): Path to save the trained model

        Returns:
            str: Path to the trained model
        """
        # Create config file
        config_path = self.create_config()

        # Create output directory
        os.makedirs(output_path, exist_ok=True)

        # Run training command
        cmd = [
            "python",
            "-m",
            "spacy",
            "train",
            config_path,
            "--output",
            output_path,
            "--paths.train",
            train_data_path,
            "--paths.dev",
            test_data_path,
            "--training.max_steps",
            "1000",  # Reduced for faster training
            "--training.eval_frequency",
            "100",
            "--gpu-id",
            "0",  # Use GPU for training
        ]

        logger.info(f"Starting training with command: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True)
            # The actual model is saved in a model-last subdirectory
            model_last_path = os.path.join(output_path, "model-last")
            logger.info(
                f"Training completed successfully. Model saved to {model_last_path}"
            )

            # Load the trained model from the correct subdirectory
            self.nlp = spacy.load(model_last_path)
            self.model_path = model_last_path
            self.using_rules = False

            return model_last_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error during training: {e}")
            raise

    def predict(self, text: str) -> List[Tuple[str, int, int, str]]:
        """
        Predict PII entities in text.

        Args:
            text (str): Input text

        Returns:
            List[Tuple[str, int, int, str]]: List of (text, start, end, label) tuples
        """
        entities = []

        if not self.using_rules:
            # Use trained model
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in PII_CATEGORIES:
                    entities.append(
                        (ent.text, ent.start_char, ent.end_char, ent.label_)
                    )

        # Apply rule-based approach if no entities found or using rules
        if not entities or self.using_rules:
            # Use regex patterns
            for category, pattern in self.rules.items():
                for match in re.finditer(pattern, text):
                    start, end = match.span()
                    entities.append((text[start:end], start, end, category))

        # Sort entities by position
        entities.sort(key=lambda x: x[1])

        logger.debug(f"Found {len(entities)} entities in text")
        return entities

    def redact_text(self, text: str) -> str:
        """
        Redact PII entities in text.

        Args:
            text (str): Input text

        Returns:
            str: Redacted text
        """
        entities = self.predict(text)

        # Sort entities by position in reverse order
        entities.sort(key=lambda x: x[1], reverse=True)

        # Redact entities
        redacted_text = text
        for entity_text, start, end, label in entities:
            redacted_text = redacted_text[:start] + f"[{label}]" + redacted_text[end:]

        return redacted_text

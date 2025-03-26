import os
from typing import Tuple

from ..config.config import DATA_PATH, MODEL_PATH
from ..data.processor import PIIDataProcessor
from .model import PIIModel
from ..utils.logger import get_logger

logger = get_logger(__name__)


def train_model(data_path: str = DATA_PATH, model_path: str = MODEL_PATH) -> str:
    """
    Train a PII detection model.

    Args:
        data_path (str): Path to the JSON data file
        model_path (str): Path to save the trained model

    Returns:
        str: Path to the trained model
    """
    logger.info(f"Training model with data from {data_path}")

    # Use default paths if None is provided
    if data_path is None:
        data_path = DATA_PATH
    if model_path is None:
        model_path = MODEL_PATH

    # Create output directory
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # Load and process data
    processor = PIIDataProcessor(data_path)
    data = processor.load_data()
    training_data = processor.create_training_data(data)

    # Prepare data for spaCy
    train_db, test_db = processor.prepare_spacy_data(training_data)

    # Create temporary files for the data
    train_data_path = os.path.join(os.path.dirname(model_path), "train.spacy")
    test_data_path = os.path.join(os.path.dirname(model_path), "test.spacy")

    # Save data
    processor.save_spacy_data(train_db, test_db, train_data_path, test_data_path)

    # Initialize and train model
    model = PIIModel()
    model_path = model.train(train_data_path, test_data_path, model_path)

    logger.info(f"Model training completed. Model saved to {model_path}")
    return model_path

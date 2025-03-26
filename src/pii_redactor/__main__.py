import argparse
import os
import sys

from .config.config import MODEL_PATH
from .model.factory import train_model
from .service.service import PIIRedactorService
from .utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main entry point for the PII redactor module."""
    parser = argparse.ArgumentParser(description="Redact PII from text")

    # Define subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Train command
    train_parser = subparsers.add_parser("train", help="Train a new model")
    train_parser.add_argument("--data", type=str, help="Path to training data")
    train_parser.add_argument(
        "--output", type=str, help="Path to save the trained model"
    )

    # Redact command
    redact_parser = subparsers.add_parser("redact", help="Redact PII from text")
    redact_parser.add_argument("--text", type=str, help="Text to redact")
    redact_parser.add_argument(
        "--file", type=str, help="File containing text to redact"
    )
    redact_parser.add_argument(
        "--output", type=str, help="Output file for redacted text"
    )
    redact_parser.add_argument(
        "--model", type=str, help="Path to the model to use for redaction"
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if not args.command:
        # No command provided
        parser.print_help()
        return

    if args.command == "train":
        # Train a new model
        data_path = args.data if hasattr(args, "data") and args.data else None
        output_path = args.output if hasattr(args, "output") and args.output else None

        logger.info("Training a new model...")
        try:
            model_path = train_model(data_path, output_path)
            logger.info(f"Model trained and saved to {model_path}")
        except Exception as e:
            logger.error(f"Error training model: {e}")
            sys.exit(1)

    elif args.command == "redact":
        # Redact text
        if (
            not hasattr(args, "text")
            or not hasattr(args, "file")
            or (not args.text and not args.file)
        ):
            logger.error("Either --text or --file must be provided")
            redact_parser.print_help()
            sys.exit(1)

        model_path = args.model if hasattr(args, "model") and args.model else MODEL_PATH

        # Initialize service
        service = PIIRedactorService(model_path)

        # Get input text
        if hasattr(args, "file") and args.file:
            try:
                with open(args.file, "r") as f:
                    text = f.read()
            except Exception as e:
                logger.error(f"Error reading file: {e}")
                sys.exit(1)
        else:
            text = args.text

        # Redact text
        redacted_text = service.redact(text)

        # Output
        if hasattr(args, "output") and args.output:
            try:
                with open(args.output, "w") as f:
                    f.write(redacted_text)
                logger.info(f"Redacted text written to {args.output}")
            except Exception as e:
                logger.error(f"Error writing to output file: {e}")
                sys.exit(1)
        else:
            logger.info("\nOriginal text:")
            logger.info("-" * 50)
            logger.info(text)
            logger.info("\nRedacted text:")
            logger.info("-" * 50)
            logger.info(redacted_text)
    else:
        # Unknown command
        logger.error(f"Unknown command: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()

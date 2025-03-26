# PII Redactor Solution

This solution implements a machine learning-based PII (Personally Identifiable Information) redaction service that identifies and redacts the following types of PII from text:

- `NAME` - Names of people or organizations
- `ORGANIZATION` - Names of organizations
- `ADDRESS` - Addresses of people or organizations
- `EMAIL` - Email addresses
- `PHONE_NUMBER` - Phone numbers

## Solution Architecture

The solution follows a modular architecture with clear separation of concerns:

1. **Data Processing**: Handles loading and preprocessing of training data
2. **Model Component**: A Named Entity Recognition (NER) model using spaCy to identify PII in text
3. **Service Component**: A FastAPI-based web service that provides an API for redacting PII from text
4. **CLI Interface**: Command-line tools for training models and redacting text

## Code Structure

The codebase is organized as a proper Python package with the following structure:

```
pii-redactor/
├── data/                  # Data files
├── models/                # Trained models
├── src/                   # Source code
│   ├── pii_redactor/      # Main package
│   │   ├── __init__.py
│   │   ├── config/        # Configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   ├── data/          # Data processing
│   │   │   ├── __init__.py
│   │   │   └── processor.py
│   │   ├── model/         # Model definition and training
│   │   │   ├── __init__.py
│   │   │   ├── factory.py
│   │   │   └── model.py
│   │   ├── service/       # Service layer
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   └── service.py
│   │   ├── utils/         # Utilities
│   │   │   ├── __init__.py
│   │   │   └── logger.py
│   │   └── __main__.py    # CLI entry point
│   └── tests/             # Tests
│       ├── __init__.py
│       ├── test_model.py
│       ├── test_processor.py
│       └── test_service.py
├── app.py                 # Backward compatibility entry point
├── cli.py                 # Backward compatibility entry point
├── setup.py               # Package setup script
├── Dockerfile
├── docker-compose.yml
└── test.sh                # Test runner script
```

### Key Components

1. **Data Processor**: Extracts PII entities from training data by comparing original and redacted texts
2. **PII Model**: Uses spaCy for NER, with fallback to regex patterns for common PII formats
3. **Redactor Service**: Main service that handles redacting PII from text
4. **API Layer**: FastAPI implementation with endpoints for single and batch redaction
5. **CLI Interface**: Command-line tools with subcommands for training and redaction

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository
2. Install the package and dependencies:
   ```bash
   # Using pip
   pip install -e .
   
   # OR via requirements.txt
   pip install -r requirements.txt
   ```

## Running the Application

### Command Line Interface

The package provides a command-line interface with multiple subcommands:

#### Training a Model

```bash
# Using the installed package
pii-redactor train

# Using the compatibility script
python cli.py train

# With custom paths
pii-redactor train --data path/to/data.json --output path/to/model
```

#### Redacting Text

```bash
# From command line
pii-redactor redact --text "Please contact John Smith at john.smith@example.com"

# From a file
pii-redactor redact --file input.txt --output redacted.txt
```

### Running the API Server

```bash
# Using the installed package
pii-redactor-api

# Using the compatibility script
python app.py

# Using uvicorn directly
uvicorn src.pii_redactor.service.api:create_app --factory --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000 with interactive documentation at http://localhost:8000/docs.

### Using Docker

```bash
# Build and start the service
docker-compose up --build

# Run in background
docker-compose up -d
```

The service will be available at http://localhost:8000.

## API Usage

### Redact PII from Text

**Request:**
```bash
curl -X POST http://localhost:8000/redact \
  -H "Content-Type: application/json" \
  -d '{"text": "Please contact Sarah Thompson at sarah.thompson@company.com.au or 0422 111 222 to schedule a meeting."}'
```

**Response:**
```json
{
    "redacted_text": "Please contact [NAME] at [EMAIL] or [PHONE_NUMBER] to schedule a meeting."
}
```

### Redact PII from Multiple Texts

**Request:**
```bash
curl -X POST http://localhost:8000/redact/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Please contact Sarah Thompson at sarah.thompson@company.com.au.", "My phone number is 0422 111 222."]}'
```

**Response:**
```json
{
    "redacted_texts": [
        "Please contact [NAME] at [EMAIL].",
        "My phone number is [PHONE_NUMBER]."
    ]
}
```

## Testing

The solution includes comprehensive unit tests for all components. To run the tests:

```bash
# Using the test script
./test.sh

# OR using Python unittest directly
PYTHONPATH=$PYTHONPATH:$(pwd)/src python -m unittest discover -v -s src/tests
```

## Design Patterns and Best Practices

The codebase implements several software engineering best practices:

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Factory Pattern**: For model creation and training
3. **Dependency Injection**: For better testability
4. **Configuration Management**: Centralized configuration
5. **Comprehensive Logging**: For better debugging and monitoring
6. **Type Hints**: For better code readability and IDE support
7. **Comprehensive Documentation**: Docstrings and comments

## Assumptions and Limitations

1. The model is trained on a relatively small dataset, so its performance may be limited.
2. The current implementation uses a hybrid approach: ML-based detection with regex fallback.
3. The model identifies entities using context and learned patterns, but might struggle with unusual formats.

## Potential Improvements

1. Use a larger dataset for training
2. Incorporate additional specialized models for specific entity types
3. Implement confidence scores for redacted entities
4. Add incremental learning capabilities
5. Implement more sophisticated pattern matching for edge cases
6. Add more comprehensive metrics and monitoring 
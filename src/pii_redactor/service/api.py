from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import uvicorn

from ..config.config import (
    MODEL_PATH,
    API_HOST,
    API_PORT,
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
)
from ..model.factory import train_model
from .service import PIIRedactorService
from ..utils.logger import get_logger

logger = get_logger(__name__)


# Define request and response models
class RedactRequest(BaseModel):
    text: str


class RedactResponse(BaseModel):
    redacted_text: str


class BatchRedactRequest(BaseModel):
    texts: List[str]


class BatchRedactResponse(BaseModel):
    redacted_texts: List[str]


class HealthResponse(BaseModel):
    status: str
    version: str


def create_app():
    """Create a FastAPI application."""
    # Check if model exists, train if it doesn't
    try:
        if not os.path.exists(MODEL_PATH):
            logger.info("Model not found. Training a new model...")
            model_path = train_model()
        else:
            model_path = MODEL_PATH

        # Initialize the service
        service = PIIRedactorService(model_path)
    except Exception as e:
        logger.error(f"Error initializing service: {e}")
        # We'll still create the app, but it will return error responses
        service = None

    # Create FastAPI app
    app = FastAPI(title=API_TITLE, description=API_DESCRIPTION, version=API_VERSION)

    @app.get("/", response_model=HealthResponse)
    async def root():
        """Root endpoint for health check."""
        status = "healthy" if service is not None else "unhealthy"
        return HealthResponse(status=status, version=API_VERSION)

    @app.post("/redact", response_model=RedactResponse)
    async def redact(request: RedactRequest):
        """Redact PII from text."""
        if service is None:
            logger.error("Service not initialized properly")
            raise HTTPException(
                status_code=500, detail="Service not initialized properly"
            )

        try:
            redacted_text = service.redact(request.text)
            return RedactResponse(redacted_text=redacted_text)
        except Exception as e:
            logger.error(f"Error redacting text: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error redacting text: {str(e)}"
            )

    @app.post("/redact/batch", response_model=BatchRedactResponse)
    async def redact_batch(request: BatchRedactRequest):
        """Redact PII from a batch of texts."""
        if service is None:
            logger.error("Service not initialized properly")
            raise HTTPException(
                status_code=500, detail="Service not initialized properly"
            )

        try:
            redacted_texts = service.redact_batch(request.texts)
            return BatchRedactResponse(redacted_texts=redacted_texts)
        except Exception as e:
            logger.error(f"Error redacting batch: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error redacting batch: {str(e)}"
            )

    return app


def start_server():
    """Start the API server."""
    app = create_app()
    logger.info(f"Starting API server on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    start_server()

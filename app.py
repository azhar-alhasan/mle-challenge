#!/usr/bin/env python3
"""
Backward compatibility entry point for the PII Redactor service.
This file simply imports and calls the new API server.
"""

from src.pii_redactor.service.api import start_server

if __name__ == "__main__":
    start_server()

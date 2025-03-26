#!/usr/bin/env python3
"""
Backward compatibility entry point for the PII Redactor CLI.
This file simply imports and calls the new CLI.
"""

from src.pii_redactor.__main__ import main

if __name__ == "__main__":
    main()

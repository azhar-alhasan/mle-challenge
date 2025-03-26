#!/bin/bash
# Quick script to run the tests

# Set PYTHONPATH to include the src directory
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Run tests
python -m unittest discover -v -s src/tests 
#!/bin/sh

# Start the FastAPI application
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &

# Capture the PID of the FastAPI process
PID=$!

# Wait for the FastAPI process to complete
wait $PID
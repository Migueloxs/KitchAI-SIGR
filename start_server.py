#!/usr/bin/env python3
"""Start the FastAPI development server"""
import subprocess
import sys
import time

print("Starting FastAPI development server...")
print("Server will be available at http://localhost:8001")
print("Swagger UI: http://localhost:8001/docs")
print("")

try:
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--reload", 
        "--port", "8001"
    ])
except KeyboardInterrupt:
    print("\nServer stopped")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

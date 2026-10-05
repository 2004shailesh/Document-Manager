"""
================================================================================
Root Application Entrypoint Wrapper
================================================================================
Enables running `uvicorn main:app --reload` directly from the project root.
Imports and exposes the primary FastAPI app from `src.api.api.main`.
================================================================================
"""

import os
import sys

# Ensure project root and backend directory are in sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from src.api.api import app
from src.constants.constant import DEBUG, ENVIRONMENT, HOST, PORT

__all__ = ["app"]


def run() -> None:
    """Entrypoint function for CLI script execution (e.g. `dev`)."""
    import uvicorn

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG and ENVIRONMENT == "development",
    )


if __name__ == "__main__":
    run()


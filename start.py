#!/usr/bin/env python3
"""
Startup script for Railway deployment
This script handles data ingestion and starts the FastAPI server
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_directories():
    """Create necessary directories"""
    directories = [
        "data/pdfs",
        "data/docx",
        "data/scraped_pages",
        "chroma_db"
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def check_vector_store():
    """Check if vector store exists and has data"""
    chroma_db_path = Path("chroma_db")
    if chroma_db_path.exists():
        # Check if there are any files in the chroma_db directory
        db_files = list(chroma_db_path.rglob('*'))
        non_empty_files = [f for f in db_files if f.is_file() and f.stat().st_size > 0]

        if non_empty_files:
            logger.info(f"Vector store found with {len(non_empty_files)} files, skipping data ingestion")
            return True

    logger.info("Vector store not found or empty, will need to ingest data")
    return False


async def run_data_ingestion():
    """Run data ingestion if needed"""
    try:
        logger.info("Starting data ingestion...")

        # Import and run ingestion
        from ingest_data import AngelOneDataIngester

        ingester = AngelOneDataIngester()
        vector_store = await asyncio.to_thread(ingester.run_ingestion)

        if vector_store:
            logger.info("Data ingestion completed successfully")
            return True
        else:
            logger.error("Data ingestion failed")
            return False

    except Exception as e:
        logger.error(f"Error during data ingestion: {e}")
        logger.exception("Full traceback:")
        return False


def start_server():
    """Start the FastAPI server"""
    try:
        logger.info("Starting FastAPI server...")
        port = int(os.getenv("PORT", "8000"))

        # Import uvicorn and start server
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )

    except ImportError as e:
        logger.error(f"Failed to import uvicorn: {e}")
        logger.error("Trying alternative startup method...")

        # Alternative: use subprocess to start uvicorn
        import subprocess
        port = int(os.getenv("PORT", "8000"))
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", str(port)
        ]

        logger.info(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd)

    except Exception as e:
        logger.error(f"Error starting server: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


async def main():
    """Main startup function"""
    logger.info("=" * 60)
    logger.info("Angel One RAG Chatbot - Railway Deployment")
    logger.info("=" * 60)

    # Debug: Print Python path and installed packages location
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"PATH environment: {os.environ.get('PATH', 'Not set')}")

    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is required")
        sys.exit(1)
    else:
        logger.info("OPENAI_API_KEY found ✓")

    # Setup directories
    setup_directories()

    # Check if we need to run data ingestion
    if not check_vector_store():
        logger.info("Running data ingestion on first deployment...")
        success = await run_data_ingestion()
        if not success:
            logger.warning("Data ingestion failed, but continuing with server startup")
    else:
        logger.info("Vector store exists, skipping data ingestion")

    # Start the server
    logger.info("Starting server...")
    start_server()


if __name__ == "__main__":
    # Check if uvicorn is available
    try:
        import uvicorn

        logger.info("uvicorn imported successfully ✓")
    except ImportError as e:
        logger.error(f"uvicorn import failed: {e}")
        logger.error("This indicates a package installation issue")
        sys.exit(1)

    # Run main function
    asyncio.run(main())
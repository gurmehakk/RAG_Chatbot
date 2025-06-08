#!/usr/bin/env python3
"""
Startup script for Railway deployment
This script handles data ingestion and starts the FastAPI server
"""

import os
import sys
import asyncio
import subprocess
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
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
    """Check if vector store exists"""
    chroma_db_path = Path("chroma_db")
    if chroma_db_path.exists() and any(chroma_db_path.iterdir()):
        logger.info("Vector store found, skipping data ingestion")
        return True
    else:
        logger.info("Vector store not found, will need to ingest data")
        return False


async def run_data_ingestion():
    """Run data ingestion if needed"""
    try:
        logger.info("Starting data ingestion...")

        # Import and run ingestion
        from ingest_data import AngelOneDataIngester, setup_directories

        setup_directories()
        ingester = AngelOneDataIngester()
        vector_store = ingester.run_ingestion()

        if vector_store:
            logger.info("Data ingestion completed successfully")
            return True
        else:
            logger.error("Data ingestion failed")
            return False

    except Exception as e:
        logger.error(f"Error during data ingestion: {e}")
        return False


def start_server():
    """Start the FastAPI server"""
    try:
        logger.info("Starting FastAPI server...")
        port = int(os.getenv("PORT", "8000"))

        # Start uvicorn server
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )

    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


async def main():
    """Main startup function"""
    logger.info("=" * 60)
    logger.info("Angel One RAG Chatbot - Railway Deployment")
    logger.info("=" * 60)

    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is required")
        sys.exit(1)

    # Setup directories
    setup_directories()

    # Check if we need to run data ingestion
    if not check_vector_store():
        logger.info("Running data ingestion on first deployment...")
        success = await run_data_ingestion()
        if not success:
            logger.warning("Data ingestion failed, but continuing with server startup")

    # Start the server
    logger.info("Starting server...")
    start_server()


if __name__ == "__main__":
    asyncio.run(main())
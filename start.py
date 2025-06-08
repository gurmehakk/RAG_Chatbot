#!/usr/bin/env python3
"""
Startup script to run data ingestion followed by the main application.
Provides better error handling and logging for Docker deployment.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def run_command(command, description):
    """Run a command and handle errors."""
    try:
        logger.info(f"Starting: {description}")
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Completed: {description}")
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed: {description}")
        logger.error(f"Error: {e.stderr}")
        return False


def check_files_exist():
    """Check if required files exist."""
    required_files = ['ingest_data.py', 'main.py']
    for file in required_files:
        if not Path(file).exists():
            logger.error(f"Required file not found: {file}")
            return False
    return True


def create_directories():
    """Ensure data directories exist."""
    dirs = ['data', 'data/pdfs', 'data/docx', 'data/scraped_pages', 'chroma_db']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ensured: {dir_path}")


def main():
    """Main startup sequence."""
    logger.info("=== Starting Application Deployment ===")

    # Check if required files exist
    if not check_files_exist():
        logger.error("Missing required files. Exiting.")
        sys.exit(1)

    # Create necessary directories
    create_directories()

    # Step 1: Run data ingestion
    logger.info("Step 1: Running data ingestion...")
    if not run_command("python ingest_data.py", "Data ingestion"):
        logger.error("Data ingestion failed. Continuing anyway...")
        # Don't exit here - the app might still work with existing data

    # Step 2: Start the main application
    logger.info("Step 2: Starting main application...")

    # Get port from environment - using 8000 consistently
    port = os.environ.get('PORT', '8000')
    logger.info(f"Starting app on port {port}")

    # Start the main application
    # Adjust this command based on how your main.py starts the server
    try:
        # If main.py uses uvicorn or similar, you might need to modify this
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down gracefully.")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
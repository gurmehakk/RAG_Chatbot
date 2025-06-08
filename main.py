from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
import logging
from pathlib import Path
import asyncio

from models import ChatResponse, QuestionRequest, SourceInfo, HealthResponse
from rag_chain import get_rag_chain
from chatbot_interface import get_chatbot_html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Angel One RAG Chatbot API",
    description="A Retrieval-Augmented Generation chatbot for Angel One customer support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_chain_instance = None


def setup_directories():
    """Create necessary directories"""
    directories = ["data/pdfs", "data/docx", "data/scraped_pages", "chroma_db"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def check_vector_store():
    """Check if vector store exists and has data"""
    chroma_db_path = Path("chroma_db")
    if chroma_db_path.exists() and any(chroma_db_path.iterdir()):
        logger.info("Vector store found")
        return True
    else:
        logger.warning("Vector store not found - data ingestion may be needed")
        return False


async def run_initial_setup():
    """Run initial setup including data ingestion if needed"""
    try:
        # Setup directories
        setup_directories()

        # Check if vector store exists
        if not check_vector_store():
            logger.info("Vector store not found. Running data ingestion...")

            # Import and run ingestion
            from ingest_data import AngelOneDataIngester

            ingester = AngelOneDataIngester()
            vector_store = await asyncio.get_event_loop().run_in_executor(
                None, ingester.run_ingestion
            )

            if vector_store:
                logger.info("Data ingestion completed successfully")
            else:
                logger.warning("Data ingestion failed, but continuing with startup")

        return True
    except Exception as e:
        logger.error(f"Error during initial setup: {str(e)}")
        return False


@app.on_event("startup")
async def startup_event():
    """Initialize the RAG chain on startup"""
    global rag_chain_instance
    try:
        logger.info("Starting Angel One RAG Chatbot...")

        # Check for required environment variables
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY environment variable is required")
            raise ValueError("OPENAI_API_KEY not found")

        # Run initial setup
        await run_initial_setup()

        # Initialize RAG chain
        logger.info("Initializing RAG chain...")
        rag_chain_instance = get_rag_chain()
        logger.info("RAG chain initialized successfully")

        # Test the system
        health_result = rag_chain_instance.health_check()
        logger.info(f"System health check: {health_result['status']}")

    except Exception as e:
        logger.error(f"Failed to initialize RAG chain: {str(e)}")
        # Don't raise here - let the app start and show error in health check
        pass


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main chatbot interface"""
    return get_chatbot_html()


@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: QuestionRequest):
    """Main endpoint to ask questions to the RAG chatbot"""
    global rag_chain_instance  # Move global declaration to the top

    try:
        if not rag_chain_instance:
            # Try to initialize if not already done
            try:
                rag_chain_instance = get_rag_chain()
            except Exception as e:
                raise HTTPException(
                    status_code=503,
                    detail="RAG system not initialized. Please check logs and try again later."
                )

        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        if len(request.question) > 500:
            raise HTTPException(status_code=400, detail="Question too long (max 500 characters)")

        logger.info(f"Processing question: {request.question[:100]}...")

        # Get answer from RAG chain
        result = rag_chain_instance.ask_question(request.question)

        # Get similar questions for better UX
        similar_questions = rag_chain_instance.get_similar_questions(request.question)

        # Convert to response model
        sources = [SourceInfo(**source) for source in result["sources"]]

        response = ChatResponse(
            answer=result["answer"],
            sources=sources,
            confidence=result["confidence"],
            similar_questions=similar_questions
        )

        logger.info(f"Question processed successfully. Confidence: {result['confidence']}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        if not rag_chain_instance:
            return HealthResponse(
                status="error",
                vector_store_loaded=False,
                total_documents=0,
                test_query_successful=False,
                error="RAG chain not initialized"
            )

        health_data = rag_chain_instance.health_check()

        return HealthResponse(
            status=health_data["status"],
            vector_store_loaded=health_data["vector_store_loaded"],
            total_documents=health_data.get("total_documents", 0),
            test_query_successful=health_data.get("test_query_successful", False),
            error=health_data.get("error")
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="error",
            vector_store_loaded=False,
            total_documents=0,
            test_query_successful=False,
            error=str(e)
        )


@app.get("/sources")
async def get_sources():
    """Get information about available data sources"""
    try:
        if not rag_chain_instance:
            return {"error": "RAG chain not initialized"}

        metadata = getattr(rag_chain_instance, 'metadata', {})
        return {
            "total_documents": metadata.get("total_documents", 0),
            "total_chunks": metadata.get("total_chunks", 0),
            "sources": metadata.get("sources", [])
        }
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/vector-store-info")
async def get_vector_store_info():
    """Get detailed information about the vector store"""
    try:
        if not rag_chain_instance:
            return {"error": "RAG chain not initialized"}

        # Get collection info from Chroma
        try:
            collection = rag_chain_instance.vector_store._collection
            count = collection.count()
        except:
            count = 0

        # Try to get a sample of documents to show what's available
        try:
            sample_docs = rag_chain_instance.vector_store.similarity_search("Angel One", k=3)
            sample_sources = list(set([doc.metadata.get("source", "Unknown") for doc in sample_docs]))
        except:
            sample_sources = []

        return {
            "vector_store_type": "Chroma",
            "total_documents": count,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "sample_sources": sample_sources[:5],
            "collection_name": getattr(collection, 'name', 'default') if 'collection' in locals() else "default"
        }
    except Exception as e:
        logger.error(f"Error getting vector store info: {str(e)}")
        return {"error": str(e)}


@app.get("/ingest-data")
async def trigger_data_ingestion():
    """Manually trigger data ingestion (for debugging)"""
    global rag_chain_instance  # Add global declaration here too

    try:
        logger.info("Manual data ingestion triggered")

        from ingest_data import AngelOneDataIngester, setup_directories

        setup_directories()
        ingester = AngelOneDataIngester()

        # Run ingestion in background
        vector_store = await asyncio.get_event_loop().run_in_executor(
            None, ingester.run_ingestion
        )

        if vector_store:
            # Reinitialize RAG chain
            rag_chain_instance = get_rag_chain()

            return {"status": "success", "message": "Data ingestion completed"}
        else:
            return {"status": "error", "message": "Data ingestion failed"}

    except Exception as e:
        logger.error(f"Error during manual ingestion: {str(e)}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print(" Starting Angel One RAG Chatbot Server...")
    print("=" * 60)
    print("  IMPORTANT: Make sure you have:")
    print("1.  Set OPENAI_API_KEY environment variable")
    print("2.  Added PDF files to data/pdfs/ directory")
    print("3.  Added DOCX files to data/docx/ directory")
    print("=" * 60)

    port = int(os.getenv("PORT", "8000"))
    print(f" Server will be available at: http://0.0.0.0:{port}")
    print(f" Health check: http://0.0.0.0:{port}/health")
    print(f" Vector store info: http://0.0.0.0:{port}/vector-store-info")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
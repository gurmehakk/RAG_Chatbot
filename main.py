from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os

from models import ChatResponse, QuestionRequest, SourceInfo, HealthResponse
from rag_chain import get_rag_chain
from chatbot_interface import get_chatbot_html
import logging
logging.basicConfig(level=logging.INFO)
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


@app.on_event("startup")
async def startup_event():
    """Initialize the RAG chain on startup"""
    global rag_chain_instance
    try:
        logger.info("Initializing RAG chain...")
        rag_chain_instance = get_rag_chain()
        logger.info("RAG chain initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG chain: {str(e)}")
        raise


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main chatbot interface"""
    return get_chatbot_html()


@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: QuestionRequest):
    """Main endpoint to ask questions to the RAG chatbot"""
    try:
        if not rag_chain_instance:
            raise HTTPException(status_code=500, detail="RAG chain not initialized")

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
            raise HTTPException(status_code=500, detail="RAG chain not initialized")

        metadata = getattr(rag_chain_instance, 'metadata', {})
        return {
            "total_documents": metadata.get("total_documents", 0),
            "total_chunks": metadata.get("total_chunks", 0),
            "sources": metadata.get("sources", [])
        }
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/chat-history")
async def get_chat_history():
    """Get recent chat history for analytics (optional endpoint)"""
    # For now, return empty as we're not storing history
    return {"message": "Chat history not implemented yet"}


@app.get("/vector-store-info")
async def get_vector_store_info():
    """Get detailed information about the vector store"""
    try:
        if not rag_chain_instance:
            raise HTTPException(status_code=500, detail="RAG chain not initialized")

        # Get collection info from Chroma
        collection = rag_chain_instance.vector_store._collection
        count = collection.count()

        # Try to get a sample of documents to show what's available
        sample_docs = rag_chain_instance.vector_store.similarity_search("Angel One", k=3)
        sample_sources = list(set([doc.metadata.get("source", "Unknown") for doc in sample_docs]))

        return {
            "vector_store_type": "Chroma",
            "total_documents": count,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "sample_sources": sample_sources[:5],
            "collection_name": collection.name if hasattr(collection, 'name') else "default"
        }
    except Exception as e:
        logger.error(f"Error getting vector store info: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Serve static files (for React frontend if needed)
if os.path.exists("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

if __name__ == "__main__":
    print(" Starting Angel One RAG Chatbot Server...")
    print("=" * 50)
    print("1.  Created the vector store by running: python ingest_data.py")
    print("2.  Set OPENAI_API_KEY in your .env file")
    print("3.  Added documents to chroma_db/ directory")
    print("=" * 50)
    print(" Server will be available at: http://localhost:8000")
    print(" Health check endpoint: http://localhost:8000/health")
    print(" Vector store info: http://localhost:8000/vector-store-info")
    print(" Sources info: http://localhost:8000/sources")
    print("=" * 50)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
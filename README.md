# RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built with LangChain, Hugging Face embeddings, and Chroma vector database. This application allows users to upload documents and ask questions about their content using natural language.

## 🌐 Live Demo

**Service URL:** https://ragbot-5kblu53ana-uc.a.run.app

<img width="1224" alt="Screenshot 2025-06-08 at 12 28 29 AM" src="https://github.com/user-attachments/assets/8993afdf-fcb0-4d6b-9d30-8aa36eac2eca" />
<img width="914" alt="Screenshot 2025-06-08 at 12 29 41 AM" src="https://github.com/user-attachments/assets/91db23f8-7874-4c1e-b4bc-e073e0e52548" />


## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [How It Works](#how-it-works)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)

## 🔍 Overview

This RAG (Retrieval-Augmented Generation) chatbot combines the power of information retrieval with generative AI to provide accurate, context-aware responses based on your uploaded documents. Instead of relying solely on pre-trained knowledge, the system retrieves relevant information from your documents and uses it to generate informed responses.

## 🏗️ Architecture

The application follows a typical RAG architecture:

```
User Query → Document Retrieval → Context Augmentation → LLM Response Generation
     ↑              ↑                      ↑                        ↑
   Frontend    Vector Search         LangChain Pipeline      Generative AI
                (Chroma DB)         (Prompt Engineering)
```

## 🛠️ Technologies Used

### Core Technologies

- **LangChain**: Orchestrates the entire RAG pipeline, handling document processing, retrieval, and response generation
- **Hugging Face Embeddings**: Converts text into high-dimensional vectors for semantic similarity search
- **Chroma**: Vector database for storing and retrieving document embeddings efficiently
- **Google Cloud Run**: Serverless deployment platform

### Supporting Technologies

- **Python**: Core programming language
- **FastAPI**: Web framework for API endpoints
- **Docker**: Containerization for consistent deployment

## 🔧 How It Works

### 1. Document Processing
- Users upload documents (PDF, TXT, DOCX, etc.)
- **LangChain** splits documents into manageable chunks using text splitters
- Each chunk maintains context and metadata for better retrieval

### 2. Embedding Generation
- **Hugging Face embeddings** (likely `sentence-transformers/all-MiniLM-L6-v2` or similar) convert text chunks into dense vector representations
- These embeddings capture semantic meaning, allowing for similarity-based retrieval
- Embeddings are generated locally without external API calls

### 3. Vector Storage
- **Chroma** stores the embeddings along with their corresponding text chunks
- Provides fast similarity search capabilities
- Maintains persistence between sessions

### 4. Query Processing
When a user asks a question:

1. **Query Embedding**: The user's question is converted to an embedding using the same Hugging Face model
2. **Similarity Search**: Chroma performs vector similarity search to find the most relevant document chunks
3. **Context Retrieval**: Top-k most similar chunks are retrieved as context
4. **Response Generation**: LangChain combines the retrieved context with the user's question in a prompt template
5. **LLM Processing**: The augmented prompt is sent to a language model for response generation

### 5. LangChain's Role

LangChain acts as the orchestration layer:

- **Document Loaders**: Handle different file formats
- **Text Splitters**: Break documents into optimal chunks
- **Retrieval Chains**: Manage the retrieval and generation pipeline
- **Prompt Templates**: Structure the context and query for the LLM
- **Memory Management**: Handle conversation history and context
- **Chain Composition**: Connect retrieval and generation components seamlessly

## ✨ Features

- **Multi-format Document Support**: PDF, TXT, DOCX, and more
- **Semantic Search**: Find relevant information even with different wording
- **Context-Aware Responses**: Answers are grounded in your uploaded documents
- **Persistent Storage**: Documents remain available across sessions
- **Scalable Architecture**: Deployed on Google Cloud Run for auto-scaling
- **Fast Retrieval**: Optimized vector search with Chroma
- **Privacy-Focused**: Documents and embeddings stored locally/privately

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Google Cloud SDK (for deployment)
- Docker (optional, for containerization)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RAG_Chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## 💻 Usage

### Web Interface

1. Navigate to the application URL
2. Upload your documents using the file upload interface
3. Wait for processing (document chunking and embedding generation)
4. Ask questions about your documents in natural language
5. Receive contextually relevant answers

### Example Queries

- "What are the main findings in the research paper?"
- "Summarize the key points from chapter 3"
- "What does the document say about [specific topic]?"

## 🌐 Deployment

The application is deployed on Google Cloud Run for serverless scaling:

```bash
# Build and deploy
gcloud run deploy ragbot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Deployment Features

- **Auto-scaling**: Scales from 0 to handle traffic spikes
- **HTTPS**: Automatic SSL certificate
- **Global CDN**: Fast content delivery
- **Monitoring**: Built-in logging and metrics

## 📡 API Endpoints

- `POST /upload`: Upload documents for processing
- `POST /query`: Ask questions about uploaded documents
- `GET /health`: Health check endpoint
- `GET /documents`: List uploaded documents
- `DELETE /documents/{id}`: Remove specific documents

## 🔧 Configuration

Key configuration options:

- **Embedding Model**: Specify Hugging Face model for embeddings
- **Chunk Size**: Control document splitting parameters
- **Retrieval Count**: Number of relevant chunks to retrieve
- **Vector Store**: Chroma database configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

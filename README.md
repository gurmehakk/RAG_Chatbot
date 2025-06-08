# Angel Assist: Angel One Support RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot designed to provide customer support assistance based on Angel One's documentation and resources.
This intelligent chatbot can answer queries related to Angel One services, trading, and insurance policies using only the information available in the provided sources.

## 📸 Screenshots

### Chatbot Interface
<img width="1224" alt="Screenshot 2025-06-08 at 12 28 29 AM" src="https://github.com/user-attachments/assets/cb98cce9-fb68-455b-b98a-b139846a304e" />

### Sample Conversations
<img width="914" alt="Screenshot 2025-06-08 at 12 29 41 AM" src="https://github.com/user-attachments/assets/1866bb4f-718d-40ab-b845-ce3f6f8a76a2" />
*Example conversations showing the bot's ability to answer questions about Angel One services and handle out-of-scope queries*

## 🏗️ Project Structure

```
angel-assist/
├── data/                          # Data storage directory
│   ├── docx/                     # Word documents
│   ├── pdfs/                     # Insurance PDFs and documentation
│   └── scraped_pages/            # Scraped web content from Angel One support
├── .dockerignore                 # Docker ignore file
├── Dockerfile                    # Container configuration
├── chatbot_interface.py          # Web interface implementation
├── ingest_data.py               # Data preprocessing and ingestion
├── main.py                      # Main application entry point
├── models.py                    # Data models and schemas
├── rag_chain.py                 # RAG pipeline implementation
├── railway.json                 # Railway deployment configuration
├── requirements.txt             # Python dependencies
└── start.py                     # Application startup script
```

## ✨ Key Features

- **Intelligent Query Processing**: Uses RAG architecture to provide contextual answers
- **Source-Based Responses**: Only answers questions based on Angel One's official documentation
- **Fallback Handling**: Responds with "I don't know" for out-of-scope queries
- **User-Friendly Interface**: Clean, responsive chat interface
- **Multi-Format Support**: Processes PDFs, DOCX, and web content
- **Real-time Interaction**: Fast response times with streaming capabilities

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip package manager
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd angel-one-rag-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create a .env file with necessary API keys
   echo "OPENAI_API_KEY=your_openai_api_key" > .env
   # Add other required environment variables
   ```

4. **Ingest data**
   ```bash
   python ingest_data.py
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t angel-one-chatbot .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 angel-one-chatbot
   ```

## 🔧 Configuration

### Data Sources

The chatbot is trained on:
- **Web Content**: All pages from https://www.angelone.in/support
- **Insurance PDFs**: Official insurance documentation
- **Support Documentation**: Various support materials in DOCX format

### RAG Pipeline

The system implements a sophisticated RAG pipeline that:
1. Processes and chunks documents from multiple sources
2. Creates embeddings for efficient similarity search
3. Retrieves relevant context for user queries
4. Generates responses using language models
5. Validates responses against source material

## 🎮 Usage

### Web Interface

1. Access the chatbot at `http://localhost:8000`
2. Type your question in the input field
3. The bot will respond with relevant information from Angel One's documentation
4. For questions outside the scope, it will respond with "I don't know"

### API Endpoints

The application provides RESTful API endpoints for programmatic access:

- `POST /chat`: Send a message to the chatbot
- `GET /health`: Health check endpoint

### Example Queries

**✅ Supported Queries:**
- "What is Angel One?"
- "How does it suggest stocks for short term trading?"
- "What are the insurance policies available?"
- "How to open a trading account?"

**❌ Out-of-scope Queries:**
- "What is Motilal Oswal?" (responds with "I don't know")
- General questions not related to Angel One services

## 🛠️ Technical Implementation

### Architecture

The chatbot follows a modular architecture:

1. **Data Ingestion Layer** (`ingest_data.py`): Processes various document formats
2. **RAG Chain** (`rag_chain.py`): Implements retrieval and generation logic
3. **Models** (`models.py`): Defines data structures and schemas
4. **Interface Layer** (`chatbot_interface.py`): Handles user interactions
5. **Main Application** (`main.py`): Orchestrates all components

## 🌐 Deployment

### Live Demo

The chatbot is deployed and accessible at: [Your Deployment URL]

### Railway Deployment

The project is configured for Railway deployment with:
- Automatic builds from Git commits
- Environment variable management
- Scalable hosting infrastructure

## 📝 Key Requirements Fulfilled

- ✅ **Source-based Responses**: Only answers based on provided Angel One documentation
- ✅ **Fallback Handling**: Returns "I don't know" for out-of-scope queries
- ✅ **User-friendly Interface**: Clean, intuitive chat interface
- ✅ **Web Hosted**: Functional prototype deployed and accessible
- ✅ **Complete Documentation**: Comprehensive setup and usage instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

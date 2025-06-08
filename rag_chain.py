import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()


class AngelOneRAGChain:
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        self.llm = None
        self.chain = None
        self.setup_components()
        self.embeddings = None

    def setup_components(self):
        """Initialize all RAG components"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                encode_kwargs={'model_name': "sentence-transformers/all-MiniLM-L3-v2"}
            )
            print("Using sentence-transformers/all-MiniLM-L3-v2")
        except Exception as e:
            raise Exception("Could not initialize any embedding model. Please check your setup.")

        # Load vector store
        self.load_vector_store()

        # Initialize LLM
        self.setup_llm()

        # Create retrieval chain
        self.setup_chain()

    def load_vector_store(self):
        """Load the Chroma vector store"""
        try:
            # Load Chroma vector store
            self.vector_store = Chroma(
                persist_directory="chroma_db",
                embedding_function=self.embeddings
            )

            # Setup retriever with specific parameters
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}  # Retrieve top 5 most similar chunks
            )

            # Load metadata if exists
            try:
                with open("chroma_db/metadata.json", "r") as f:
                    self.metadata = json.load(f)
                    print(f"Loaded vector store with {self.metadata.get('total_chunks', 'unknown')} chunks")
            except FileNotFoundError:
                # Try to get collection info from Chroma
                try:
                    collection = self.vector_store.collection
                    total_chunks = collection.count()
                    self.metadata = {"total_chunks": total_chunks}
                    print(f"Loaded Chroma vector store with {total_chunks} chunks")
                except Exception as e:
                    self.metadata = {}
                    print("Loaded Chroma vector store (chunk count unknown)")

        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            raise

    def setup_llm(self):
        """Initialize the language model"""
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=openai_api_key
        )

    def setup_chain(self):
        """Setup the RAG chain with custom prompt"""

        # Custom prompt template
        template = """You are an Angel One customer support assistant. Answer questions based ONLY on the provided context from Angel One's official documentation and insurance policies.

                    IMPORTANT RULES:
                    1. Only answer questions using information from the provided context
                    2. If the context doesn't contain enough information to answer the question, respond with "I don't know."
                    3. Be helpful and specific when you can answer based on the context
                    4. Always mention relevant policy numbers, charges, or specific procedures when available in the context
                    5. Format your response clearly and professionally
                    
                    Context: {context}
                    
                    Question: {question}
                    
                    Answer:"""

        self.prompt = ChatPromptTemplate.from_template(template)

        # Create the chain
        self.chain = (
                {
                    "context": self.retriever | self._format_docs,
                    "question": RunnablePassthrough()
                }
                | self.prompt
                | self.llm
                | StrOutputParser()
        )

    def _format_docs(self, docs):
        """Format retrieved documents for the prompt"""
        if not docs:
            return "No relevant information found."

        formatted_docs = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            doc_type = doc.metadata.get("type", "document")

            formatted_doc = f"Document {i} (Source: {source}, Type: {doc_type}):\n{doc.page_content}\n"
            formatted_docs.append(formatted_doc)

        return "\n".join(formatted_docs)

    def ask_question(self, question: str) -> dict:
        """
        Ask a question and get an answer from the RAG system

        Args:
            question (str): The user's question

        Returns:
            dict: Contains answer, sources, and metadata
        """
        try:
            # Get relevant documents first to check if we have context
            # Use invoke instead of deprecated get_relevant_documents
            relevant_docs = self.retriever.invoke(question)

            if not relevant_docs:
                return {
                    "answer": "I don't know.",
                    "sources": [],
                    "confidence": "low"
                }

            # Generate answer using the chain
            answer = self.chain.invoke(question)

            # Extract sources
            sources = []
            for doc in relevant_docs:
                source_info = {
                    "source": doc.metadata.get("source", "Unknown"),
                    "type": doc.metadata.get("type", "document"),
                    "title": doc.metadata.get("title", "")
                }
                if source_info not in sources:
                    sources.append(source_info)

            # Determine confidence based on answer content
            confidence = "high" if "I don't know" not in answer else "low"

            return {
                "answer": answer,
                "sources": sources[:3],
                "confidence": confidence
            }

        except Exception as e:
            print(f"Error processing question: {str(e)}")
            return {
                "answer": "I encountered an error while processing your question. Please try again or contact support.",
                "sources": [],
                "confidence": "error"
            }

    def get_similar_questions(self, question: str, num_questions: int = 3) -> list:
        """Get similar questions based on document content"""
        try:
            # Use invoke instead of deprecated method
            docs = self.retriever.invoke(question)

            # Extract potential questions from document content
            similar_questions = []
            for doc in docs[:num_questions]:
                content = doc.page_content
                # Simple heuristic to find question-like content
                sentences = content.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if ('?' in sentence or
                            sentence.lower().startswith(
                                ('what', 'how', 'when', 'where', 'why', 'can', 'do', 'is', 'are'))):
                        if len(sentence) > 10 and len(sentence) < 100:
                            similar_questions.append(sentence)
                            if len(similar_questions) >= num_questions:
                                break
                if len(similar_questions) >= num_questions:
                    break

            return similar_questions[:num_questions]
        except:
            return []

    def health_check(self) -> dict:
        """Check if the RAG system is working properly"""
        try:
            test_question = "What is Angel One?"
            result = self.ask_question(test_question)

            return {
                "status": "healthy",
                "vector_store_loaded": self.vector_store is not None,
                "total_documents": self.metadata.get("total_chunks", 0),
                "test_query_successful": result["confidence"] != "error"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "vector_store_loaded": False
            }


# Global instance
rag_chain = None


def get_rag_chain():
    """Get or create the RAG chain instance"""
    global rag_chain
    if rag_chain is None:
        rag_chain = AngelOneRAGChain()
    return rag_chain


if __name__ == "__main__":
    # Test the RAG chain
    print("Testing RAG Chain...")

    try:
        chain = AngelOneRAGChain()

        # Health check
        health = chain.health_check()
        print(f"Health check: {health}")

        # Test questions
        test_questions = [
            "What is Angel One?",
            "How do I open an account?",
            "What are the trading charges?",
            "What is the process for account closure?"
        ]

        for question in test_questions:
            print(f"\nQ: {question}")
            result = chain.ask_question(question)
            print(f"A: {result['answer'][:200]}...")
            print(f"Sources: {len(result['sources'])}")
            print(f"Confidence: {result['confidence']}")

    except Exception as e:
        print(f"Error testing RAG chain: {str(e)}")

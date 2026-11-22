Palm Mind AI — RAG Backend

A modular backend application built with FastAPI that supports document ingestion, retrieval-augmented generation (RAG), conversational memory, and interview booking requests.

Features:
Document Upload & Extraction: Upload documents and extract their text content.
Text Chunking: Split extracted text into smaller chunks using configurable chunking strategies.
Embeddings: Generate vector embeddings using Google's Gemini embedding model.
Vector Storage & Retrieval: Store document embeddings in Qdrant and retrieve relevant chunks for user queries.
RAG Chat: Generate responses grounded in uploaded documents using retrieved context.
Conversational Memory: Maintain session-based conversation context using Redis.
Booking Requests: Extract booking details from user messages, create booking requests, and retrieve bookings by ID.
Persistent Storage: Store document metadata and booking records in PostgreSQL.
Containerized Setup: Run the application and supporting services using Docker Compose.

Tech Stack:
-Python 3.11
-FastAPI
-Google Gemini API
-Qdrant
-PostgreSQL
-Redis
-Docker & Docker Compose
-Pytest

Architecture:
1.A client sends requests to the FastAPI API.
2.Uploaded documents are processed and their text is extracted.
3.The text is split into chunks.
4.Gemini generates embeddings for the chunks.
5.Embeddings and chunk metadata are stored in Qdrant.
6.A user asks a question through the chat API.
7.Relevant chunks are retrieved from Qdrant and used as context for the LLM response.
8.Redis maintains session conversation memory.
9.Booking requests are extracted and stored in PostgreSQL; booking details can be retrieved by ID.

Prerequisites:
-Python 3.11
-Docker Desktop
-Docker Compose
-A Google Gemini API key

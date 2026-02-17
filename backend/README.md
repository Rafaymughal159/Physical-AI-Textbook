# RAG Data Ingestion Pipeline

This pipeline crawls Docusaurus documentation sites, extracts and cleans text content, generates embeddings using Cohere, and stores them in Qdrant vector database for semantic search capabilities.

## Prerequisites

- Python 3.11+
- pip package manager
- Access to Cohere API (sign up at https://cohere.com)
- Qdrant Cloud account (sign up at https://qdrant.tech)

## Setup

1. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   # Or if using uv:
   uv pip install requests beautifulsoup4 cohere qdrant-client python-dotenv
   ```

2. Configure environment variables by copying the example:
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` with your actual API keys and URLs:
   ```env
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_URL=your_qdrant_cluster_url_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   DOCS_BASE_URL=https://ai-textbook-hazel.vercel.app/
   CHUNK_SIZE_CHARS=2000
   OVERLAP_CHARS=200
   BATCH_SIZE=32
   MAX_RETRIES=3
   BACKOFF_FACTOR=1.0
   ```

## Usage

Run the complete ingestion pipeline:
```bash
cd backend
python -m rag_ingestion.main
```

## Configuration Options

- `CHUNK_SIZE_CHARS`: Size of text chunks in characters (default: 2000)
- `OVERLAP_CHARS`: Overlap between chunks in characters (default: 200)
- `BATCH_SIZE`: Number of items to process in each batch (default: 32)
- `MAX_RETRIES`: Maximum retry attempts for failed operations (default: 3)
- `BACKOFF_FACTOR`: Factor for exponential backoff (default: 1.0)

## Architecture

The pipeline consists of the following stages:

1. **URL Discovery**: Crawls the Docusaurus site to find all accessible pages
2. **Content Extraction**: Extracts and cleans text content from each page
3. **Text Chunking**: Splits content into manageable chunks for embedding
4. **Embedding Generation**: Creates vector embeddings using Cohere API
5. **Vector Storage**: Stores embeddings in Qdrant with associated metadata

## Error Handling

The pipeline includes robust error handling with:
- Exponential backoff for API rate limits
- Comprehensive logging for debugging
- Individual URL failure isolation
- Progress tracking to resume interrupted processes

## Logging

Logs are written to both console and `rag_pipeline.log` file with detailed information about the ingestion process.
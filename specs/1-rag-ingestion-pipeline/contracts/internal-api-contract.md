# Internal API Contract: RAG Ingestion Pipeline

## Overview
This document defines the internal function interfaces for the RAG ingestion pipeline implemented in `main.py`.

## Function Contracts

### `get_all_URLs(base_url: str) -> List[str]`
**Purpose**: Discover and return all publicly accessible URLs from the Docusaurus site

**Parameters**:
- `base_url` (str): The base URL of the Docusaurus site to crawl

**Returns**:
- `List[str]`: List of all discovered URLs

**Errors**:
- Raises exception if base URL is inaccessible

### `extract_text_from_URL(url: str) -> Dict[str, str]`
**Purpose**: Extract and clean text content from a single URL

**Parameters**:
- `url` (str): The URL to extract content from

**Returns**:
- `Dict[str, str]`: Dictionary with keys 'url', 'title', 'content'

**Errors**:
- Returns dictionary with error information if extraction fails

### `Chunk_text(content: str, chunk_size_chars: int = 2000, overlap_chars: int = 200) -> List[Dict[str, str]]`
**Purpose**: Split content into overlapping chunks of specified size

**Parameters**:
- `content` (str): The content to chunk
- `chunk_size_chars` (int): Target size of each chunk in characters (default 2000 ≈ 500 tokens)
- `overlap_chars` (int): Overlap between chunks in characters (default 200)

**Returns**:
- `List[Dict[str, str]]`: List of chunk dictionaries with content and metadata

### `embed(texts: List[str]) -> List[List[float]]`
**Purpose**: Generate embeddings for a list of text strings using Cohere

**Parameters**:
- `texts` (List[str]): List of text strings to embed

**Returns**:
- `List[List[float]]`: List of embedding vectors (each 1024-dimensional)

**Errors**:
- Handles API rate limits and retries appropriately

### `create_collection(collection_name: str = "rag_embedding") -> bool`
**Purpose**: Create or verify existence of Qdrant collection

**Parameters**:
- `collection_name` (str): Name of the collection to create (default "rag_embedding")

**Returns**:
- `bool`: True if collection exists/created successfully

### `save_chunk_to_qdrant(chunk_data: Dict, collection_name: str = "rag_embedding") -> bool`
**Purpose**: Save a single chunk with its embedding to Qdrant

**Parameters**:
- `chunk_data` (Dict): Dictionary containing chunk content, embedding, and metadata
- `collection_name` (str): Name of the collection to save to

**Returns**:
- `bool`: True if save operation succeeded

### `main() -> None`
**Purpose**: Execute the complete RAG ingestion pipeline

**Parameters**: None (reads configuration from environment variables)

**Returns**: None (executes pipeline and reports status)
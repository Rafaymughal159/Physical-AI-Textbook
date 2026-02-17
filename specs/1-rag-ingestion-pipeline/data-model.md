# Data Model: RAG Data Ingestion Pipeline

## Overview
This document defines the key data structures and entities used in the RAG data ingestion pipeline.

## Core Entities

### Document
Represents a web page extracted from the Docusaurus site

**Fields**:
- `url` (string): The source URL of the document
- `title` (string): The title of the page
- `content` (string): The cleaned text content of the page
- `hash` (string): Unique hash of the content for change detection
- `created_at` (datetime): Timestamp when the document was processed
- `updated_at` (datetime): Timestamp when the document was last updated

**Relationships**:
- Zero-to-many Chunks (one document can be split into multiple chunks)

### Chunk
Represents a segment of a document that has been processed for embedding

**Fields**:
- `id` (string): Unique identifier for the chunk
- `document_url` (string): Reference to the source document URL
- `content` (string): The text content of the chunk
- `token_count` (int): Estimated number of tokens in the chunk
- `position` (int): Position of the chunk within the original document
- `embedding` (list[float]): The vector embedding of the content (1024 dimensions)

**Validation rules**:
- Content length should be between 1600-2400 characters (approx 400-600 tokens)
- Position must be non-negative
- Embedding must have exactly 1024 dimensions

### EmbeddingResult
Represents the result of embedding generation for a batch of chunks

**Fields**:
- `chunk_ids` (list[string]): List of chunk IDs that were embedded
- `vectors` (list[list[float]]): List of embedding vectors (each 1024-dimensional)
- `success` (bool): Whether the embedding operation succeeded
- `error_message` (string, optional): Error message if operation failed

### CrawlResult
Represents the result of crawling and extracting content from a URL

**Fields**:
- `url` (string): The URL that was crawled
- `title` (string): Extracted page title
- `content` (string): Extracted and cleaned content
- `status_code` (int): HTTP status code of the response
- `success` (bool): Whether the crawl operation succeeded
- `error_message` (string, optional): Error message if operation failed

## State Transitions

### Document States
1. **Crawled**: Document has been successfully extracted from the web
2. **Cleaned**: HTML and non-content elements have been removed
3. **Chunked**: Document has been divided into processable chunks
4. **Embedded**: All chunks have been converted to vector embeddings
5. **Stored**: Embeddings have been saved to Qdrant vector database
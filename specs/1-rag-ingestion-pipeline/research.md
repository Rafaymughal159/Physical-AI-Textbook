# Research: RAG Data Ingestion Pipeline

## Overview
This document consolidates research findings for implementing the RAG data ingestion pipeline that crawls Docusaurus content, generates embeddings using Cohere, and stores vectors in Qdrant Cloud.

## Decision: Web Scraping Approach
**Rationale**: For crawling the Docusaurus GitHub Pages website, we'll use `requests` and `beautifulsoup4` as they provide reliable HTML parsing and are commonly used for this purpose. Docusaurus sites are static and well-structured, making them suitable for traditional web scraping techniques.

**Alternatives considered**:
- Selenium: More complex, requires browser automation, unnecessary overhead
- Playwright: Similar to Selenium, adds complexity without significant benefits for static sites
- Direct API: Docusaurus GitHub Pages doesn't expose a content API

## Decision: Text Extraction and Cleaning
**Rationale**: Beautiful Soup will be used to extract main content from Docusaurus pages by targeting specific CSS selectors that contain the main documentation content. We'll strip HTML tags, navigation elements, and other non-content elements.

**Common Docusaurus selectors for main content**:
- `.theme-doc-markdown` - Main documentation content area
- `.markdown` - Markdown-rendered content
- `[role="main"]` - Main content area

## Decision: Text Chunking Strategy
**Rationale**: For chunking text into 400-600 token ranges with overlap, we'll use a character-based approach initially since we can estimate that ~1 token ≈ 4 characters for English text. This gives us a rough range of 1600-2400 characters per chunk with appropriate overlap.

**Implementation approach**:
- Split text into overlapping windows of appropriate size
- Ensure sentence boundaries aren't broken mid-chunk
- Maintain context with overlapping segments

## Decision: Cohere Embedding Model
**Rationale**: Cohere's embed-multilingual-v3.0 model is ideal for this use case as it handles technical documentation well and supports multiple languages. The model produces 1024-dimensional embeddings which are efficient for similarity search.

**Batch processing approach**:
- Process texts in batches (max 96 texts per request for optimal performance)
- Implement retry logic for API failures
- Handle rate limiting with exponential backoff

## Decision: Qdrant Vector Database Setup
**Rationale**: Qdrant Cloud provides a managed vector database solution that's perfect for RAG applications. We'll create a collection with cosine distance metric for semantic similarity search.

**Collection configuration**:
- Collection name: `rag_embedding` (as specified)
- Vector size: 1024 (to match Cohere embeddings)
- Distance metric: Cosine
- Payload schema: Include document metadata (URL, title, content hash)

## Decision: Error Handling and Resilience
**Rationale**: The pipeline needs to handle various failure modes gracefully including network timeouts, API rate limits, and transient errors.

**Implementation approach**:
- Exponential backoff for API calls
- Retry mechanisms with configurable attempts
- Progress tracking to enable resume functionality
- Comprehensive logging for debugging

## Decision: Environment Configuration
**Rationale**: Following security best practices, all sensitive information (API keys) and configuration will be managed through environment variables.

**Required environment variables**:
- `COHERE_API_KEY`: Cohere API key
- `QDRANT_URL`: Qdrant Cloud cluster URL
- `QDRANT_API_KEY`: Qdrant Cloud API key
- `DOCS_BASE_URL`: Base URL of the Docusaurus site to crawl
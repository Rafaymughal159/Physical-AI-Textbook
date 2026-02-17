"""
RAG Data Ingestion Pipeline for Docusaurus Content

This module implements a complete pipeline for:
1. Crawling Docusaurus documentation sites
2. Extracting and cleaning text content
3. Generating embeddings using Cohere
4. Storing embeddings in Qdrant vector database
"""

import os
import time
import hashlib
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('rag_pipeline.log'),
            logging.StreamHandler()
        ]
    )

    # Set lower levels for specific loggers if needed
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client").setLevel(logging.WARNING)


def get_config():
    """Load configuration from environment variables"""
    config = {
        'cohere_api_key': os.getenv('COHERE_API_KEY'),
        'qdrant_url': os.getenv('QDRANT_URL'),
        'qdrant_api_key': os.getenv('QDRANT_API_KEY'),
        'docs_base_url': os.getenv('DOCS_BASE_URL', 'https://ai-textbook-hazel.vercel.app/'),
        'chunk_size_chars': int(os.getenv('CHUNK_SIZE_CHARS', '2000')),
        'overlap_chars': int(os.getenv('OVERLAP_CHARS', '200')),
        'batch_size': int(os.getenv('BATCH_SIZE', '32')),
        'max_retries': int(os.getenv('MAX_RETRIES', '3')),
        'backoff_factor': float(os.getenv('BACKOFF_FACTOR', '1.0'))
    }

    # Validate required configuration
    required_keys = ['cohere_api_key', 'qdrant_url', 'qdrant_api_key']
    missing_keys = [key for key in required_keys if not config[key]]
    if missing_keys:
        raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")

    return config


def retry_on_failure(max_retries: int = 3, backoff_factor: float = 1.0):
    """
    Decorator to retry functions on failure with exponential backoff
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        logging.error(f"All {max_retries} attempts failed for {func.__name__}: {e}")
                        raise e
                    sleep_time = backoff_factor * (2 ** attempt)
                    logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
            return None
        return wrapper
    return decorator


def calculate_content_hash(content: str) -> str:
    """Calculate SHA-256 hash of content for change detection"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def validate_url(url: str) -> bool:
    """Validate if a string is a properly formatted URL"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


# Placeholder functions that will be implemented in subsequent tasks
@retry_on_failure(max_retries=3, backoff_factor=1.0)
def get_all_URLs(base_url: str) -> List[str]:
    """
    Discover and return all publicly accessible URLs from the Docusaurus site

    Args:
        base_url: The base URL of the Docusaurus site to crawl

    Returns:
        List of all discovered URLs
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting URL discovery from: {base_url}")

    urls = set()
    visited = set()

    # Normalize base URL to ensure proper format
    parsed_base = urllib.parse.urlparse(base_url)
    base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"

    # Queue for BFS traversal
    to_visit = [base_url]

    while to_visit:
        current_url = to_visit.pop(0)

        # Skip if already visited
        if current_url in visited:
            continue

        visited.add(current_url)

        try:
            # Fetch the page
            response = requests.get(current_url, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {current_url}: Status {response.status_code}")
                continue

            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Add current URL to our list
            urls.add(current_url)

            # Find all links on the page
            for link in soup.find_all('a', href=True):
                href = link['href']

                # Convert relative URLs to absolute
                absolute_url = urllib.parse.urljoin(current_url, href)

                # Only include URLs from the same domain and with proper structure
                parsed_href = urllib.parse.urlparse(absolute_url)
                if (parsed_href.netloc == parsed_base.netloc and
                    absolute_url.startswith(base_domain) and
                    absolute_url.endswith(('.html', '/')) and
                    '#' not in absolute_url):  # Avoid anchor links

                    # Avoid duplicate URLs with and without trailing slash
                    normalized_url = absolute_url.rstrip('/')
                    if normalized_url not in visited and len(urls) < 1000:  # Limit to prevent infinite crawling
                        to_visit.append(normalized_url)

        except requests.RequestException as e:
            logger.error(f"Error fetching {current_url}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error processing {current_url}: {e}")
            continue

    logger.info(f"Discovered {len(urls)} URLs from {base_url}")
    return list(urls)


@retry_on_failure(max_retries=3, backoff_factor=1.0)
def extract_text_from_URL(url: str) -> Dict[str, str]:
    """
    Extract and clean text content from a single URL

    Args:
        url: The URL to extract content from

    Returns:
        Dictionary with keys 'url', 'title', 'content', 'status_code', 'success', 'error_message'
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Extracting content from URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        status_code = response.status_code

        if response.status_code != 200:
            return {
                'url': url,
                'title': '',
                'content': '',
                'status_code': status_code,
                'success': False,
                'error_message': f'HTTP {status_code}: Failed to fetch URL'
            }

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract page title from <title> tag first
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else 'No Title'

        # Initialize content parts
        content_parts = []

        # Try to find the main hero section content for the homepage
        left_content = soup.select_one('.leftContent')
        if left_content:
            h1_title = left_content.select_one('.hero__title')
            if h1_title:
                content_parts.append(h1_title.get_text(strip=True))
            subtitle = left_content.select_one('.hero__subtitle')
            if subtitle:
                content_parts.append(subtitle.get_text(strip=True))
            button_link = left_content.select_one('.buttons a')
            if button_link:
                content_parts.append(button_link.get_text(strip=True))

        # Also try to extract content from standard Docusaurus selectors for doc pages
        standard_content_selectors = [
            '.theme-doc-markdown',  # Main documentation content area
            '.markdown',           # Markdown-rendered content
            '[role="main"]',       # Main content area
            'main',                # Main content area
            '.container',          # Container divs that often hold content
            '.docItemContainer',   # Docusaurus doc item container
            '.docs-doc-id-*'       # Docusaurus specific class pattern
        ]

        for selector in standard_content_selectors:
            if '*' in selector:
                for tag in soup.find_all(True):
                    classes = tag.get('class', [])
                    if classes and any(cls.startswith('docs-doc-id-') for cls in classes):
                        content_parts.append(tag.get_text(separator='\n', strip=True))
                        break
            else:
                element = soup.select_one(selector)
                if element:
                    content_parts.append(element.get_text(separator='\n', strip=True))

        # If no specific content found, fallback to body but after cleaning
        if not content_parts and soup.find('body'):
            # Remove unwanted elements before extracting from body
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            body_content = soup.find('body').get_text(separator='\n', strip=True)
            if body_content:
                content_parts.append(body_content)

        # Combine all extracted content parts
        full_content = '\n\n'.join(filter(None, content_parts)) # Filter out empty strings

        # Clean up the combined content - remove extra whitespace and empty lines
        lines = [line.strip() for line in full_content.split('\n')]
        cleaned_lines = [line for line in lines if line]
        content = '\n'.join(cleaned_lines)

        logger.info(f"Successfully extracted content from {url} ({len(content)} characters)")

        return {
            'url': url,
            'title': title,
            'content': content,
            'status_code': status_code,
            'success': True,
            'error_message': None
        }

    except requests.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(error_msg)
        return {
            'url': url,
            'title': '',
            'content': '',
            'status_code': 0,
            'success': False,
            'error_message': error_msg
        }
    except Exception as e:
        error_msg = f"Extraction error: {str(e)}"
        logger.error(error_msg)
        return {
            'url': url,
            'title': '',
            'content': '',
            'status_code': 0,
            'success': False,
            'error_message': error_msg
        }


def Chunk_text(content: str, chunk_size_chars: int = 2000, overlap_chars: int = 200) -> List[Dict[str, str]]:
    """
    Split content into overlapping chunks of specified size

    Args:
        content: The content to chunk
        chunk_size_chars: Target size of each chunk in characters (default 2000 ≈ 500 tokens)
        overlap_chars: Overlap between chunks in characters (default 200)

    Returns:
        List of chunk dictionaries with content and metadata
    """
    logger = logging.getLogger(__name__)

    if not content:
        return []

    chunks = []
    start = 0
    content_length = len(content)

    if content_length <= chunk_size_chars:
        # If content is smaller than or equal to chunk size, return it as a single chunk
        chunk_data = {
            'content': content,
            'start_pos': 0,
            'end_pos': content_length,
            'length': content_length,
        }
        chunks.append(chunk_data)
        return chunks

    while start < content_length:
        end = min(start + chunk_size_chars, content_length)
        chunk_text = content[start:end]

        if not chunk_text:  # Prevent empty chunks and infinite loops for edge cases
            break

        chunk_data = {
            'content': chunk_text,
            'start_pos': start,
            'end_pos': end,
            'length': len(chunk_text),
        }
        chunks.append(chunk_data)

        # Calculate next start position with overlap, ensuring it doesn't go backwards
        next_start = end - overlap_chars
        start = max(0, next_start)

        # If start didn't advance, it means we've processed all we can with overlap
        if start >= end:
            break # Exit to prevent infinite loop if overlap causes no progress

    logger.info(f"Content chunked into {len(chunks)} pieces (avg {sum(c['length'] for c in chunks) // len(chunks) if chunks else 0} chars)")
    return chunks


@retry_on_failure(max_retries=3, backoff_factor=1.0)
def embed(texts: List[str], cohere_client=None) -> List[List[float]]:
    """
    Generate embeddings for a list of text strings using Cohere

    Args:
        texts: List of text strings to embed
        cohere_client: Initialized Cohere client (optional, will be created if not provided)

    Returns:
        List of embedding vectors (each 1024-dimensional)
    """
    logger = logging.getLogger(__name__)

    if not texts:
        return []

    # Use the global cohere_client if not provided
    if cohere_client is None:
        config = get_config()
        cohere_client = cohere.Client(config['cohere_api_key'])

    logger.info(f"Generating embeddings for {len(texts)} text chunks...")

    try:
        # Call Cohere's embed API
        response = cohere_client.embed(
            texts=texts,
            model="embed-multilingual-v3.0",  # Using multilingual model for broad compatibility
            input_type="search_document"  # Optimize for search use case
        )

        embeddings = response.embeddings
        logger.info(f"Successfully generated {len(embeddings)} embeddings of dimension {len(embeddings[0]) if embeddings else 0}")

        return embeddings

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise


def create_collection(qdrant_client=None, collection_name: str = "rag_embedding") -> bool:
    """
    Create or verify existence of Qdrant collection

    Args:
        qdrant_client: Initialized Qdrant client (optional, will be created if not provided)
        collection_name: Name of the collection to create (default "rag_embedding")

    Returns:
        True if collection exists/created successfully
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Creating/verifying Qdrant collection: {collection_name}")

    # Use the global qdrant_client if not provided
    if qdrant_client is None:
        config = get_config()
        qdrant_client = QdrantClient(
            url=config['qdrant_url'],
            api_key=config['qdrant_api_key']
        )

    try:
        # Check if collection already exists
        collections = qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]

        if collection_name in collection_names:
            logger.info(f"Collection '{collection_name}' already exists")
            return True

        # Create the collection with 1024-dimensional vectors (for Cohere embeddings)
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )

        logger.info(f"Collection '{collection_name}' created successfully")
        return True

    except Exception as e:
        logger.error(f"Error creating collection '{collection_name}': {e}")
        return False


def save_chunk_to_qdrant(chunk_data: Dict, qdrant_client=None, collection_name: str = "rag_embedding") -> bool:
    """
    Save a single chunk with its embedding to Qdrant

    Args:
        chunk_data: Dictionary containing chunk content, embedding, and metadata
        qdrant_client: Initialized Qdrant client (optional, will be created if not provided)
        collection_name: Name of the collection to save to

    Returns:
        True if save operation succeeded
    """
    logger = logging.getLogger(__name__)

    # Use the global qdrant_client if not provided
    if qdrant_client is None:
        config = get_config()
        qdrant_client = QdrantClient(
            url=config['qdrant_url'],
            api_key=config['qdrant_api_key']
        )

    try:
        # Extract required fields from chunk_data
        content = chunk_data.get('content', '')
        embedding = chunk_data.get('embedding', [])
        document_url = chunk_data.get('document_url', '')
        chunk_id = chunk_data.get('id', hashlib.md5((content + document_url).encode()).hexdigest())

        # Prepare payload with metadata
        payload = {
            'content': content,
            'document_url': document_url,
            'title': chunk_data.get('title', ''),
            'content_hash': calculate_content_hash(content),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'chunk_position': chunk_data.get('position', 0),
            'token_count': chunk_data.get('token_count', len(content.split()))
        }

        # Add any additional metadata from chunk_data
        for key, value in chunk_data.items():
            if key not in ['content', 'embedding', 'document_url', 'id', 'title', 'position', 'token_count']:
                payload[key] = value

        # Prepare point to be inserted
        point = PointStruct(
            id=chunk_id,
            vector=embedding,
            payload=payload
        )

        # Upsert the point into the collection
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[point]
        )

        logger.info(f"Chunk saved to Qdrant with ID: {chunk_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving chunk to Qdrant: {e}")
        return False


def main():
    """Execute the complete RAG ingestion pipeline"""
    # Setup logging
    setup_logging()

    # Load configuration
    config = get_config()

    logger = logging.getLogger(__name__)
    logger.info("Starting RAG ingestion pipeline...")

    # Initialize clients
    cohere_client = cohere.Client(config['cohere_api_key'])
    qdrant_client = QdrantClient(
        url=config['qdrant_url'],
        api_key=config['qdrant_api_key']
    )

    logger.info("Clients initialized successfully")

    # Create Qdrant collection
    logger.info("Creating Qdrant collection...")
    if not create_collection(qdrant_client, "rag_embedding"):
        logger.error("Failed to create Qdrant collection")
        return

    # Get all URLs from the Docusaurus site
    logger.info(f"Discovering URLs from: {config['docs_base_url']}")
    urls = get_all_URLs(config['docs_base_url'])
    logger.info(f"Discovered {len(urls)} URLs")

    # Process each URL
    processed_count = 0
    failed_count = 0

    for i, url in enumerate(urls):
        logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")

        # Extract content from URL
        extraction_result = extract_text_from_URL(url)
        if not extraction_result['success']:
            logger.error(f"Failed to extract content from {url}: {extraction_result['error_message']}")
            failed_count += 1
            continue

        # Chunk the content
        content = extraction_result['content']
        title = extraction_result['title']
        chunks = Chunk_text(content, config['chunk_size_chars'], config['overlap_chars'])

        logger.info(f"Content from {url} chunked into {len(chunks)} pieces")

        # Process chunks in batches for embedding
        for j, chunk in enumerate(chunks):
            try:
                # Generate embedding for the chunk
                embeddings = embed([chunk['content']], cohere_client)
                if not embeddings or len(embeddings) == 0:
                    logger.warning(f"No embeddings generated for chunk {j} of {url}")
                    continue

                chunk_embedding = embeddings[0]

                # Prepare chunk data for storage
                chunk_data = {
                    'id': hashlib.md5((chunk['content'] + url + str(j)).encode()).hexdigest(),
                    'content': chunk['content'],
                    'embedding': chunk_embedding,
                    'document_url': url,
                    'title': title,
                    'position': j,
                    'token_count': len(chunk['content'].split()),
                    'start_pos': chunk['start_pos'],
                    'end_pos': chunk['end_pos']
                }

                # Save to Qdrant
                if save_chunk_to_qdrant(chunk_data, qdrant_client, "rag_embedding"):
                    logger.debug(f"Chunk {j} from {url} saved to Qdrant")
                else:
                    logger.error(f"Failed to save chunk {j} from {url} to Qdrant")
                    failed_count += 1

            except Exception as e:
                logger.error(f"Error processing chunk {j} from {url}: {e}")
                failed_count += 1
                continue

        processed_count += 1

    logger.info(f"Pipeline completed. Processed: {processed_count}, Failed: {failed_count}")
    logger.info("RAG ingestion pipeline finished.")


if __name__ == "__main__":
    main()
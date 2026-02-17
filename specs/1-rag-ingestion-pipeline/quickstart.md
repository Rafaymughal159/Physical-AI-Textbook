# Quickstart: RAG Data Ingestion Pipeline

## Prerequisites
- Python 3.11+
- pip package manager
- Access to Cohere API (sign up at https://cohere.com)
- Qdrant Cloud account (sign up at https://qdrant.tech)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create Backend Directory
```bash
mkdir backend
cd backend
```

### 3. Initialize Python Project
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install uv  # Install uv package manager
uv init  # Initialize project with uv
```

### 4. Install Dependencies
```bash
uv pip install requests beautifulsoup4 cohere qdrant-client python-dotenv
```

### 5. Configure Environment Variables
Create a `.env` file in the backend directory with the following content:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
DOCS_BASE_URL=https://physicalaitextbook.vercel.app/docs
```

### 6. Create the Main Application
Create `backend/main.py` with the implementation containing the required functions:
- `get_all_URLs()`
- `extract_text_from_URL()`
- `Chunk_text()`
- `embed()`
- `create_collection()`
- `save_chunk_to_qdrant()`
- Main execution function

### 7. Run the Pipeline
```bash
cd backend
python main.py
```

## Expected Output
The pipeline will:
1. Crawl all pages from the Docusaurus site
2. Extract and clean text content
3. Chunk the content into 400-600 token segments
4. Generate embeddings using Cohere
5. Store embeddings in Qdrant Cloud with metadata
6. Report completion statistics

## Troubleshooting
- If you get API rate limit errors, ensure your Cohere and Qdrant quotas are sufficient
- Check that all environment variables are properly set
- Verify that the Docusaurus site is accessible and not behind authentication
# cybertx-genai_assignment-
# FastAPI Document Ingestion and Query API

This FastAPI application allows users to ingest documents in PDF, DOC/DOCX, or TXT format, store their embeddings in a ChromaDB database, and then query those documents using semantic search. It leverages `sentence-transformers` to generate embeddings and `ChromaDB` for storage, enabling flexible, similarity-based searches.

## Features

- **Document Ingestion**: Supports ingestion of PDF, DOC/DOCX, and TXT files.
- **Embedding-Based Search**: Uses semantic embeddings to allow searching within documents.
- **Flexible Querying**: Accepts text queries and returns documents that are similar in meaning.

## Requirements

- Python 3.8 or above
- FastAPI
- ChromaDB
- Sentence Transformers
- PyMuPDF (`fitz`) for PDF processing
- `python-docx` for DOC/DOCX processing

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   
**Create and activate a virtual environment:**   
- python -m venv venv
- source venv/bin/activate  # On macOS/Linux
- venv\Scripts\activate     # On Windows
- pip install -r requirements.txt

**Run the FastAPI server:**
uvicorn main:app --reload # http://127.0.0.1:8000


## Usage

**Ingest Documents**
- To ingest documents, send a POST request to the /ingest/ endpoint with one or more files.
**Command**
- curl -X POST "http://127.0.0.1:8000/ingest/" -F "files=@path_to_your_file/l.txt"

**Query Documents**
- To search within ingested documents, send a POST request to the /query/ endpoint with a JSON body containing your query string.
**Command**
- curl -X POST "http://127.0.0.1:8000/query/" -H "Content-Type: application/json" -d "{\"query\": \"sample search term\"}"



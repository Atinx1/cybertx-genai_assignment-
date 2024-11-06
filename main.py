from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import asyncio
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import fitz
import docx
import uuid


'''
This FastAPI application provides endpoints to ingest files and query them based on semantic similarity. 
The application uses ChromaDB to store documents and Sentence Transformers to generate embeddings.
The /ingest/ endpoint accepts PDF, DOC/DOCX, or TXT files, extracts their text, generates embeddings, 
and stores the content with metadata in ChromaDB. The /query/ endpoint receives a text query, 
converts it  into an embedding, and searches the database for similar documents, 
returning matching filenames and document excerpts.
'''

app = FastAPI()
client = chromadb.Client(Settings(persist_directory='./chromadb_data'))
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
collection = client.get_or_create_collection(name="documents")

class QueryRequest(BaseModel):
    query: str

def extract_text_from_pdf(content: bytes) -> str:
    text = ""
    with fitz.open("pdf", content) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def extract_text_from_doc(content: bytes) -> str:
    doc = docx.Document(content)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

async def process_file(file: UploadFile) -> str:
    content = await file.read()
    if file.filename.endswith('.pdf'):
        return extract_text_from_pdf(content)
    elif file.filename.endswith(('.doc', '.docx')):
        return extract_text_from_doc(content)
    elif file.filename.endswith('.txt'):
        return content.decode('utf-8')
    else:
        raise HTTPException(status_code=415, detail="Unsupported file type")

async def process_and_store(file: UploadFile):
    text = await process_file(file)
    embedding = model.encode(text, convert_to_tensor=False)
    doc_id = str(uuid.uuid4())
    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[{"filename": file.filename}]
    )

@app.post("/ingest/")
async def ingest_documents(files: List[UploadFile]):
    try:
        tasks = [process_and_store(file) for file in files]
        await asyncio.gather(*tasks)
        print(f"Number of documents in collection after ingestion: {collection.count()}")
        return JSONResponse({"message": "Documents ingested successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/")
async def query_documents(request: Request):
    try:
        query_request = await request.json()
        print(f"Parsed query request: {query_request}")
        query_embedding = model.encode(query_request["query"], convert_to_tensor=False)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=1
        )
        if not results["results"]:
            raise ValueError("No results returned from collection.query")
        formatted_results = [
            {"filename": res["metadata"].get("filename", "unknown"), "text": res.get("document", "")}
            for res in results["results"][0]
        ]
        return JSONResponse({"results": formatted_results})

    except ValueError as ve:
        print(f"Value error: {ve}")
        raise HTTPException(status_code=500, detail=str(ve))
    except KeyError as ke:
        print(f"Key error: {ke}")
        raise HTTPException(status_code=500, detail=str(ke))
    except Exception as e:
        print(f"General error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

''' 
This functionality was tested using `l.txt` as a sample text file. The ingestion was tested with:
# curl -X POST "http://127.0.0.1:8000/ingest/" -F "files=@path_to_your_file/l.txt"
and querying was tested using:
# curl -X POST "http://127.0.0.1:8000/query/" -H "Content-Type: application/json" -d "{\"query\": \"Atin\"}"
This approach enables flexible, semantic searching within stored documents based on the provided input.
'''
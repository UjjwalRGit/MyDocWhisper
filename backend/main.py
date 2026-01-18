from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path
import shutil
from dotenv import load_dotenv
from vector_store_supabase import VectorStoreManager
from rag_pipeline import RAGPipeline
from fastapi.responses import StreamingResponse
from supabase import create_client
import tempfile

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not loaded")

app = FastAPI(
    title = "MyDocWhisper API", 
    version = "2.0",
    description = "RAG document chat now with streaming")

#CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
    "http://localhost:3000",
    "https://mydocwhisper.vercel.app",  # Add your actual Vercel URL
    "https://*.vercel.app"  # Allow preview deployments
    ],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# Storage
USE_SUPABASE_STORAGE = os.getenv("USE_SUPABASE_STORAGE", "false").lower() == "true"

# Initialize RAG pipline
vectorStore = VectorStoreManager(store_type = "auto")
ragPipeline = RAGPipeline(vector_store = vectorStore)
documentsStore = {}

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    documentId: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[dict]] = []

class UploadResponse(BaseModel):
    message: str
    documentId: str
    filename: str
    stats: dict

@app.get("/")
async def root():
    stats = ragPipeline.getStats()
    return {
        "message": "MyDocWhisper API v2.0 is running",
        "version": "2.0",
        "features": {
            "streaming": True,
            "chatHistory": True,
            "citations": True
        },
        "stats": stats
    }

# Upload and process a PDF Document (modified)
@app.post("/upload", response_model = UploadResponse)
async def uploadDocument(file: UploadFile = File(...)):
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    file.file.seek(0, 2) 
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code = 400, detail = "File too large. Maximum size is 50MB")

    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code = 400, detail = "Only PDF files are allowed")
    
    docId = file.filename.replace('.pdf', '').replace(' ', '_')

    try:
        if USE_SUPABASE_STORAGE and supabase:
            file_bytes = await file.read()
            storage_path = f"{docId}/{file.filename}"

            supabase.storage.from_("pdf-uploads").upload(
                storage_path, file_bytes, {"content-type": "application/pdf"}
            )

            # Download to temp file for processing
            with tempfile.NamedTemporaryFile(delete = False, suffix = '.pdf') as tmp:
                tmp.write(file_bytes)
                temp_path = tmp.name

            result = ragPipeline.processDocument(temp_path, docId)
            os.unlink(temp_path) # clean up tmp

            documentsStore[docId] = {
                "filename": file.filename,
                "path": storage_path,
                "storage": "supabase",
                "stats": result
            }

        else:
            # Development logic with local db
            UPLOAD_DIR = Path("./uploads")
            UPLOAD_DIR.mkdir(exist_ok=True)
            filePath = UPLOAD_DIR / file.filename
            
            with open(filePath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            result = ragPipeline.processDocument(str(filePath), docId)
            
            documentsStore[docId] = {
                "filename": file.filename,
                "path": str(filePath),
                "storage": "local",
                "stats": result
            }

        return UploadResponse(
            message="File uploaded and processed successfully",
            documentId=docId,
            filename=file.filename,
            stats=result
        )
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code = 500, detail = f"Processing failed: {str(e)}")

# Chat with a document with a streaming response
@app.post("/chat/stream")
async def chatStream(request: ChatRequest):
    if request.documentId not in documentsStore:
        raise HTTPException(
            status_code = 404,
            detail = f"Document {request.documentId} not found" 
        )
    
    try:
        # Convert chat history to RAG pipeline format
        chatHistory = [
            {"role": msg.role, "content": msg.content}
            for msg in request.history
        ]

        async def generate():
            async for chunk in ragPipeline.answerStream(
                question = request.message,
                documentId = request.documentId,
                chatHistory = chatHistory
            ):
                yield chunk

        return StreamingResponse(
            generate(), media_type = "text/event-stream"
        )
    
    except Exception as e:
        print(f"❌ Error in streaming chat: {str(e)}")
        raise HTTPException(
            status_code = 500,
            detail = f"Failed to generate answer: {str(e)}"
        )

# Chat with a document using RAG. Retrieves relevant chunks and generates answer with citations. (Without streaming)
@app.post("/chat", response_model = ChatResponse)
async def chat(request: ChatRequest):
    if request.documentId not in documentsStore:
        raise HTTPException(
            status_code = 404,
            detail = f"Document {request.documentId} not found"
        )
    
    try:
        chatHistory = [
            {"role": msg.role, "content": msg.content}
            for msg in request.history
        ]

        result = ragPipeline.answer(
            question = request.message,
            documentId = request.documentId,
            chatHistory = chatHistory
        )

        print(f"Answer generated with {len(result['sources'])} sources")

        return ChatResponse(
            answer = result["answer"],
            sources = result["sources"]
        )

    except Exception as e:
        print(f"❌ Error answering question: {str(e)}")
        raise HTTPException(
            status_code = 500,
            detail = f"Failed to generate answer: {str(e)}"
        )
    
# Delete a document from the vector store and system
@app.delete("/document/{documentId}")
async def deleteDoc(documentId: str):
    if documentId not in documentsStore:
        raise HTTPException(
            status_code = 404,
            detail = "Document not found"
        )
    
    try:
        ragPipeline.deleteDocument(documentId)

        docInfo = documentsStore[documentId]
        filePath = Path(docInfo["path"])
        if filePath.exists():
            filePath.unlink()

        del documentsStore[documentId]
        return {"message": f"Document {documentId} deleted successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"Deletion failed: {str(e)}"
        )
    
# Clear the vector database and clear all docs
@app.delete("/reset")
async def reset():
    try:
        vectorStore.clear()

        if not USE_SUPABASE_STORAGE:
            UPLOAD_DIR = Path("./uploads")
            if UPLOAD_DIR.exists():
                shutil.rmtree(UPLOAD_DIR)
                UPLOAD_DIR.mkdir(exist_ok = True)
        
        documentsStore.clear()
        return {"message": "Database reset"}
    
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"Reset failed: {str(e)}"
        )
    
# List all documents
@app.get("/documents")
async def listDocs():
    return {
        "documents": [
            {
                "id": docId,
                "filename": info["filename"],
                "stats": info["stats"]
            }
            for docId, info in documentsStore.items()
        ],
        "total": len(documentsStore)
    }

# Get system stats
@app.get("/stats")
async def getStats():
    return {
        "documentsCount": len(documentsStore),
        "vectorStoreStats": ragPipeline.getStats()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MyDocWhisper API with RAG enabled...")
    print(f"📊 Vector store: {vectorStore.store_type}")
    print("✨ Features: Streaming, Chat History, Enhanced Citations")
    uvicorn.run(app, host="0.0.0.0", port=8000)
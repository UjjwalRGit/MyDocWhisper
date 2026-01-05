from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path
import shutil
from dotenv import load_dotenv
from vector_store import VectorStoreManager
from rag_pipeline import RAGPipeline

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not loaded")

app = FastAPI(title = "MyDocWhisper API", version = "1.0")

#CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# Storage
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok= True)

# Initialize RAG pipline
vectorStore = VectorStoreManager(store_type = "chroma", persist_directory= "./chroma_db")
ragPipeline = RAGPipeline(vector_store = vectorStore)
documentsStore = {}

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
        "message": "MyDocWhisper API is running",
        "version": "1.0",
        "ragEnabled": True,
        "stats": stats
    }

# Upload and process a PDF Document
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
    
    filePath = UPLOAD_DIR / file.filename

    try:
        with open(filePath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        docId = file.filename.replace('.pdf', '').replace(' ', '_')

        # Process the document through the RAG pipeline
        print(f"Processing document: {file.filename}")
        result = ragPipeline.processDocument(str(filePath), docId)

        # Store document info
        documentsStore[docId] = {
            "filename": file.filename,
            "path": str(filePath),
            "stats": result
        }

        print(f"✅ Document processed: {result['totalChunks']} chunks created)")

        return UploadResponse(
            message = "File uploaded and processed successfully",
            documentId = docId,
            filename = file.filename,
            stats = result
        )
    
    except Exception as e:
        if filePath.exists():
            filePath.unlink()

        print(f"❌ Error processing document: {str(e)}")
        raise HTTPException(
            status_code = 500,
            detail = f"Document processing failed: {str(e)}"
        )

# Chat with a document using RAG. Retrieves relevant chunks and generates answer with citations. 
@app.post("/chat", response_model = ChatResponse)
async def chat(request: ChatRequest):
    if request.documentId not in documentsStore:
        raise HTTPException(
            status_code = 404,
            detail = f"Document {request.documentId} not found"
        )
    
    try:
        result = ragPipeline.answer(
            question = request.message,
            documentId = request.documentId,
            chatHistory = None # TODO
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
# RAG Pipeline handles PDF extraction, chunking, embeddings and retrieval
# This processes documents and answers questions

from typing import List, Dict, Tuple, Optional
from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from vector_store import VectorStoreManager

class RAGPipeline:
    # The complete RAG pipeline for the app, handles taking ing documents
    # chunking, and question answering
    def __init__(self, vector_store: VectorStoreManager):
        # Initialize the RAG pipeline
            # vector_store: A VectorStoreManager instance
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            model = "gpt-4o-mini",
            temperature = 0
        )

        # Splitter to split text for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200,
            length_function = len,
            separators = ["\n\n", "\n", " ", ""]
        )

    # Extract text from PDF with page metadata.
        # Args:
            # pdfPath: Path to the PDF file
        # Returns:
            # Tuple of (texts, metadatas) where each text has corresponding metadata
        
    def extractText(self, pdfPath: str) -> Tuple[List[str], List[Dict]]:
        reader = PdfReader(pdfPath)
        texts = []
        metadatas = []
        filename = Path(pdfPath).name

        for pageNum, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip(): # only add pages that aren't empty
                texts.append(text)
                metadatas.append({
                    "page": pageNum,
                    "filename": filename,
                    "source": f"{filename} - Page {pageNum}"
                })

        return texts, metadatas

    # Split texts into chunks while preserving metadata
        # Args:
            # texts: List of text strings (one per page)
            # metadatas: List of metadata dicts (one per page)
        # Returns:
            # Tuple of (chunked_texts, chunked_metadatas)
    def chunkDocuments(self, texts: List[str], 
        metadatas: List[Dict]) -> Tuple[List[str], List[Dict]]:
        allChunks = []
        allMetadata = []
        for text, metadata in zip(texts, metadatas):
            chunks = self.text_splitter.split_text(text)
            for chunk in chunks:
                allChunks.append(chunk)
                allMetadata.append(metadata.copy())
        
        return allChunks, allMetadata
    
    # Complete document processing pipeline
        # Args:
            # pdfPath: Path to the PDF file
            # documentId: Unique identifier for this document
        # Returns:
            # Dict with processing statistics
    def processDocument(self, pdfPath: str, documentId: str) -> Dict:
        # 1. Extract Text
        texts, metadatas = self.extractText(pdfPath)
        # 2. Chunk
        chunks, chunkMetadatas = self.chunkDocuments(texts, metadatas)
        # 3. Embed and Store
        # Done through vector store
        ids = self.vector_store.addDocuments(chunks, chunkMetadatas, documentId)

        return {
            "documentId": documentId,
            "filename": Path(pdfPath).name,
            "totalPages": len(texts),
            "totalChunks": len(chunks),
            "status": "success"
        }

    # Answer a question about a document using RAG.
        # Args:
            # question: The user's question
            # documentId: Which document to query
            # chatHistory: Previous conversation (for context)
        # Returns:
            # Dict with answer and source information
    def answer(self, question: str, documentId: str, 
                chatHistory: Optional[List[Tuple[str, str]]] 
                = None) -> Dict:
        # Retrieve relevant chunks
        relevantDocs = self.vector_store.similaritySearch(
            query = question,
            k = 5,
            documentId = documentId
        )

        if not relevantDocs:
            return {
                "answer": "I couldn't find any relevant information to your question in this document",
                "sources": []
            }
        
        # Build context from the retrieved chunks
        context = "\n\n".join([
            f"[Page {doc.metadata['page']}]: {doc.page_content}"
            for doc in relevantDocs
        ])

        # Build the prompt
        prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided context from a document.
        CONTEXT:
        {context}

        INSTRUCTIONS:
        - Answer the question using ONLY the information in the context above
        - If the answer is not in the context, say "I don't know based on the provided document"
        - Be concise but complete
        - When you reference information, mention which page it came from
        - Do not make up or infer information not explicitly stated

        QUESTION:
        {question}

        ANSWER:"""

        # Get answer from LLM
        response = self.llm.invoke(prompt)
        answer = response.content

        # Extract sources of pages (unique)
        sources = []
        seenPages = set()

        for doc in relevantDocs:
            page = doc.metadata['page']
            if page not in seenPages:
                sources.append({
                    "page": page,
                    "text": doc.page_content[:200] + "...",  # Preview
                    "filename": doc.metadata['filename']
                })
                seenPages.add(page)

        return {
            "answer": answer,
            "sources": sources
        }
    
    # Delete a document from the vector store
    def deleteDocument(self, documentId: str) -> bool:
        return self.vector_store.deleteDocument(documentId)
    
    # Get statistices about the vector store
    def getStats(self) -> Dict:
        return {
            "totalChunks": self.vector_store.getDocumentCount(),
            "store_type": self.vector_store.store_type
        }




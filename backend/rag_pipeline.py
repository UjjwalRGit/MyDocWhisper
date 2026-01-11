# RAG Pipeline handles PDF extraction, chunking, embeddings and retrieval
# This processes documents and answers questions
    # Phase 2 adds streaming responses and coversation context

from typing import List, Dict, Tuple, Optional, AsyncGenerator
from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from vector_store import VectorStoreManager
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import json

class RAGPipeline:
    # The complete RAG pipeline for the app, handles taking ing documents
    # chunking, and question answering
    def __init__(self, vector_store: VectorStoreManager):
        # Initialize the RAG pipeline
            # vector_store: A VectorStoreManager instance
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            model = "gpt-4o-mini",
            temperature = 0,
            streaming = True
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
    
    # Build the prompt with context and optional chat history.
        # Args:
            # question: The user's question
            # context: Retrieved context from vector database
            # chatHistory: Previous conversation messages
            
        # Returns:
            # Formatted prompt string
    def buildPrompt(self, question: str, context: str,
                    chatHistory: Optional[List[Dict[str, str]]] = None) -> str:
        historyStr = ""
        if chatHistory and len(chatHistory) > 0:
            historyStr = "PREVIOUS CONVERSATION:\n"
            for msg in chatHistory[-3:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                historyStr += f"{role}: {msg['content']}\n"
            historyStr += "\n"
        
        prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided context from a document.
        
        {historyStr}CONTEXT:
        {context}

        INSTRUCTIONS:
        - Answer the question using ONLY the information in the context above
        - If the answer is not in the context, say "I don't know based on the provided document"
        - Be concise but complete
        - When you reference information, mention which page it came from
        - Do not make up or infer information not explicitly stated
        - If there is previous conversation context, use it to understand follow-up questions

        QUESTION:
        {question}
        
        ANSWER:"""

        return prompt
    
    # Answer a question with streaming response
        # Args:
            # question: The user's question
            # documentId: Which document to query
            # chatHistory: Previous conversation for context
            
        # Yields:
            # Chunks of the answer as they're generated
    async def answerStream(self, question: str, documentId: str,
                           chatHistory: Optional[List[Dict[str, str]]] = None) -> AsyncGenerator[str, None]:
        relevantDocs = self.vector_store.similaritySearch(
            query = question, k = 5, documentId = documentId)
        
        if not relevantDocs:
            yield json.dumps({
                "type": "answer",
                "content": "I couldn't find any relevant information to your question in this document"
            }) + "\n"
            yield json.dumps({
                "type": "sources",
                "sources": []
            }) + "\n"
            return
        
        # Build context
        context = "\n\n".join([
            f"[Page {doc.metadata['page']}]: {doc.page_content}"
            for doc in relevantDocs
        ])

        # Build prompt
        prompt = self.buildPrompt(question, context, chatHistory)

        # Stream the answer token by token
        async for chunk in self.llm.astream(prompt):
            if chunk.content:
                yield json.dumps({
                    "type": "answer",
                    "content": chunk.content
                }) + "\n"

        # Send sources
        sources = []
        seenPages = set()
        for doc in relevantDocs:
            page = doc.metadata['page']
            if page not in seenPages:
                sources.append({
                    "page": page,
                    "text": doc.page_content[:200] + "...",
                    "filename": doc.metadata['filename']
                })
                seenPages.add(page)

        yield json.dumps({
            "type": "sources",
            "sources": sources
        }) + "\n"
        

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
        prompt = self.buildPrompt(question, context, chatHistory)

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
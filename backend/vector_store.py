# Vector Store Manager - Abstraction layer for vector database
    # Allows easy switching between current local DB (ChromaDB)
    # and to the deployment database (Supabase)

import os
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


class VectorStoreManager:
    # Manages vector store operations independently of the underlying
    # database. Currently supports ChromaDB, but will be changed to support
    # Supabase in production.
    def __init__(self, store_type: str = "chroma", persist_directory: str = "./chroma_db"):
        # Initialize the vector store manager.
            # store_type: Type of vector store (currently "chroma")
            # persist_directory: where to store database
        self.store_type = store_type
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # Initialize the appropriate vector store
        if store_type == "chroma":
            self.vectorstore = self._init_chroma()
        elif store_type == "supabase":
            self.vectorstore = self._init_supabase()
        else:
            raise ValueError(f"Unsupported store type: {store_type}")
        
    def _init_chroma(self) -> Chroma:
        # Initialize ChromaDB (loacl vector db)
        return Chroma(
            persist_directory = self.persist_directory,
            embedding_function = self.embeddings,
            collection_name = "mydocwhisper"
        )
    
    def _init_supabase(self):
        # Intialize Supabase (TODO)
        raise NotImplementedError("Supabase to be implemented")
    
    # add documents that user uploads to db
        # Args:
            # texts: List of text chunks
            # metadatas: List of metadata dicts (page, filename, etc.)
            # documentId: Unique identifier for this document
        # Returns:
            # List of IDs for the added chunks
    def addDocuments(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        documentId: str
    ) -> List[str]:
        # Add documentId to all metadata
        for metadata in metadatas:
            metadata["documentId"] = documentId

        # Create Document objects
        documents = [
            Document(page_content=str(text), metadata=metadata)
            for text, metadata in zip(texts, metadatas)
        ]

        # Add to vector store
        print(f"Adding {len(documents)} documents to vector store")
        ids = self.vectorstore.add_documents(documents)
        print(f"Received ids: {type(ids)}, value: {ids}")
    
        # Handle different return types
        if ids is None:
            return []
        elif isinstance(ids, int):
            # If it returns count instead of list of IDs
            return [str(i) for i in range(ids)]
        else:
            return ids if ids else []
    
    # Search for similar documents
        # Args:
            # query: The search query
            # k: Number of results to return
            # documentId: Optional filter by document ID
        # Returns:
            # List of Document objects with content and metadata
    def similaritySearch(
        self,
        query: str,
        k: int = 5,
        documentId: Optional[str] = None
    ) -> List[Document]:
        # Filter by specific document
        if documentId:
            filter_dict = {"documentId": documentId}
            results = self.vectorstore.similarity_search(
                query, k = k, filter = filter_dict)
        else:
            # Search through all documents
            results = self.vectorstore.similarity_search(query, k = k)

        return results
    
    # Deletes all associated chucks of a document
        # Args:
            # documentId: The document ID to delete
        # Returns:
            # True if successful
            #  False if not
    def deleteDocument(self, documentId: str) -> bool:
        try:
            # Get all IDs for this document
            collection = self.vectorstore._collection
            results = collection.get(where = {"documentId": documentId})

            if results and results['ids']:
                collection.delete(ids = results['ids'])
                return True
            return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    # Get the total number of document chunks in store
    def getDocumentCount(self) -> int:
        try:
            collection = self.vectorstore._collection
            return collection.count()
        except Exception as e:
            print(f"Error getting count: {e}")
            return 0
        
    # Clear all documents from the store
    def clear(self) -> bool:
        try:
            collection = self.vectorstore._collection
            collection.delete(where = {})
            return True
        except Exception as e:
            print(f"Error clearing store: {e}")
            return False
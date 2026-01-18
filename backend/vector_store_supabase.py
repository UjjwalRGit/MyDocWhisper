# Supabase vector store for deployment
import os
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client, Client
from langchain_core.documents import Document

class VectorStoreManager:
    # Initialize the vector store manager.
        # store_type: Type of vector store (supabase)
    def __init__(self, store_type: str = "supabase", persist_directory: str = None):
        self.store_type = "supabase"
        self.embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")
        
        # Supabase setup - with debug logging
        print("=" * 50)
        print("DEBUG: Checking environment variables...")
        print(f"All env vars: {list(os.environ.keys())[:10]}")  # First 10 keys
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        print(f"SUPABASE_URL found: {bool(supabase_url)}")
        print(f"SUPABASE_SERVICE_KEY found: {bool(supabase_key)}")
        
        if supabase_url:
            print(f"SUPABASE_URL value: {supabase_url[:30]}...")
        if supabase_key:
            print(f"SUPABASE_SERVICE_KEY value: {supabase_key[:30]}...")
        print("=" * 50)
        
        if not supabase_url or not supabase_key:
            print("❌ ERROR: Environment variables not found!")
            print("Available environment variables:")
            for key in os.environ.keys():
                if 'SUPABASE' in key or 'OPENAI' in key:
                    print(f"  - {key}")
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        
        self.supabase_client: Client = create_client(supabase_url, supabase_key)
        
        self.vectorstore = SupabaseVectorStore(
            client = self.supabase_client,
            embedding = self.embeddings,
            table_name = "documents",
            query_name = "match_documents"
        )

    
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
        for metadata in metadatas:
            metadata["documentId"] = documentId
        
        documents = [
            Document(page_content = text, metadata=metadata)
            for text, metadata in zip(texts, metadatas)
        ]
        
        ids = self.vectorstore.add_documents(documents)
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
        if documentId:
            # Supabase filtering
            results = self.vectorstore.similarity_search(
                query,
                k = k,
                filter = {"documentId": documentId}
            )
        else:
            results = self.vectorstore.similarity_search(query, k=k)
        
        return results
    

    # Deletes all associated chucks of a document
        # Args:
            # documentId: The document ID to delete
        # Returns:
            # True if successful
            #  False if not
    def deleteDocument(self, documentId: str) -> bool:
        try:
            # Delete from Supabase
            response = self.supabase_client.table("documents").delete().eq(
                "metadata->>documentId", documentId
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
        
    
    # Get the total number of document chunks in store
    def getDocumentCount(self) -> int:
        try:
            response = self.supabase_client.table("documents").select("id", count="exact").execute()
            return response.count if response.count else 0
        except Exception as e:
            print(f"Error getting count: {e}")
            return 0
        

    # Clear all documents from the store
    def clear(self) -> bool:
        try:
            self.supabase_client.table("documents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            return True
        except Exception as e:
            print(f"Error clearing store: {e}")
            return False
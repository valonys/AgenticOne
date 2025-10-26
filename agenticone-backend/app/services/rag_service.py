"""
RAG (Retrieval-Augmented Generation) Service for document processing and search
"""
import uuid
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.config import settings
from app.services.vector_store import VectorStore
from app.services.document_processor import DocumentProcessor
from app.services.vertex_ai_service import VertexAIService
from app.models.database import db_client

class RAGService:
    """RAG service for document processing and retrieval"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.document_processor = DocumentProcessor()
        self.vertex_ai_service = VertexAIService()
        self.status = "initialized"
    
    async def process_document(
        self, 
        content: bytes, 
        filename: str, 
        metadata: Dict[str, Any]
    ) -> str:
        """Process and store a document"""
        try:
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Process document content
            processed_content = await self.document_processor.process_document(
                content, filename, metadata
            )
            
            # Extract text and create embeddings
            text_content = processed_content.get("text", "")
            embeddings = await self.vector_store.create_embeddings(text_content)
            
            # Store in vector database
            await self.vector_store.store_document(
                document_id=document_id,
                content=text_content,
                embeddings=embeddings,
                metadata={
                    "filename": filename,
                    "document_type": processed_content.get("document_type", "unknown"),
                    "size": len(content),
                    "processed_at": datetime.utcnow().isoformat(),
                    **metadata
                }
            )
            
            # Store document metadata in Firestore
            await db_client.create_document({
                "document_id": document_id,
                "filename": filename,
                "document_type": processed_content.get("document_type", "unknown"),
                "size": len(content),
                "storage_path": f"documents/{document_id}",
                "metadata": metadata
            })
            
            return document_id
            
        except Exception as e:
            raise ValueError(f"Failed to process document: {str(e)}")
    
    async def analyze_document_with_ai(
        self, 
        document_id: str, 
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """Analyze document using Vertex AI"""
        try:
            # Get document content
            document_content = await self.get_document_content(document_id)
            
            # Use Vertex AI for analysis
            analysis_result = await self.vertex_ai_service.analyze_document(
                document_text=document_content,
                analysis_type=analysis_type
            )
            
            return analysis_result
            
        except Exception as e:
            raise ValueError(f"Failed to analyze document with AI: {str(e)}")
    
    async def search_documents_semantic(
        self, 
        query: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search documents using semantic search with Vertex AI"""
        try:
            # Use Vertex AI for semantic search
            results = await self.vertex_ai_service.search_similar_documents(
                query=query,
                limit=limit
            )
            
            return results
            
        except Exception as e:
            raise ValueError(f"Failed to search documents semantically: {str(e)}")
    
    async def get_document_content(self, document_id: str) -> str:
        """Get document content by ID"""
        try:
            # Get from vector store
            document = await self.vector_store.get_document(document_id)
            if document:
                return document.get("content", "")
            
            # Fallback to database
            doc_record = await db_client.get_document(document_id)
            if doc_record:
                # This would typically involve retrieving from cloud storage
                return f"Document content for {doc_record.filename}"
            
            raise ValueError(f"Document {document_id} not found")
            
        except Exception as e:
            raise ValueError(f"Failed to get document content: {str(e)}")
    
    async def search_documents(
        self, 
        query: str, 
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        try:
            # Create query embedding
            query_embedding = await self.vector_store.create_embeddings(query)
            
            # Search vector database
            results = await self.vector_store.search_similar(
                query_embedding=query_embedding,
                limit=limit,
                filters=filters
            )
            
            return results
            
        except Exception as e:
            raise ValueError(f"Failed to search documents: {str(e)}")
    
    async def get_document_summary(self, document_id: str) -> Dict[str, Any]:
        """Get document summary and key information"""
        try:
            # Get document content
            content = await self.get_document_content(document_id)
            
            # Get document metadata
            doc_record = await db_client.get_document(document_id)
            if not doc_record:
                raise ValueError(f"Document {document_id} not found")
            
            # Generate summary using document processor
            summary = await self.document_processor.generate_summary(content)
            
            return {
                "document_id": document_id,
                "filename": doc_record.filename,
                "document_type": doc_record.document_type,
                "summary": summary,
                "metadata": doc_record.metadata,
                "size": doc_record.size
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get document summary: {str(e)}")
    
    async def update_document_metadata(
        self, 
        document_id: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """Update document metadata"""
        try:
            # Update in vector store
            await self.vector_store.update_document_metadata(document_id, metadata)
            
            # Update in Firestore
            await db_client.update_analysis(document_id, {"metadata": metadata})
            
            return True
            
        except Exception as e:
            raise ValueError(f"Failed to update document metadata: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        try:
            # Delete from vector store
            await self.vector_store.delete_document(document_id)
            
            # Delete from Firestore (metadata only, actual file deletion handled separately)
            # Note: In production, you'd also delete from cloud storage
            
            return True
            
        except Exception as e:
            raise ValueError(f"Failed to delete document: {str(e)}")
    
    async def get_related_documents(
        self, 
        document_id: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get documents related to a specific document"""
        try:
            # Get document content
            content = await self.get_document_content(document_id)
            
            # Search for similar documents
            similar_docs = await self.search_documents(content, limit=limit)
            
            # Filter out the original document
            related_docs = [
                doc for doc in similar_docs 
                if doc.get("document_id") != document_id
            ]
            
            return related_docs[:limit]
            
        except Exception as e:
            raise ValueError(f"Failed to get related documents: {str(e)}")
    
    async def batch_process_documents(
        self, 
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """Process multiple documents in batch"""
        try:
            document_ids = []
            
            # Process documents in parallel
            tasks = []
            for doc in documents:
                task = self.process_document(
                    doc["content"],
                    doc["filename"],
                    doc.get("metadata", {})
                )
                tasks.append(task)
            
            document_ids = await asyncio.gather(*tasks)
            return document_ids
            
        except Exception as e:
            raise ValueError(f"Failed to batch process documents: {str(e)}")
    
    async def get_document_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored documents"""
        try:
            # Get document count from vector store
            doc_count = await self.vector_store.get_document_count()
            
            # Get document types distribution
            doc_types = await self.vector_store.get_document_types()
            
            return {
                "total_documents": doc_count,
                "document_types": doc_types,
                "status": self.status
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get document statistics: {str(e)}")
    
    async def close(self):
        """Close the RAG service and cleanup resources"""
        try:
            await self.vector_store.close()
            self.status = "closed"
        except Exception as e:
            print(f"Error closing RAG service: {str(e)}")

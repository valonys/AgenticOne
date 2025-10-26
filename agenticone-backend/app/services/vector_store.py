"""
Vector Store Service for document embeddings and similarity search using Vertex AI
"""
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.config import settings
from app.services.vertex_ai_service import VertexAIService

class VectorStore:
    """Vector store for document embeddings and similarity search using Vertex AI"""
    
    def __init__(self):
        self.vertex_ai_service = VertexAIService()
        self.documents = {}  # In production, this would be a proper vector database
        self.status = "initialized"
    
    async def create_embeddings(self, text: str) -> List[float]:
        """Create embeddings for text content using Vertex AI"""
        try:
            # Use Vertex AI for real embeddings
            embedding = await self.vertex_ai_service.create_embeddings(text)
            
            # Ensure correct dimensions
            target_dim = settings.VECTOR_SEARCH_DIMENSIONS
            if len(embedding) < target_dim:
                embedding.extend([0.0] * (target_dim - len(embedding)))
            else:
                embedding = embedding[:target_dim]
            
            return embedding
            
        except Exception as e:
            raise ValueError(f"Failed to create embeddings: {str(e)}")
    
    async def store_document(
        self, 
        document_id: str, 
        content: str, 
        embeddings: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """Store document with embeddings"""
        try:
            self.documents[document_id] = {
                "document_id": document_id,
                "content": content,
                "embeddings": embeddings,
                "metadata": metadata,
                "created_at": datetime.utcnow().isoformat()
            }
            
            return True
            
        except Exception as e:
            raise ValueError(f"Failed to store document: {str(e)}")
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        return self.documents.get(document_id)
    
    async def search_similar(
        self, 
        query_embedding: List[float], 
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            results = []
            
            for doc_id, doc_data in self.documents.items():
                # Apply filters if provided
                if filters:
                    metadata = doc_data.get("metadata", {})
                    if not self._matches_filters(metadata, filters):
                        continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(
                    query_embedding, 
                    doc_data["embeddings"]
                )
                
                results.append({
                    "document_id": doc_id,
                    "content": doc_data["content"][:500] + "..." if len(doc_data["content"]) > 500 else doc_data["content"],
                    "metadata": doc_data["metadata"],
                    "similarity": similarity
                })
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            raise ValueError(f"Failed to search similar documents: {str(e)}")
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            return 0.0
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if document metadata matches filters"""
        try:
            for key, value in filters.items():
                if key not in metadata:
                    return False
                if metadata[key] != value:
                    return False
            return True
        except Exception:
            return False
    
    async def update_document_metadata(
        self, 
        document_id: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """Update document metadata"""
        try:
            if document_id in self.documents:
                self.documents[document_id]["metadata"].update(metadata)
                return True
            return False
            
        except Exception as e:
            raise ValueError(f"Failed to update document metadata: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document from vector store"""
        try:
            if document_id in self.documents:
                del self.documents[document_id]
                return True
            return False
            
        except Exception as e:
            raise ValueError(f"Failed to delete document: {str(e)}")
    
    async def get_document_count(self) -> int:
        """Get total number of documents"""
        return len(self.documents)
    
    async def get_document_types(self) -> Dict[str, int]:
        """Get distribution of document types"""
        try:
            doc_types = {}
            for doc_data in self.documents.values():
                doc_type = doc_data.get("metadata", {}).get("document_type", "unknown")
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            return doc_types
        except Exception:
            return {}
    
    async def get_documents_by_type(self, document_type: str) -> List[Dict[str, Any]]:
        """Get all documents of a specific type"""
        try:
            results = []
            for doc_data in self.documents.values():
                if doc_data.get("metadata", {}).get("document_type") == document_type:
                    results.append(doc_data)
            return results
        except Exception:
            return []
    
    async def batch_store_documents(
        self, 
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """Store multiple documents in batch"""
        try:
            document_ids = []
            for doc in documents:
                await self.store_document(
                    doc["document_id"],
                    doc["content"],
                    doc["embeddings"],
                    doc["metadata"]
                )
                document_ids.append(doc["document_id"])
            return document_ids
        except Exception as e:
            raise ValueError(f"Failed to batch store documents: {str(e)}")
    
    async def search_by_metadata(
        self, 
        metadata_filters: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search documents by metadata filters"""
        try:
            results = []
            for doc_data in self.documents.values():
                if self._matches_filters(doc_data.get("metadata", {}), metadata_filters):
                    results.append(doc_data)
            
            return results[:limit]
        except Exception as e:
            raise ValueError(f"Failed to search by metadata: {str(e)}")
    
    async def get_document_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored documents"""
        try:
            total_docs = len(self.documents)
            doc_types = await self.get_document_types()
            
            return {
                "total_documents": total_docs,
                "document_types": doc_types,
                "status": self.status
            }
        except Exception as e:
            raise ValueError(f"Failed to get document statistics: {str(e)}")
    
    async def close(self):
        """Close the vector store and cleanup resources"""
        try:
            self.documents.clear()
            self.status = "closed"
        except Exception as e:
            print(f"Error closing vector store: {str(e)}")

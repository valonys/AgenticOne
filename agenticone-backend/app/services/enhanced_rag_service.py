"""
Enhanced RAG Service with advanced knowledge ingestion capabilities
"""
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
import json

from app.config import settings
from app.services.vector_store import VectorStore
from app.services.document_processor import DocumentProcessor
from app.models.database import db_client

class EnhancedRAGService:
    """Enhanced RAG service with advanced knowledge management"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.document_processor = DocumentProcessor()
        self.status = "initialized"
        self.knowledge_stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "last_updated": None
        }
    
    async def batch_ingest_documents(
        self, 
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Batch ingest multiple documents for knowledge base"""
        try:
            results = {
                "successful": [],
                "failed": [],
                "total_processed": 0,
                "total_chunks": 0
            }
            
            for doc_data in documents:
                try:
                    # Process individual document
                    doc_result = await self.process_document_enhanced(
                        content=doc_data["content"],
                        filename=doc_data["filename"],
                        metadata=doc_data.get("metadata", {}),
                        chunk_size=doc_data.get("chunk_size", 1000),
                        overlap=doc_data.get("overlap", 200)
                    )
                    
                    results["successful"].append({
                        "document_id": doc_result["document_id"],
                        "filename": doc_data["filename"],
                        "chunks_created": doc_result["chunks_created"]
                    })
                    results["total_chunks"] += doc_result["chunks_created"]
                    
                except Exception as e:
                    results["failed"].append({
                        "filename": doc_data["filename"],
                        "error": str(e)
                    })
                
                results["total_processed"] += 1
            
            # Update knowledge stats
            self.knowledge_stats["total_documents"] += len(results["successful"])
            self.knowledge_stats["total_chunks"] += results["total_chunks"]
            self.knowledge_stats["last_updated"] = datetime.utcnow().isoformat()
            
            return results
            
        except Exception as e:
            raise ValueError(f"Failed to batch ingest documents: {str(e)}")
    
    async def process_document_enhanced(
        self, 
        content: bytes, 
        filename: str, 
        metadata: Dict[str, Any],
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> Dict[str, Any]:
        """Enhanced document processing with semantic chunking"""
        try:
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Process document content
            processed_content = await self.document_processor.process_document(
                content, filename, metadata
            )
            
            # Extract text and create semantic chunks
            text_content = processed_content.get("text", "")
            chunks = await self._create_semantic_chunks(
                text_content, chunk_size, overlap
            )
            
            # Process each chunk
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                # Create embeddings for chunk
                embeddings = await self.vector_store.create_embeddings(chunk["text"])
                
                # Store chunk in vector database
                chunk_id = f"{document_id}_chunk_{i}"
                await self.vector_store.store_document(
                    document_id=chunk_id,
                    content=chunk["text"],
                    embeddings=embeddings,
                    metadata={
                        "parent_document_id": document_id,
                        "chunk_index": i,
                        "chunk_size": len(chunk["text"]),
                        "filename": filename,
                        "document_type": processed_content.get("document_type", "unknown"),
                        "processed_at": datetime.utcnow().isoformat(),
                        **metadata
                    }
                )
                chunk_ids.append(chunk_id)
            
            # Store document metadata in Firestore
            await db_client.create_document({
                "document_id": document_id,
                "filename": filename,
                "document_type": processed_content.get("document_type", "unknown"),
                "size": len(content),
                "storage_path": f"documents/{document_id}",
                "chunks": chunk_ids,
                "chunk_count": len(chunks),
                "metadata": metadata
            })
            
            return {
                "document_id": document_id,
                "chunks_created": len(chunks),
                "chunk_ids": chunk_ids
            }
            
        except Exception as e:
            raise ValueError(f"Failed to process document: {str(e)}")
    
    async def _create_semantic_chunks(
        self, 
        text: str, 
        chunk_size: int, 
        overlap: int
    ) -> List[Dict[str, Any]]:
        """Create semantic chunks with overlap for better context"""
        chunks = []
        words = text.split()
        
        start = 0
        while start < len(words):
            # Get chunk of words
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            # Add metadata
            chunk_metadata = {
                "start_word": start,
                "end_word": end,
                "word_count": len(chunk_words),
                "char_count": len(chunk_text)
            }
            
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
            
            # Move start position with overlap
            start = max(start + chunk_size - overlap, start + 1)
            if start >= len(words):
                break
        
        return chunks
    
    async def search_knowledge_base(
        self, 
        query: str, 
        agent_type: str = "general",
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Enhanced knowledge base search with agent specialization"""
        try:
            # Create query embedding
            query_embedding = await self.vector_store.create_embeddings(query)
            
            # Search vector database
            results = await self.vector_store.search_similar(
                query_embedding=query_embedding,
                limit=limit * 2,  # Get more results for filtering
                threshold=similarity_threshold
            )
            
            # Filter and rank by agent relevance
            agent_filtered_results = await self._filter_by_agent_relevance(
                results, agent_type, limit
            )
            
            return agent_filtered_results
            
        except Exception as e:
            raise ValueError(f"Failed to search knowledge base: {str(e)}")
    
    async def _filter_by_agent_relevance(
        self, 
        results: List[Dict[str, Any]], 
        agent_type: str, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Filter results by agent type relevance"""
        # Agent-specific keywords and relevance scoring
        agent_keywords = {
            "methods_specialist": [
                "procedure", "method", "process", "operation", "protocol",
                "safety", "maintenance", "inspection", "quality", "standard"
            ],
            "corrosion_engineer": [
                "corrosion", "material", "coating", "inspection", "degradation",
                "prevention", "cathodic", "anodic", "galvanic", "rust"
            ],
            "subsea_engineer": [
                "subsea", "underwater", "marine", "offshore", "pipeline",
                "riser", "umbilical", "ROV", "diving", "seabed"
            ],
            "discipline_head": [
                "project", "management", "coordination", "decision", "strategy",
                "planning", "oversight", "governance", "compliance", "risk"
            ]
        }
        
        keywords = agent_keywords.get(agent_type, [])
        
        # Score results based on keyword relevance
        scored_results = []
        for result in results:
            score = 0
            content_lower = result.get("content", "").lower()
            metadata_lower = str(result.get("metadata", {})).lower()
            
            # Check for keyword matches
            for keyword in keywords:
                if keyword in content_lower or keyword in metadata_lower:
                    score += 1
            
            # Add base similarity score
            score += result.get("similarity", 0) * 10
            
            scored_results.append({
                **result,
                "agent_relevance_score": score
            })
        
        # Sort by relevance and return top results
        scored_results.sort(key=lambda x: x["agent_relevance_score"], reverse=True)
        return scored_results[:limit]
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            # Get stats from vector store
            vector_stats = await self.vector_store.get_stats()
            
            # Get stats from database
            db_stats = await db_client.get_document_stats()
            
            return {
                "knowledge_base": {
                    "total_documents": db_stats.get("total_documents", 0),
                    "total_chunks": vector_stats.get("total_vectors", 0),
                    "last_updated": self.knowledge_stats["last_updated"],
                    "storage_size": db_stats.get("total_size", 0)
                },
                "vector_store": vector_stats,
                "database": db_stats
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get knowledge stats: {str(e)}",
                "knowledge_base": self.knowledge_stats
            }
    
    async def update_document(
        self, 
        document_id: str, 
        new_content: bytes,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing document in knowledge base"""
        try:
            # Get existing document
            existing_doc = await db_client.get_document(document_id)
            if not existing_doc:
                raise ValueError(f"Document {document_id} not found")
            
            # Process new content
            processed_content = await self.document_processor.process_document(
                new_content, existing_doc.filename, metadata
            )
            
            # Delete old chunks
            if hasattr(existing_doc, 'chunks'):
                for chunk_id in existing_doc.chunks:
                    await self.vector_store.delete_document(chunk_id)
            
            # Create new chunks
            text_content = processed_content.get("text", "")
            chunks = await self._create_semantic_chunks(text_content)
            
            # Store new chunks
            new_chunk_ids = []
            for i, chunk in enumerate(chunks):
                embeddings = await self.vector_store.create_embeddings(chunk["text"])
                chunk_id = f"{document_id}_chunk_{i}"
                
                await self.vector_store.store_document(
                    document_id=chunk_id,
                    content=chunk["text"],
                    embeddings=embeddings,
                    metadata={
                        "parent_document_id": document_id,
                        "chunk_index": i,
                        "updated_at": datetime.utcnow().isoformat(),
                        **metadata
                    }
                )
                new_chunk_ids.append(chunk_id)
            
            # Update document metadata
            await db_client.update_document(document_id, {
                "chunks": new_chunk_ids,
                "chunk_count": len(chunks),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": metadata
            })
            
            return {
                "document_id": document_id,
                "chunks_updated": len(chunks),
                "new_chunk_ids": new_chunk_ids
            }
            
        except Exception as e:
            raise ValueError(f"Failed to update document: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document and all its chunks from knowledge base"""
        try:
            # Get document metadata
            doc = await db_client.get_document(document_id)
            if not doc:
                return False
            
            # Delete all chunks
            if hasattr(doc, 'chunks'):
                for chunk_id in doc.chunks:
                    await self.vector_store.delete_document(chunk_id)
            
            # Delete document metadata
            await db_client.delete_document(document_id)
            
            return True
            
        except Exception as e:
            raise ValueError(f"Failed to delete document: {str(e)}")
    
    async def close(self):
        """Close the enhanced RAG service"""
        if hasattr(self.vector_store, 'close'):
            await self.vector_store.close()

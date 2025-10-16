"""
Enhanced API endpoints for knowledge management and RAG operations
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Dict, Any, Optional
import json

from app.services.enhanced_rag_service import EnhancedRAGService
from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.models.database import db_client

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# Initialize enhanced RAG service
enhanced_rag = EnhancedRAGService()

@router.post("/ingest/batch")
async def batch_ingest_documents(
    documents: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Batch ingest multiple documents into knowledge base"""
    try:
        result = await enhanced_rag.batch_ingest_documents(documents)
        return {
            "status": "success",
            "message": f"Processed {result['total_processed']} documents",
            "results": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest/single")
async def ingest_single_document(
    content: bytes = File(...),
    filename: str = Form(...),
    metadata: str = Form("{}"),
    chunk_size: int = Form(1000),
    overlap: int = Form(200)
) -> Dict[str, Any]:
    """Ingest a single document into knowledge base"""
    try:
        # Parse metadata
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            metadata_dict = {}
        
        result = await enhanced_rag.process_document_enhanced(
            content=content,
            filename=filename,
            metadata=metadata_dict,
            chunk_size=chunk_size,
            overlap=overlap
        )
        
        return {
            "status": "success",
            "message": f"Document '{filename}' ingested successfully",
            "document_id": result["document_id"],
            "chunks_created": result["chunks_created"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_knowledge_base(
    query: str,
    agent_type: str = "general",
    limit: int = 5,
    similarity_threshold: float = 0.7
) -> Dict[str, Any]:
    """Search knowledge base with agent-specific filtering"""
    try:
        results = await enhanced_rag.search_knowledge_base(
            query=query,
            agent_type=agent_type,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        return {
            "status": "success",
            "query": query,
            "agent_type": agent_type,
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_knowledge_stats() -> Dict[str, Any]:
    """Get knowledge base statistics"""
    try:
        stats = await enhanced_rag.get_knowledge_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/documents/{document_id}")
async def update_document(
    document_id: str,
    content: bytes = File(...),
    metadata: str = Form("{}")
) -> Dict[str, Any]:
    """Update existing document in knowledge base"""
    try:
        # Parse metadata
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            metadata_dict = {}
        
        result = await enhanced_rag.update_document(
            document_id=document_id,
            new_content=content,
            metadata=metadata_dict
        )
        
        return {
            "status": "success",
            "message": f"Document {document_id} updated successfully",
            "chunks_updated": result["chunks_updated"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str) -> Dict[str, Any]:
    """Delete document from knowledge base"""
    try:
        success = await enhanced_rag.delete_document(document_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Document {document_id} deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_type}/analyze")
async def agent_specific_analysis(
    agent_type: str,
    query: str,
    context_documents: Optional[List[str]] = None,
    analysis_depth: str = "standard"
) -> Dict[str, Any]:
    """Perform agent-specific analysis with knowledge base context"""
    try:
        # Search for relevant knowledge
        knowledge_results = await enhanced_rag.search_knowledge_base(
            query=query,
            agent_type=agent_type,
            limit=10,
            similarity_threshold=0.6
        )
        
        # Prepare context for agent
        context = {
            "query": query,
            "agent_type": agent_type,
            "relevant_documents": knowledge_results,
            "analysis_depth": analysis_depth,
            "context_documents": context_documents or []
        }
        
        # This would integrate with the actual agent analysis
        # For now, return the context that would be sent to the agent
        return {
            "status": "success",
            "agent_type": agent_type,
            "context": context,
            "knowledge_sources": len(knowledge_results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents(
    limit: int = 20,
    offset: int = 0,
    document_type: Optional[str] = None
) -> Dict[str, Any]:
    """List documents in knowledge base"""
    try:
        # This would query the database for documents
        # For now, return a mock response
        documents = await db_client.list_documents(
            limit=limit,
            offset=offset,
            document_type=document_type
        )
        
        return {
            "status": "success",
            "documents": documents,
            "total": len(documents),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document_details(document_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific document"""
    try:
        document = await db_client.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "status": "success",
            "document": document.dict() if hasattr(document, 'dict') else document
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_knowledge_base(
    format: str = "json",
    include_content: bool = False
) -> Dict[str, Any]:
    """Export knowledge base data"""
    try:
        # This would export the knowledge base
        # For now, return a mock response
        return {
            "status": "success",
            "message": f"Knowledge base exported in {format} format",
            "include_content": include_content,
            "export_url": f"/exports/knowledge_base_{format}.{format}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_knowledge_base(
    data: Dict[str, Any],
    overwrite: bool = False
) -> Dict[str, Any]:
    """Import knowledge base data"""
    try:
        # This would import knowledge base data
        # For now, return a mock response
        return {
            "status": "success",
            "message": "Knowledge base imported successfully",
            "overwrite": overwrite,
            "imported_documents": len(data.get("documents", []))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

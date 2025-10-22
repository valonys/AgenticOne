"""
Vertex AI API endpoints for real Google Cloud AI services
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, List, Any, Optional
import json

from app.services.vertex_ai_service import VertexAIService
from app.services.rag_service import RAGService
from app.services.vision_service import VisionService

router = APIRouter(prefix="/api/vertex-ai", tags=["Vertex AI"])

# Initialize services
vertex_ai_service = VertexAIService()
rag_service = RAGService()
vision_service = VisionService()

@router.post("/analyze-document")
async def analyze_document_with_vertex_ai(
    document_id: str = Form(...),
    analysis_type: str = Form("general"),
    context: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Analyze document using Vertex AI"""
    try:
        result = await rag_service.analyze_document_with_ai(
            document_id=document_id,
            analysis_type=analysis_type
        )
        return {
            "status": "success",
            "analysis": result,
            "document_id": document_id,
            "analysis_type": analysis_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-image")
async def analyze_image_with_vertex_ai(
    image: UploadFile = File(...),
    analysis_type: str = Form("general"),
    prompt: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Analyze image using Vertex AI Gemini Vision"""
    try:
        image_content = await image.read()
        
        result = await vision_service.analyze_image(
            image_content=image_content,
            analysis_type=analysis_type,
            prompt=prompt
        )
        
        return {
            "status": "success",
            "analysis": result,
            "filename": image.filename,
            "analysis_type": analysis_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-text")
async def generate_text_with_vertex_ai(
    prompt: str = Form(...),
    system_prompt: Optional[str] = Form(None),
    max_tokens: int = Form(1000),
    temperature: float = Form(0.7)
) -> Dict[str, Any]:
    """Generate text using Vertex AI Gemini"""
    try:
        result = await vertex_ai_service.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {
            "status": "success",
            "generated_text": result,
            "prompt": prompt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-documents")
async def search_documents_semantic(
    query: str = Form(...),
    limit: int = Form(5)
) -> Dict[str, Any]:
    """Search documents using semantic search"""
    try:
        results = await rag_service.search_documents_semantic(
            query=query,
            limit=limit
        )
        
        return {
            "status": "success",
            "results": results,
            "query": query,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-analyze")
async def batch_analyze_documents(
    documents: str = Form(...),  # JSON string of documents
    analysis_type: str = Form("general")
) -> Dict[str, Any]:
    """Batch analyze multiple documents using Vertex AI"""
    try:
        documents_list = json.loads(documents)
        
        results = await vertex_ai_service.batch_analyze_documents(
            documents=documents_list,
            analysis_type=analysis_type
        )
        
        return {
            "status": "success",
            "results": results,
            "analysis_type": analysis_type,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-report")
async def generate_report_with_vertex_ai(
    analysis_results: str = Form(...),  # JSON string of analysis results
    report_type: str = Form("comprehensive")
) -> Dict[str, Any]:
    """Generate comprehensive report using Vertex AI"""
    try:
        results_list = json.loads(analysis_results)
        
        report = await vertex_ai_service.generate_report(
            analysis_results=results_list,
            report_type=report_type
        )
        
        return {
            "status": "success",
            "report": report,
            "report_type": report_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-embeddings")
async def create_embeddings_with_vertex_ai(
    text: str = Form(...)
) -> Dict[str, Any]:
    """Create embeddings using Vertex AI"""
    try:
        embeddings = await vertex_ai_service.create_embeddings(text)
        
        return {
            "status": "success",
            "embeddings": embeddings,
            "dimensions": len(embeddings),
            "text_length": len(text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def vertex_ai_health_check() -> Dict[str, Any]:
    """Check Vertex AI service health"""
    try:
        # Test basic functionality
        test_result = await vertex_ai_service.generate_text(
            prompt="Hello, this is a test.",
            max_tokens=10
        )
        
        return {
            "status": "healthy",
            "service": "vertex_ai",
            "model": vertex_ai_service.model_name,
            "location": vertex_ai_service.location,
            "test_result": test_result[:50] + "..." if len(test_result) > 50 else test_result
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "vertex_ai",
            "error": str(e)
        }

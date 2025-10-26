"""
Document Analysis API Endpoints
Handles document upload, analysis, and report generation
"""

from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime

from app.services.document_analysis_service import DocumentAnalysisService
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/document-analysis", tags=["Document Analysis"])

def get_document_analysis_service() -> DocumentAnalysisService:
    return DocumentAnalysisService()

def get_rag_service() -> RAGService:
    return RAGService()

@router.post("/upload-and-analyze")
async def upload_and_analyze_documents(
    specialist_type: str = Form(...),
    user_email: str = Form(...),
    user_name: Optional[str] = Form(None),
    analysis_parameters: str = Form("{}"),  # JSON string
    files: List[UploadFile] = File(...),
    analysis_service: DocumentAnalysisService = Depends(get_document_analysis_service),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Upload documents and perform comprehensive analysis
    
    Args:
        specialist_type: Type of specialist (corrosion_engineer, subsea_engineer, etc.)
        user_email: User's email
        user_name: User's name
        analysis_parameters: JSON string with additional analysis parameters
        files: List of uploaded files (PDFs, images, documents)
    """
    try:
        # Parse analysis parameters
        try:
            parsed_parameters = json.loads(analysis_parameters)
        except json.JSONDecodeError:
            parsed_parameters = {}
        
        print(f"📁 Document upload and analysis request:")
        print(f"   Specialist: {specialist_type}")
        print(f"   User: {user_name or user_email}")
        print(f"   Files: {len(files)}")
        
        # Process uploaded files
        document_ids = []
        upload_results = []
        
        for file in files:
            try:
                # Read file content
                content = await file.read()
                
                # Generate metadata
                metadata = {
                    "original_filename": file.filename,
                    "content_type": file.content_type,
                    "upload_date": datetime.now().isoformat(),
                    "user_email": user_email,
                    "user_name": user_name,
                    "specialist_type": specialist_type
                }
                
                # Process document through RAG service
                document_id = await rag_service.process_document(
                    content=content,
                    filename=file.filename,
                    metadata=metadata
                )
                
                document_ids.append(document_id)
                upload_results.append({
                    "filename": file.filename,
                    "document_id": document_id,
                    "status": "processed"
                })
                
                print(f"✅ Processed file: {file.filename} -> {document_id}")
                
            except Exception as e:
                print(f"❌ Failed to process file {file.filename}: {e}")
                upload_results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e)
                })
        
        if not document_ids:
            raise HTTPException(status_code=400, detail="No documents could be processed")
        
        # Perform document analysis
        analysis_result = await analysis_service.analyze_uploaded_documents(
            specialist_type=specialist_type,
            document_ids=document_ids,
            user_email=user_email,
            user_name=user_name,
            analysis_parameters=parsed_parameters
        )
        
        return {
            "status": "success",
            "message": f"Analysis completed for {len(document_ids)} documents",
            "analysis_id": analysis_result["analysis_id"],
            "upload_results": upload_results,
            "analysis_summary": analysis_result["analysis_summary"],
            "key_findings": analysis_result["key_findings"],
            "risk_level": analysis_result["risk_level"],
            "recommendations": analysis_result["recommendations"],
            "report_manifest": analysis_result["report_manifest"],
            "generated_at": analysis_result["generated_at"]
        }
        
    except Exception as e:
        print(f"❌ Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze documents: {str(e)}")

@router.post("/analyze-existing-documents")
async def analyze_existing_documents(
    specialist_type: str = Form(...),
    document_ids: str = Form(...),  # JSON array of document IDs
    user_email: str = Form(...),
    user_name: Optional[str] = Form(None),
    analysis_parameters: str = Form("{}"),
    analysis_service: DocumentAnalysisService = Depends(get_document_analysis_service)
):
    """
    Analyze previously uploaded documents
    
    Args:
        specialist_type: Type of specialist
        document_ids: JSON array of existing document IDs
        user_email: User's email
        user_name: User's name
        analysis_parameters: JSON string with analysis parameters
    """
    try:
        # Parse document IDs
        try:
            parsed_document_ids = json.loads(document_ids)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid document_ids format")
        
        # Parse analysis parameters
        try:
            parsed_parameters = json.loads(analysis_parameters)
        except json.JSONDecodeError:
            parsed_parameters = {}
        
        print(f"🔍 Analyzing existing documents:")
        print(f"   Specialist: {specialist_type}")
        print(f"   Documents: {len(parsed_document_ids)}")
        print(f"   User: {user_name or user_email}")
        
        # Perform analysis
        analysis_result = await analysis_service.analyze_uploaded_documents(
            specialist_type=specialist_type,
            document_ids=parsed_document_ids,
            user_email=user_email,
            user_name=user_name,
            analysis_parameters=parsed_parameters
        )
        
        return {
            "status": "success",
            "message": f"Analysis completed for {len(parsed_document_ids)} documents",
            "analysis_result": analysis_result
        }
        
    except Exception as e:
        print(f"❌ Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze documents: {str(e)}")

@router.get("/analysis/{analysis_id}")
async def get_analysis_result(
    analysis_id: str,
    analysis_service: DocumentAnalysisService = Depends(get_document_analysis_service)
):
    """Get analysis result by ID"""
    try:
        # This would typically retrieve from a database
        # For now, return a placeholder
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "message": "Analysis result retrieval not yet implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analysis: {str(e)}")

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported document formats"""
    return {
        "status": "success",
        "supported_formats": {
            "documents": [
                {"mime_type": "application/pdf", "extension": ".pdf", "description": "PDF documents"},
                {"mime_type": "application/msword", "extension": ".doc", "description": "Word documents"},
                {"mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "extension": ".docx", "description": "Word documents (DOCX)"},
                {"mime_type": "text/plain", "extension": ".txt", "description": "Text files"}
            ],
            "images": [
                {"mime_type": "image/jpeg", "extension": ".jpg", "description": "JPEG images"},
                {"mime_type": "image/png", "extension": ".png", "description": "PNG images"},
                {"mime_type": "image/tiff", "extension": ".tiff", "description": "TIFF images"}
            ]
        },
        "limits": {
            "max_files": 10,
            "max_file_size_mb": 50,
            "max_total_size_mb": 200
        }
    }

@router.get("/specialist-types")
async def get_specialist_types():
    """Get available specialist types for analysis"""
    return {
        "status": "success",
        "specialist_types": [
            {
                "id": "corrosion_engineer",
                "name": "Corrosion Engineer",
                "description": "Material degradation, corrosion mechanisms, risk assessment"
            },
            {
                "id": "subsea_engineer", 
                "name": "Subsea Engineer",
                "description": "Offshore systems, underwater infrastructure, ROV operations"
            },
            {
                "id": "methods_specialist",
                "name": "Methods Specialist", 
                "description": "Process optimization, operational procedures, performance analysis"
            },
            {
                "id": "discipline_head",
                "name": "Discipline Head",
                "description": "Project management, strategic planning, technical leadership"
            }
        ]
    }

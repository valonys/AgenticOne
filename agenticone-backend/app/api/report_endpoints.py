"""
Report Generation API Endpoints
Handles specialist report generation and PDF conversion
"""

from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path

from app.services.report_generator import ReportGenerator
from app.services.vertex_ai_service import VertexAIService

router = APIRouter(prefix="/api/reports", tags=["Reports"])

def get_report_generator() -> ReportGenerator:
    return ReportGenerator()

def get_vertex_ai_service() -> VertexAIService:
    return VertexAIService()

@router.post("/generate")
async def generate_specialist_report(
    specialist_type: str = Form(...),
    customer_request: str = Form(...),
    user_email: str = Form(...),
    analysis_data: str = Form(...),  # JSON string
    report_generator: ReportGenerator = Depends(get_report_generator)
):
    """Generate a comprehensive report for any specialist type"""
    try:
        # Parse analysis data
        try:
            parsed_analysis_data = json.loads(analysis_data)
        except json.JSONDecodeError:
            parsed_analysis_data = {"findings": [analysis_data], "recommendations": []}
        
        print(f"📊 Report generation request:")
        print(f"   - Specialist: {specialist_type}")
        print(f"   - Customer Request: {customer_request}")
        print(f"   - Analysis Data: {parsed_analysis_data}")
        print(f"   - User Email: {user_email}")
        
        # Generate report
        report = await report_generator.generate_specialist_report(
            specialist_type=specialist_type,
            analysis_data=parsed_analysis_data,
            customer_request=customer_request,
            user_email=user_email
        )
        
        return {
            "status": "success",
            "message": f"Report generated successfully for {specialist_type}",
            "report": report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.post("/generate-from-upload")
async def generate_report_from_upload(
    specialist_type: str = Form(...),
    customer_request: str = Form(...),
    user_email: str = Form(...),
    files: List[UploadFile] = File(...),
    report_generator: ReportGenerator = Depends(get_report_generator),
    vertex_ai_service: VertexAIService = Depends(get_vertex_ai_service)
):
    """Generate report from uploaded documents"""
    try:
        # Process uploaded files
        analysis_data = {
            "findings": [],
            "recommendations": [],
            "technical_details": "",
            "uploaded_files": []
        }
        
        for file in files:
            if file.filename:
                content = await file.read()
                analysis_data["uploaded_files"].append({
                    "filename": file.filename,
                    "size": len(content),
                    "type": file.content_type
                })
                
                # Analyze document content if it's text-based
                if file.content_type and file.content_type.startswith('text/'):
                    try:
                        text_content = content.decode('utf-8')
                        # Use Vertex AI to analyze the content
                        ai_analysis = await vertex_ai_service.analyze_document(
                            text_content, 
                            f"{specialist_type} analysis"
                        )
                        analysis_data["findings"].append(f"Analysis of {file.filename}: {ai_analysis.get('generated_content', '')[:200]}...")
                    except Exception as e:
                        analysis_data["findings"].append(f"File {file.filename} uploaded but could not be analyzed: {str(e)}")
        
        # Generate report
        report = await report_generator.generate_specialist_report(
            specialist_type=specialist_type,
            analysis_data=analysis_data,
            customer_request=customer_request,
            user_email=user_email
        )
        
        return {
            "status": "success",
            "message": f"Report generated from {len(files)} uploaded files",
            "report": report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report from uploads: {str(e)}")

@router.get("/list")
async def list_available_reports(
    report_generator: ReportGenerator = Depends(get_report_generator)
):
    """Get list of available reports"""
    try:
        reports = report_generator.get_available_reports()
        return {
            "status": "success",
            "reports": reports,
            "count": len(reports)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")

@router.get("/download/{filename}")
async def download_report(filename: str):
    """Download a specific report file"""
    try:
        reports_dir = Path("reports")
        file_path = reports_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report file not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/pdf' if filename.endswith('.pdf') else 'text/html'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")

@router.get("/preview/{filename}")
async def preview_report(filename: str):
    """Preview a report in the browser"""
    try:
        reports_dir = Path("reports")
        file_path = reports_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report file not found")
        
        if filename.endswith('.html'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            return FileResponse(
                path=str(file_path),
                filename=filename,
                media_type='application/pdf'
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview report: {str(e)}")

@router.post("/convert-markdown")
async def convert_markdown_to_pdf(
    markdown_content: str = Form(...),
    output_filename: str = Form(None),
    report_generator: ReportGenerator = Depends(get_report_generator)
):
    """Convert Markdown content to PDF"""
    try:
        output_path = await report_generator.convert_markdown_to_html(
            markdown_content, 
            output_filename
        )
        
        return {
            "status": "success",
            "message": "Markdown converted to PDF successfully",
            "output_path": output_path,
            "download_url": f"/api/reports/download/{Path(output_path).name}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert Markdown to PDF: {str(e)}")

@router.get("/templates/{specialist_type}")
async def get_report_template(specialist_type: str):
    """Get a report template for a specific specialist type"""
    
    templates = {
        "corrosion_engineer": {
            "title": "Corrosion Analysis Report",
            "sections": [
                "Executive Summary",
                "Corrosion Assessment",
                "Material Analysis", 
                "Environmental Factors",
                "Risk Assessment",
                "Mitigation Recommendations",
                "Monitoring Plan",
                "Technical Specifications"
            ],
            "fields": [
                "corrosion_type",
                "severity_level", 
                "affected_areas",
                "material_composition",
                "environmental_conditions",
                "inspection_date",
                "recommended_actions"
            ]
        },
        "subsea_engineer": {
            "title": "Subsea Engineering Report",
            "sections": [
                "Executive Summary",
                "Subsea System Analysis",
                "Equipment Assessment",
                "Installation Analysis",
                "Operational Readiness",
                "Risk Assessment",
                "Maintenance Recommendations",
                "Technical Specifications"
            ],
            "fields": [
                "system_type",
                "water_depth",
                "equipment_status",
                "installation_method",
                "operational_conditions",
                "inspection_results",
                "recommended_actions"
            ]
        },
        "discipline_head": {
            "title": "Discipline Head Assessment Report",
            "sections": [
                "Executive Summary",
                "Project Overview",
                "Technical Review",
                "Resource Assessment",
                "Risk Analysis",
                "Strategic Recommendations",
                "Implementation Plan",
                "Technical Specifications"
            ],
            "fields": [
                "project_scope",
                "technical_complexity",
                "resource_requirements",
                "timeline_assessment",
                "risk_factors",
                "stakeholder_impact",
                "recommended_actions"
            ]
        },
        "methods_specialist": {
            "title": "Methods Specialist Report",
            "sections": [
                "Executive Summary",
                "Methodology Analysis",
                "Process Assessment",
                "Efficiency Analysis",
                "Risk Assessment",
                "Optimization Recommendations",
                "Implementation Plan",
                "Technical Specifications"
            ],
            "fields": [
                "method_type",
                "process_efficiency",
                "resource_utilization",
                "quality_metrics",
                "performance_indicators",
                "bottlenecks",
                "recommended_actions"
            ]
        }
    }
    
    if specialist_type not in templates:
        raise HTTPException(status_code=404, detail=f"Template not found for {specialist_type}")
    
    return {
        "status": "success",
        "template": templates[specialist_type]
    }

@router.get("/health")
async def report_service_health():
    """Check report service health"""
    try:
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        return {
            "status": "healthy",
            "service": "report_generator",
            "reports_directory": str(reports_dir),
            "directory_exists": reports_dir.exists(),
            "writable": os.access(reports_dir, os.W_OK)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report service unhealthy: {str(e)}")

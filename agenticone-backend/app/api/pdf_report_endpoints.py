"""
PDF Report Generation API Endpoints
Handles specialist PDF report generation without Vertex AI dependency
"""

from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path

from app.services.pdf_report_generator import PDFReportGenerator

router = APIRouter(prefix="/api/pdf-reports", tags=["PDF Reports"])

def get_pdf_report_generator() -> PDFReportGenerator:
    return PDFReportGenerator()

@router.post("/generate")
async def generate_specialist_pdf_report(
    specialist_type: str = Form(...),
    customer_request: str = Form(...),
    user_email: str = Form(...),
    analysis_data: str = Form(...),  # JSON string
    pdf_report_generator: PDFReportGenerator = Depends(get_pdf_report_generator)
):
    """Generate a comprehensive PDF report for any specialist type"""
    try:
        # Parse analysis data
        try:
            parsed_analysis_data = json.loads(analysis_data)
        except json.JSONDecodeError:
            parsed_analysis_data = {"findings": [analysis_data], "recommendations": []}
        
        print(f"📄 PDF Report generation request:")
        print(f"   - Specialist: {specialist_type}")
        print(f"   - Customer Request: {customer_request}")
        print(f"   - Analysis Data: {parsed_analysis_data}")
        print(f"   - User Email: {user_email}")
        
        # Generate PDF report
        report = await pdf_report_generator.generate_specialist_pdf_report(
            specialist_type=specialist_type,
            analysis_data=parsed_analysis_data,
            customer_request=customer_request,
            user_email=user_email
        )
        
        return {
            "status": "success",
            "message": f"PDF report generated successfully for {specialist_type}",
            "report": report
        }
        
    except Exception as e:
        print(f"❌ PDF Report generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")

@router.get("/download/{report_id}")
async def download_pdf_report(
    report_id: str,
    pdf_report_generator: PDFReportGenerator = Depends(get_pdf_report_generator)
):
    """Download a specific PDF report"""
    try:
        # Find the PDF file
        reports_dir = Path("reports")
        pdf_files = list(reports_dir.glob(f"*{report_id}*.pdf"))
        
        if not pdf_files:
            raise HTTPException(status_code=404, detail="PDF report not found")
        
        pdf_path = pdf_files[0]
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return FileResponse(
            path=str(pdf_path),
            filename=pdf_path.name,
            media_type="application/pdf"
        )
        
    except Exception as e:
        print(f"❌ PDF download error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download PDF: {str(e)}")

@router.get("/list")
async def list_pdf_reports(
    pdf_report_generator: PDFReportGenerator = Depends(get_pdf_report_generator)
):
    """List all available PDF reports"""
    try:
        reports_dir = Path("reports")
        pdf_files = list(reports_dir.glob("*.pdf"))
        
        reports = []
        for pdf_file in pdf_files:
            reports.append({
                "filename": pdf_file.name,
                "path": str(pdf_file),
                "size": pdf_file.stat().st_size,
                "created": datetime.fromtimestamp(pdf_file.stat().st_ctime).isoformat()
            })
        
        return {
            "status": "success",
            "reports": reports,
            "count": len(reports)
        }
        
    except Exception as e:
        print(f"❌ PDF list error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list PDF reports: {str(e)}")

@router.delete("/delete/{report_id}")
async def delete_pdf_report(
    report_id: str,
    pdf_report_generator: PDFReportGenerator = Depends(get_pdf_report_generator)
):
    """Delete a specific PDF report"""
    try:
        # Find the PDF file
        reports_dir = Path("reports")
        pdf_files = list(reports_dir.glob(f"*{report_id}*.pdf"))
        
        if not pdf_files:
            raise HTTPException(status_code=404, detail="PDF report not found")
        
        pdf_path = pdf_files[0]
        
        if pdf_path.exists():
            pdf_path.unlink()
            return {
                "status": "success",
                "message": f"PDF report {report_id} deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="PDF file not found")
        
    except Exception as e:
        print(f"❌ PDF deletion error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete PDF report: {str(e)}")

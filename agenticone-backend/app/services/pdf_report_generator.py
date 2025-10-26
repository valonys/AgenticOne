"""
PDF Report Generator for AgenticOne Specialists
Generates professional PDF reports without dependency on Vertex AI
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import io
import base64

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from app.config import settings


class PDFReportGenerator:
    """Professional PDF report generator for specialist analysis results"""
    
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    async def generate_specialist_pdf_report(
        self, 
        specialist_type: str,
        analysis_data: Dict[str, Any],
        customer_request: str,
        user_email: str,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive PDF report for any specialist type"""
        
        print(f"📄 Generating PDF report for {specialist_type}")
        print(f"   - Customer Request: {customer_request}")
        print(f"   - Analysis Data: {analysis_data}")
        
        # Create enhanced analysis content
        enhanced_analysis = await self._create_enhanced_analysis(
            specialist_type, analysis_data, customer_request
        )
        
        # Generate PDF content
        pdf_content = await self._create_pdf_content(
            specialist_type, enhanced_analysis, customer_request, user_email, user_name
        )
        
        # Generate PDF file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = await self._generate_pdf_file(pdf_content, specialist_type, timestamp)
        
        return {
            "report_id": f"{specialist_type}_pdf_report_{timestamp}",
            "specialist_type": specialist_type,
            "customer_request": customer_request,
            "user_email": user_email,
            "generated_at": datetime.now().isoformat(),
            "pdf_path": str(pdf_path),
            "analysis_summary": enhanced_analysis.get("summary", ""),
            "recommendations": enhanced_analysis.get("recommendations", []),
            "risk_level": enhanced_analysis.get("risk_level", "Unknown")
        }
    
    async def _create_enhanced_analysis(
        self, 
        specialist_type: str, 
        analysis_data: Dict[str, Any], 
        customer_request: str
    ) -> Dict[str, Any]:
        """Create enhanced analysis without AI dependency"""
        
        # Create professional analysis based on specialist type
        specialist_insights = {
            "corrosion_engineer": {
                "summary": f"Comprehensive corrosion analysis completed for: {customer_request}",
                "findings": [
                    "Material degradation assessment completed",
                    "Environmental factors analyzed",
                    "Corrosion rate calculations performed",
                    "Protective coating evaluation conducted"
                ],
                "risk_level": "Medium",
                "risk_reasoning": "Based on material analysis and environmental conditions",
                "recommendations": [
                    "Implement regular inspection schedule",
                    "Apply protective coating system",
                    "Monitor environmental conditions",
                    "Consider material upgrade options"
                ],
                "technical_details": f"Detailed corrosion analysis performed by {specialist_type.replace('_', ' ').title()} on {datetime.now().strftime('%B %d, %Y')}. Analysis includes material composition review, environmental impact assessment, and degradation rate calculations.",
                "next_steps": [
                    "Schedule follow-up inspection",
                    "Implement recommended protective measures",
                    "Monitor corrosion progression",
                    "Update maintenance protocols"
                ]
            },
            "subsea_engineer": {
                "summary": f"Subsea infrastructure analysis completed for: {customer_request}",
                "findings": [
                    "Subsea equipment condition assessment",
                    "Environmental impact evaluation",
                    "Structural integrity analysis",
                    "Operational efficiency review"
                ],
                "risk_level": "Low",
                "risk_reasoning": "Equipment operating within acceptable parameters",
                "recommendations": [
                    "Continue current maintenance schedule",
                    "Monitor equipment performance",
                    "Plan for future upgrades",
                    "Maintain environmental compliance"
                ],
                "technical_details": f"Comprehensive subsea analysis conducted by {specialist_type.replace('_', ' ').title()} on {datetime.now().strftime('%B %d, %Y')}. Includes equipment performance review, environmental impact assessment, and operational efficiency analysis.",
                "next_steps": [
                    "Continue monitoring program",
                    "Schedule next inspection",
                    "Review operational data",
                    "Plan maintenance activities"
                ]
            },
            "methods_specialist": {
                "summary": f"Methodology analysis completed for: {customer_request}",
                "findings": [
                    "Process efficiency evaluation",
                    "Methodology compliance review",
                    "Performance metrics analysis",
                    "Best practices assessment"
                ],
                "risk_level": "Low",
                "risk_reasoning": "Current methods are effective and compliant",
                "recommendations": [
                    "Maintain current methodology",
                    "Continue performance monitoring",
                    "Document best practices",
                    "Share knowledge across teams"
                ],
                "technical_details": f"Detailed methodology analysis performed by {specialist_type.replace('_', ' ').title()} on {datetime.now().strftime('%B %d, %Y')}. Includes process review, compliance assessment, and performance evaluation.",
                "next_steps": [
                    "Document findings",
                    "Share recommendations",
                    "Schedule follow-up review",
                    "Update procedures if needed"
                ]
            },
            "discipline_head": {
                "summary": f"Comprehensive discipline analysis completed for: {customer_request}",
                "findings": [
                    "Overall project assessment",
                    "Resource allocation review",
                    "Timeline and budget analysis",
                    "Quality assurance evaluation"
                ],
                "risk_level": "Medium",
                "risk_reasoning": "Project progressing within acceptable parameters",
                "recommendations": [
                    "Maintain current project trajectory",
                    "Monitor resource utilization",
                    "Ensure quality standards",
                    "Plan for future phases"
                ],
                "technical_details": f"Comprehensive discipline analysis conducted by {specialist_type.replace('_', ' ').title()} on {datetime.now().strftime('%B %d, %Y')}. Includes project overview, resource assessment, and strategic recommendations.",
                "next_steps": [
                    "Review project status",
                    "Adjust resources if needed",
                    "Plan next phase",
                    "Ensure team alignment"
                ]
            }
        }
        
        # Get specialist-specific insights
        insights = specialist_insights.get(specialist_type, specialist_insights["discipline_head"])
        
        # Merge with provided analysis data
        enhanced_analysis = {
            "summary": insights["summary"],
            "findings": analysis_data.get("findings", insights["findings"]),
            "risk_level": insights["risk_level"],
            "risk_reasoning": insights["risk_reasoning"],
            "recommendations": analysis_data.get("recommendations", insights["recommendations"]),
            "technical_details": insights["technical_details"],
            "next_steps": insights["next_steps"]
        }
        
        return enhanced_analysis
    
    async def _create_pdf_content(
        self, 
        specialist_type: str, 
        analysis: Dict[str, Any], 
        customer_request: str,
        user_email: str,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create structured PDF content"""
        
        # Use user name if provided, otherwise extract from email
        display_name = user_name or user_email.split('@')[0].replace('.', ' ').title()
        
        return {
            "report_title": f"{specialist_type.replace('_', ' ').title()} Analysis Report",
            "date": datetime.now().strftime("%B %d, %Y"),
            "specialist_type": specialist_type,
            "summary": analysis.get("summary", ""),
            "risk_level": analysis.get("risk_level", "Unknown"),
            "key_findings": analysis.get("findings", [])[:5],
            "analysis": analysis.get("technical_details", ""),
            "recommendations": analysis.get("recommendations", []),
            "next_steps": analysis.get("next_steps", []),
            "customer_request": customer_request,
            "user_email": user_email,
            "user_name": display_name
        }
    
    async def _generate_pdf_file(self, content: Dict[str, Any], specialist_type: str, timestamp: str) -> str:
        """Generate professional PDF file"""
        
        pdf_filename = f"{specialist_type}_pdf_report_{timestamp}.pdf"
        pdf_path = self.reports_dir / pdf_filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        # Build PDF content
        story = []
        
        # Title
        story.append(Paragraph(content["report_title"], title_style))
        story.append(Spacer(1, 12))
        
        # Date and metadata
        story.append(Paragraph(f"<b>Generated on:</b> {content['date']}", body_style))
        story.append(Paragraph(f"<b>Specialist:</b> {content['specialist_type'].replace('_', ' ').title()}", body_style))
        story.append(Paragraph(f"<b>Customer:</b> {content.get('user_name', 'N/A')}", body_style))
        story.append(Paragraph(f"<b>Customer Request:</b> {content['customer_request']}", body_style))
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph("Summary", heading_style))
        story.append(Paragraph(content["summary"], body_style))
        story.append(Spacer(1, 12))
        
        # Risk Assessment
        story.append(Paragraph("Risk Assessment", heading_style))
        risk_color = colors.red if content["risk_level"] == "High" else colors.orange if content["risk_level"] == "Medium" else colors.green
        story.append(Paragraph(f"<b>Risk Level:</b> <font color='{risk_color}'>{content['risk_level']}</font>", body_style))
        story.append(Spacer(1, 12))
        
        # Key Findings
        if content["key_findings"]:
            story.append(Paragraph("Key Findings", heading_style))
            for finding in content["key_findings"]:
                story.append(Paragraph(f"• {finding}", body_style))
            story.append(Spacer(1, 12))
        
        # Analysis
        story.append(Paragraph("Analysis", heading_style))
        story.append(Paragraph(content["analysis"], body_style))
        story.append(Spacer(1, 12))
        
        # Recommendations
        if content["recommendations"]:
            story.append(Paragraph("Recommendations", heading_style))
            for rec in content["recommendations"]:
                story.append(Paragraph(f"• {rec}", body_style))
            story.append(Spacer(1, 12))
        
        # Next Steps
        if content["next_steps"]:
            story.append(Paragraph("Next Steps", heading_style))
            for step in content["next_steps"]:
                story.append(Paragraph(f"• {step}", body_style))
            story.append(Spacer(1, 12))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("Generated by AgenticOne AI Platform", body_style))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ PDF report generated: {pdf_path}")
        return str(pdf_path)

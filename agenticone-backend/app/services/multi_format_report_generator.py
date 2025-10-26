"""
Multi-Format Report Generator Service for AgenticOne
Generates reports in Markdown, HTML, and PDF formats seamlessly during chat conversations
"""

import os
import json
import markdown2
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import io
import base64

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class MultiFormatReportGenerator:
    """Generate professional reports in multiple formats (MD, HTML, PDF)"""
    
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for each format
        (self.reports_dir / "markdown").mkdir(exist_ok=True)
        (self.reports_dir / "html").mkdir(exist_ok=True)
        (self.reports_dir / "pdf").mkdir(exist_ok=True)
    
    async def generate_chat_report(
        self,
        specialist_type: str,
        conversation_data: Dict[str, Any],
        analysis_data: Dict[str, Any],
        customer_request: str,
        user_email: str,
        user_name: Optional[str] = None,
        formats: List[str] = ["markdown", "html", "pdf"]
    ) -> Dict[str, Any]:
        """
        Generate report in multiple formats from chat conversation
        
        Args:
            specialist_type: Type of specialist (corrosion_engineer, subsea_engineer, etc.)
            conversation_data: Full conversation history
            analysis_data: Extracted analysis from conversation
            customer_request: Original customer request
            user_email: User's email
            user_name: User's name
            formats: List of formats to generate (markdown, html, pdf)
        
        Returns:
            Dictionary with paths to generated reports
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = f"{specialist_type}_report_{timestamp}"
        
        print(f"📊 Generating multi-format report: {report_id}")
        print(f"   Formats: {', '.join(formats)}")
        print(f"   User: {user_name or user_email}")
        print(f"   Request: {customer_request}")
        
        # Create unified report content structure
        report_content = await self._create_report_content(
            specialist_type=specialist_type,
            conversation_data=conversation_data,
            analysis_data=analysis_data,
            customer_request=customer_request,
            user_email=user_email,
            user_name=user_name,
            timestamp=timestamp
        )
        
        # Generate reports in requested formats
        generated_files = {}
        
        if "markdown" in formats:
            md_path = await self._generate_markdown(report_content, report_id)
            generated_files["markdown"] = str(md_path)
        
        if "html" in formats:
            html_path = await self._generate_html(report_content, report_id)
            generated_files["html"] = str(html_path)
        
        if "pdf" in formats:
            pdf_path = await self._generate_pdf(report_content, report_id)
            generated_files["pdf"] = str(pdf_path)
        
        # Create download manifest
        manifest = {
            "report_id": report_id,
            "specialist_type": specialist_type,
            "generated_at": datetime.now().isoformat(),
            "customer_request": customer_request,
            "user_email": user_email,
            "user_name": user_name,
            "files": generated_files,
            "download_links": self._create_download_links(report_id, generated_files)
        }
        
        # Save manifest
        manifest_path = self.reports_dir / f"{report_id}_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Report generated successfully in {len(generated_files)} formats")
        
        return manifest
    
    async def _create_report_content(
        self,
        specialist_type: str,
        conversation_data: Dict[str, Any],
        analysis_data: Dict[str, Any],
        customer_request: str,
        user_email: str,
        user_name: Optional[str] = None,
        timestamp: str = None
    ) -> Dict[str, Any]:
        """Create unified report content structure"""
        
        # Extract key information from conversation
        messages = conversation_data.get("messages", [])
        
        # Use user name if provided, otherwise extract from email
        display_name = user_name or user_email.split('@')[0].replace('.', ' ').title()
        
        # Create report structure
        report = {
            "metadata": {
                "title": f"{specialist_type.replace('_', ' ').title()} Analysis Report",
                "report_id": f"{specialist_type}_report_{timestamp}",
                "date": datetime.now().strftime("%B %d, %Y"),
                "time": datetime.now().strftime("%I:%M %p"),
                "specialist_type": specialist_type.replace('_', ' ').title(),
                "customer_name": display_name,
                "customer_email": user_email,
                "customer_request": customer_request,
                "report_type": "Chat Conversation Analysis"
            },
            "executive_summary": {
                "overview": analysis_data.get("summary", f"Comprehensive {specialist_type.replace('_', ' ')} analysis completed for {display_name} based on their inquiry: '{customer_request}'"),
                "key_points": self._extract_key_points(analysis_data, messages)
            },
            "conversation_context": {
                "original_request": customer_request,
                "conversation_summary": self._summarize_conversation(messages),
                "interaction_count": len(messages),
                "customer_name": display_name
            },
            "findings": {
                "key_findings": analysis_data.get("findings", []),
                "technical_details": analysis_data.get("technical_details", ""),
                "observations": self._extract_observations(messages)
            },
            "risk_assessment": {
                "risk_level": analysis_data.get("risk_level", "Medium"),
                "risk_reasoning": analysis_data.get("risk_reasoning", "Based on analysis performed"),
                "risk_factors": self._extract_risk_factors(analysis_data)
            },
            "recommendations": {
                "immediate_actions": analysis_data.get("recommendations", [])[:3],
                "short_term": analysis_data.get("recommendations", [])[3:6],
                "long_term": analysis_data.get("recommendations", [])[6:],
                "priority": "High"
            },
            "next_steps": {
                "actions": analysis_data.get("next_steps", []),
                "timeline": "As discussed",
                "follow_up": "Schedule follow-up consultation as needed"
            },
            "appendix": {
                "conversation_transcript": self._format_conversation_transcript(messages),
                "references": self._generate_references(specialist_type),
                "contact_info": f"For questions, contact your AgenticOne {specialist_type.replace('_', ' ')} specialist"
            }
        }
        
        return report
    
    def _extract_key_points(self, analysis_data: Dict[str, Any], messages: List[Dict[str, Any]]) -> List[str]:
        """Extract key points from analysis"""
        key_points = []
        
        findings = analysis_data.get("findings", [])
        if findings:
            key_points.extend(findings[:3])
        
        recommendations = analysis_data.get("recommendations", [])
        if recommendations:
            key_points.append(f"Primary recommendation: {recommendations[0]}")
        
        if not key_points:
            key_points = [
                "Comprehensive specialist consultation completed",
                "Technical analysis performed",
                "Actionable recommendations provided"
            ]
        
        return key_points
    
    def _summarize_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Summarize conversation flow"""
        if not messages:
            return "Detailed technical consultation conducted with specialist."
        
        summary = f"Interactive consultation involving {len(messages)} exchanges with the customer. "
        summary += "Customer inquiry addressed with detailed technical analysis and expert recommendations."
        
        return summary
    
    def _extract_observations(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract key observations from messages"""
        observations = []
        
        for msg in messages:
            content = msg.get("content", "")
            # Extract sentences that contain key terms
            if any(term in content.lower() for term in ["observed", "noted", "identified", "detected", "found"]):
                # Extract first relevant sentence
                sentences = content.split('.')
                for sentence in sentences[:2]:
                    if len(sentence.strip()) > 20:
                        observations.append(sentence.strip())
        
        if not observations:
            observations = [
                "Detailed technical review completed",
                "Comprehensive analysis performed",
                "Expert consultation provided"
            ]
        
        return observations[:5]
    
    def _extract_risk_factors(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Extract risk factors"""
        risk_factors = []
        
        findings = analysis_data.get("findings", [])
        for finding in findings:
            if any(term in finding.lower() for term in ["risk", "concern", "issue", "problem", "critical"]):
                risk_factors.append(finding)
        
        if not risk_factors:
            risk_factors = [
                "Standard operational considerations",
                "Routine monitoring requirements",
                "Regular maintenance needs"
            ]
        
        return risk_factors[:5]
    
    def _format_conversation_transcript(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format conversation transcript"""
        transcript = []
        
        for i, msg in enumerate(messages, 1):
            transcript.append({
                "number": str(i),
                "role": msg.get("role", "user").title(),
                "content": msg.get("content", "")[:500],  # Limit length
                "timestamp": msg.get("timestamp", "")
            })
        
        return transcript
    
    def _generate_references(self, specialist_type: str) -> List[str]:
        """Generate relevant references based on specialist type"""
        references = {
            "corrosion_engineer": [
                "API 510: Pressure Vessel Inspection Code",
                "NACE SP0191: Application of Internal Linings",
                "ISO 12944: Corrosion Protection Standards",
                "ASME Section VIII: Pressure Vessel Code"
            ],
            "subsea_engineer": [
                "API 17D: Subsea Wellhead and Tree Equipment",
                "ISO 13628: Petroleum and natural gas industries",
                "DNV-RP-F109: Subsea Pipeline Systems",
                "API 6A: Wellhead and Christmas Tree Equipment"
            ],
            "methods_specialist": [
                "ISO 9001: Quality Management Systems",
                "API 570: Piping Inspection Code",
                "ASME B31.3: Process Piping",
                "Company Standard Operating Procedures"
            ],
            "discipline_head": [
                "PMI PMBOK: Project Management Body of Knowledge",
                "ISO 31000: Risk Management",
                "Company Project Management Standards",
                "Industry Best Practices Guidelines"
            ]
        }
        
        return references.get(specialist_type, [
            "Industry Standard Practices",
            "Technical Guidelines",
            "Company Procedures"
        ])
    
    async def _generate_markdown(self, content: Dict[str, Any], report_id: str) -> Path:
        """Generate Markdown report"""
        
        md_path = self.reports_dir / "markdown" / f"{report_id}.md"
        
        md_content = f"""# {content['metadata']['title']}

---

**Report ID:** {content['metadata']['report_id']}  
**Date:** {content['metadata']['date']}  
**Time:** {content['metadata']['time']}  
**Specialist:** {content['metadata']['specialist_type']}  
**Customer:** {content['metadata']['customer_name']}  
**Customer Request:** {content['metadata']['customer_request']}  
**Report Type:** {content['metadata']['report_type']}

---

## Executive Summary

{content['executive_summary']['overview']}

### Key Points
"""
        
        for point in content['executive_summary']['key_points']:
            md_content += f"\n- {point}"
        
        md_content += f"""

---

## Conversation Context

**Customer:** {content['conversation_context']['customer_name']}  
**Original Request:** {content['conversation_context']['original_request']}

**Summary:** {content['conversation_context']['conversation_summary']}

**Total Interactions:** {content['conversation_context']['interaction_count']}

---

## Findings

### Key Findings
"""
        
        for finding in content['findings']['key_findings']:
            md_content += f"\n- {finding}"
        
        md_content += f"""

### Technical Details

{content['findings']['technical_details']}

### Observations
"""
        
        for obs in content['findings']['observations']:
            md_content += f"\n- {obs}"
        
        md_content += f"""

---

## Risk Assessment

**Risk Level:** {content['risk_assessment']['risk_level']}

**Risk Reasoning:** {content['risk_assessment']['risk_reasoning']}

### Risk Factors
"""
        
        for factor in content['risk_assessment']['risk_factors']:
            md_content += f"\n- {factor}"
        
        md_content += """

---

## Recommendations

### Immediate Actions
"""
        
        for action in content['recommendations']['immediate_actions']:
            md_content += f"\n1. {action}"
        
        if content['recommendations']['short_term']:
            md_content += "\n\n### Short-Term Actions\n"
            for action in content['recommendations']['short_term']:
                md_content += f"\n1. {action}"
        
        if content['recommendations']['long_term']:
            md_content += "\n\n### Long-Term Actions\n"
            for action in content['recommendations']['long_term']:
                md_content += f"\n1. {action}"
        
        md_content += f"""

**Priority Level:** {content['recommendations']['priority']}

---

## Next Steps

### Action Items
"""
        
        for step in content['next_steps']['actions']:
            md_content += f"\n- {step}"
        
        md_content += f"""

**Timeline:** {content['next_steps']['timeline']}

**Follow-up:** {content['next_steps']['follow_up']}

---

## Appendix

### References
"""
        
        for ref in content['appendix']['references']:
            md_content += f"\n- {ref}"
        
        md_content += f"""

### Contact Information

{content['appendix']['contact_info']}

---

*Generated by AgenticOne AI Platform*  
*Report Date: {content['metadata']['date']} at {content['metadata']['time']}*
"""
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ Markdown report generated: {md_path}")
        return md_path
    
    async def _generate_html(self, content: Dict[str, Any], report_id: str) -> Path:
        """Generate HTML report with professional styling"""
        
        html_path = self.reports_dir / "html" / f"{report_id}.html"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content['metadata']['title']}</title>
    <style>
        @media print {{
            body {{ margin: 0; }}
            .no-print {{ display: none; }}
            .page-break {{ page-break-before: always; }}
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 210mm;
            margin: 0 auto;
            padding: 20mm;
            background: #f5f5f5;
        }}
        
        .report-container {{
            background: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #003366;
            border-bottom: 4px solid #003366;
            padding-bottom: 15px;
            font-size: 28px;
            margin-top: 0;
        }}
        
        h2 {{
            color: #003366;
            font-size: 22px;
            margin-top: 35px;
            border-left: 5px solid #0066cc;
            padding-left: 15px;
        }}
        
        h3 {{
            color: #0066cc;
            font-size: 18px;
            margin-top: 25px;
        }}
        
        .metadata-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            background-color: #f9f9f9;
        }}
        
        .metadata-table td {{
            padding: 12px;
            border: 1px solid #ddd;
        }}
        
        .metadata-table td:first-child {{
            font-weight: bold;
            background-color: #e8e8e8;
            width: 30%;
        }}
        
        .risk-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .risk-high {{
            background-color: #ff6666;
            color: white;
        }}
        
        .risk-medium {{
            background-color: #ffaa66;
            color: white;
        }}
        
        .risk-low {{
            background-color: #90EE90;
            color: #333;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 10px 0;
            line-height: 1.8;
        }}
        
        .section {{
            margin: 30px 0;
            padding: 20px;
            background-color: #fafafa;
            border-left: 3px solid #0066cc;
        }}
        
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        
        .download-buttons {{
            margin: 20px 0;
            padding: 15px;
            background-color: #e3f2fd;
            border-radius: 5px;
            text-align: center;
        }}
        
        .download-btn {{
            display: inline-block;
            padding: 10px 20px;
            margin: 5px;
            background-color: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }}
        
        .download-btn:hover {{
            background-color: #003366;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #0066cc;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <h1>{content['metadata']['title']}</h1>
        
        <table class="metadata-table">
            <tr>
                <td>Report ID</td>
                <td>{content['metadata']['report_id']}</td>
            </tr>
            <tr>
                <td>Date</td>
                <td>{content['metadata']['date']}</td>
            </tr>
            <tr>
                <td>Time</td>
                <td>{content['metadata']['time']}</td>
            </tr>
            <tr>
                <td>Specialist</td>
                <td>{content['metadata']['specialist_type']}</td>
            </tr>
            <tr>
                <td>Customer</td>
                <td>{content['metadata']['customer_name']}</td>
            </tr>
            <tr>
                <td>Customer Request</td>
                <td>{content['metadata']['customer_request']}</td>
            </tr>
            <tr>
                <td>Report Type</td>
                <td>{content['metadata']['report_type']}</td>
            </tr>
        </table>
        
        <div class="download-buttons no-print">
            <p><strong>Download this report in other formats:</strong></p>
            <a href="../markdown/{report_id}.md" class="download-btn" download>📄 Markdown</a>
            <a href="../pdf/{report_id}.pdf" class="download-btn" download>📕 PDF</a>
            <a href="javascript:window.print()" class="download-btn">🖨️ Print</a>
        </div>
        
        <hr>
        
        <h2>Executive Summary</h2>
        <div class="section">
            <p>{content['executive_summary']['overview']}</p>
            
            <h3>Key Points</h3>
            <ul>
"""
        
        for point in content['executive_summary']['key_points']:
            html_content += f"                <li>{point}</li>\n"
        
        html_content += f"""            </ul>
        </div>
        
        <h2>Conversation Context</h2>
        <div class="section">
            <p><strong>Customer:</strong> {content['conversation_context']['customer_name']}</p>
            <p><strong>Original Request:</strong> {content['conversation_context']['original_request']}</p>
            <p><strong>Summary:</strong> {content['conversation_context']['conversation_summary']}</p>
            <p><strong>Total Interactions:</strong> {content['conversation_context']['interaction_count']}</p>
        </div>
        
        <h2>Findings</h2>
        <div class="section">
            <h3>Key Findings</h3>
            <ul>
"""
        
        for finding in content['findings']['key_findings']:
            html_content += f"                <li>{finding}</li>\n"
        
        html_content += f"""            </ul>
            
            <h3>Technical Details</h3>
            <p>{content['findings']['technical_details']}</p>
            
            <h3>Observations</h3>
            <ul>
"""
        
        for obs in content['findings']['observations']:
            html_content += f"                <li>{obs}</li>\n"
        
        risk_class = f"risk-{content['risk_assessment']['risk_level'].lower()}"
        
        html_content += f"""            </ul>
        </div>
        
        <h2>Risk Assessment</h2>
        <div class="section">
            <p><strong>Risk Level:</strong> <span class="risk-badge {risk_class}">{content['risk_assessment']['risk_level']}</span></p>
            <p><strong>Risk Reasoning:</strong> {content['risk_assessment']['risk_reasoning']}</p>
            
            <h3>Risk Factors</h3>
            <ul>
"""
        
        for factor in content['risk_assessment']['risk_factors']:
            html_content += f"                <li>{factor}</li>\n"
        
        html_content += """            </ul>
        </div>
        
        <h2>Recommendations</h2>
        <div class="section">
            <h3>Immediate Actions</h3>
            <ol>
"""
        
        for action in content['recommendations']['immediate_actions']:
            html_content += f"                <li>{action}</li>\n"
        
        if content['recommendations']['short_term']:
            html_content += """            </ol>
            
            <h3>Short-Term Actions</h3>
            <ol>
"""
            for action in content['recommendations']['short_term']:
                html_content += f"                <li>{action}</li>\n"
        
        if content['recommendations']['long_term']:
            html_content += """            </ol>
            
            <h3>Long-Term Actions</h3>
            <ol>
"""
            for action in content['recommendations']['long_term']:
                html_content += f"                <li>{action}</li>\n"
        
        html_content += f"""            </ol>
            
            <div class="highlight">
                <strong>Priority Level:</strong> {content['recommendations']['priority']}
            </div>
        </div>
        
        <h2>Next Steps</h2>
        <div class="section">
            <h3>Action Items</h3>
            <ul>
"""
        
        for step in content['next_steps']['actions']:
            html_content += f"                <li>{step}</li>\n"
        
        html_content += f"""            </ul>
            
            <p><strong>Timeline:</strong> {content['next_steps']['timeline']}</p>
            <p><strong>Follow-up:</strong> {content['next_steps']['follow_up']}</p>
        </div>
        
        <div class="page-break"></div>
        
        <h2>Appendix</h2>
        <div class="section">
            <h3>References</h3>
            <ul>
"""
        
        for ref in content['appendix']['references']:
            html_content += f"                <li>{ref}</li>\n"
        
        html_content += f"""            </ul>
            
            <h3>Contact Information</h3>
            <p>{content['appendix']['contact_info']}</p>
        </div>
        
        <div class="footer">
            <p><strong>Generated by AgenticOne AI Platform</strong></p>
            <p>Report Date: {content['metadata']['date']} at {content['metadata']['time']}</p>
        </div>
    </div>
</body>
</html>"""
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report generated: {html_path}")
        return html_path
    
    async def _generate_pdf(self, content: Dict[str, Any], report_id: str) -> Path:
        """Generate PDF report using ReportLab"""
        
        pdf_path = self.reports_dir / "pdf" / f"{report_id}.pdf"
        
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#003366')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#003366')
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor('#0066cc')
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        )
        
        # Build PDF
        story = []
        
        # Title
        story.append(Paragraph(content['metadata']['title'], title_style))
        story.append(Spacer(1, 20))
        
        # Metadata table
        metadata_data = [
            ['Report ID:', content['metadata']['report_id']],
            ['Date:', content['metadata']['date']],
            ['Time:', content['metadata']['time']],
            ['Specialist:', content['metadata']['specialist_type']],
            ['Customer:', content['metadata']['customer_name']],
            ['Request:', content['metadata']['customer_request']],
            ['Type:', content['metadata']['report_type']]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 30))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(content['executive_summary']['overview'], body_style))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph("Key Points", subheading_style))
        for point in content['executive_summary']['key_points']:
            story.append(Paragraph(f"• {point}", body_style))
        story.append(Spacer(1, 20))
        
        # Conversation Context
        story.append(Paragraph("Conversation Context", heading_style))
        story.append(Paragraph(f"<b>Customer:</b> {content['conversation_context']['customer_name']}", body_style))
        story.append(Paragraph(f"<b>Original Request:</b> {content['conversation_context']['original_request']}", body_style))
        story.append(Paragraph(f"<b>Summary:</b> {content['conversation_context']['conversation_summary']}", body_style))
        story.append(Paragraph(f"<b>Total Interactions:</b> {content['conversation_context']['interaction_count']}", body_style))
        story.append(Spacer(1, 20))
        
        # Findings
        story.append(Paragraph("Findings", heading_style))
        story.append(Paragraph("Key Findings", subheading_style))
        for finding in content['findings']['key_findings']:
            story.append(Paragraph(f"• {finding}", body_style))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph("Technical Details", subheading_style))
        story.append(Paragraph(content['findings']['technical_details'], body_style))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph("Observations", subheading_style))
        for obs in content['findings']['observations']:
            story.append(Paragraph(f"• {obs}", body_style))
        story.append(Spacer(1, 20))
        
        # Risk Assessment
        story.append(Paragraph("Risk Assessment", heading_style))
        
        risk_color = colors.red if content['risk_assessment']['risk_level'] == "High" else \
                     colors.orange if content['risk_assessment']['risk_level'] == "Medium" else \
                     colors.green
        
        story.append(Paragraph(
            f"<b>Risk Level:</b> <font color='{risk_color}'>{content['risk_assessment']['risk_level']}</font>",
            body_style
        ))
        story.append(Paragraph(f"<b>Risk Reasoning:</b> {content['risk_assessment']['risk_reasoning']}", body_style))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph("Risk Factors", subheading_style))
        for factor in content['risk_assessment']['risk_factors']:
            story.append(Paragraph(f"• {factor}", body_style))
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Recommendations", heading_style))
        
        if content['recommendations']['immediate_actions']:
            story.append(Paragraph("Immediate Actions", subheading_style))
            for i, action in enumerate(content['recommendations']['immediate_actions'], 1):
                story.append(Paragraph(f"{i}. {action}", body_style))
            story.append(Spacer(1, 10))
        
        if content['recommendations']['short_term']:
            story.append(Paragraph("Short-Term Actions", subheading_style))
            for i, action in enumerate(content['recommendations']['short_term'], 1):
                story.append(Paragraph(f"{i}. {action}", body_style))
            story.append(Spacer(1, 10))
        
        if content['recommendations']['long_term']:
            story.append(Paragraph("Long-Term Actions", subheading_style))
            for i, action in enumerate(content['recommendations']['long_term'], 1):
                story.append(Paragraph(f"{i}. {action}", body_style))
            story.append(Spacer(1, 10))
        
        story.append(Paragraph(f"<b>Priority Level:</b> {content['recommendations']['priority']}", body_style))
        story.append(Spacer(1, 20))
        
        # Next Steps
        story.append(Paragraph("Next Steps", heading_style))
        story.append(Paragraph("Action Items", subheading_style))
        for step in content['next_steps']['actions']:
            story.append(Paragraph(f"• {step}", body_style))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(f"<b>Timeline:</b> {content['next_steps']['timeline']}", body_style))
        story.append(Paragraph(f"<b>Follow-up:</b> {content['next_steps']['follow_up']}", body_style))
        story.append(Spacer(1, 30))
        
        # Page break for appendix
        story.append(PageBreak())
        
        # Appendix
        story.append(Paragraph("Appendix", heading_style))
        story.append(Paragraph("References", subheading_style))
        for ref in content['appendix']['references']:
            story.append(Paragraph(f"• {ref}", body_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("Contact Information", subheading_style))
        story.append(Paragraph(content['appendix']['contact_info'], body_style))
        story.append(Spacer(1, 30))
        
        # Footer
        story.append(Paragraph("Generated by AgenticOne AI Platform", body_style))
        story.append(Paragraph(
            f"Report Date: {content['metadata']['date']} at {content['metadata']['time']}",
            body_style
        ))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ PDF report generated: {pdf_path}")
        return pdf_path
    
    def _create_download_links(self, report_id: str, generated_files: Dict[str, str]) -> Dict[str, str]:
        """Create download links for generated reports"""
        
        links = {}
        base_url = "/api/reports/download"  # Adjust based on your API structure
        
        for format_type, file_path in generated_files.items():
            filename = Path(file_path).name
            links[format_type] = f"{base_url}/{format_type}/{filename}"
        
        return links
    
    async def get_report_manifest(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report manifest by ID"""
        
        manifest_path = self.reports_dir / f"{report_id}_manifest.json"
        
        if not manifest_path.exists():
            return None
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def list_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent reports"""
        
        manifests = []
        
        for manifest_file in sorted(
            self.reports_dir.glob("*_manifest.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifests.append(json.load(f))
        
        return manifests

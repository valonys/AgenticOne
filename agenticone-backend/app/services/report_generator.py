"""
Professional Report Generator for AgenticOne Specialists
Generates comprehensive analysis reports with HTML output
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import markdown
from jinja2 import Template

from app.config import settings
from app.services.vertex_ai_service import VertexAIService


class ReportGenerator:
    """Professional report generator for specialist analysis results"""
    
    def __init__(self):
        self.vertex_ai_service = VertexAIService()
        self.templates_dir = Path("templates")
        self.reports_dir = Path("reports")
        self.templates_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Template mapping for different specialist types
        self.template_mapping = {
            "corrosion_engineer": "corrosion_report_template.html",
            "subsea_engineer": "subsea_report_template.html", 
            "methods_specialist": "methods_report_template.html",
            "discipline_head": "corrosion_report_template.html"  # Default template
        }
        
    async def generate_specialist_report(
        self, 
        specialist_type: str,
        analysis_data: Dict[str, Any],
        customer_request: str,
        user_email: str
    ) -> Dict[str, Any]:
        """Generate a comprehensive report for any specialist type"""
        
        # Generate AI-enhanced analysis
        enhanced_analysis = await self._enhance_analysis_with_ai(
            specialist_type, analysis_data, customer_request
        )
        
        # Create report content
        report_content = await self._create_report_content(
            specialist_type, enhanced_analysis, customer_request, user_email
        )
        
        # Generate HTML version
        html_report = await self._generate_html_report(report_content, specialist_type)
        
        # Generate HTML file (print-ready)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = await self._generate_html_file(html_report, specialist_type, timestamp)
        
        return {
            "report_id": f"{specialist_type}_report_{timestamp}",
            "specialist_type": specialist_type,
            "customer_request": customer_request,
            "user_email": user_email,
            "generated_at": datetime.now().isoformat(),
            "html_content": html_report,
            "html_path": str(html_path),
            "analysis_summary": enhanced_analysis.get("summary", ""),
            "recommendations": enhanced_analysis.get("recommendations", []),
            "risk_level": enhanced_analysis.get("risk_level", "Unknown")
        }
    
    async def _enhance_analysis_with_ai(
        self, 
        specialist_type: str, 
        analysis_data: Dict[str, Any], 
        customer_request: str
    ) -> Dict[str, Any]:
        """Use Vertex AI to enhance the analysis with professional insights"""
        
        prompt = f"""
        As a {specialist_type} specialist, analyze the following data and provide a comprehensive professional assessment:
        
        Customer Request: {customer_request}
        
        Analysis Data: {json.dumps(analysis_data, indent=2)}
        
        Please provide:
        1. Executive Summary (2-3 sentences)
        2. Key Findings (bullet points)
        3. Risk Assessment (Low/Medium/High with reasoning)
        4. Recommendations (actionable items)
        5. Technical Details (if applicable)
        6. Next Steps
        
        Format as JSON with these exact keys: summary, findings, risk_level, risk_reasoning, recommendations, technical_details, next_steps
        """
        
        try:
            ai_response = await self.vertex_ai_service.generate_text(prompt)
            print(f"🤖 AI Response for {specialist_type}: {ai_response[:200]}...")
            
            # Try to parse JSON response from AI
            try:
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    ai_data = json.loads(json_match.group())
                    return {
                        "summary": ai_data.get("summary", f"AI-enhanced analysis for {specialist_type}"),
                        "findings": ai_data.get("findings", analysis_data.get("findings", [])),
                        "risk_level": ai_data.get("risk_level", "Medium"),
                        "risk_reasoning": ai_data.get("risk_reasoning", "Based on AI analysis"),
                        "recommendations": ai_data.get("recommendations", analysis_data.get("recommendations", [])),
                        "technical_details": ai_data.get("technical_details", analysis_data.get("technical_details", "")),
                        "next_steps": ai_data.get("next_steps", ["Review findings", "Implement recommendations"]),
                        "ai_insights": ai_response
                    }
            except json.JSONDecodeError:
                pass
            
            # If JSON parsing fails, use the raw AI response
            return {
                "summary": f"AI-enhanced analysis for {specialist_type}",
                "findings": analysis_data.get("findings", []),
                "risk_level": "Medium",
                "risk_reasoning": "Based on AI analysis",
                "recommendations": analysis_data.get("recommendations", []),
                "technical_details": analysis_data.get("technical_details", ""),
                "next_steps": ["Review findings", "Implement recommendations"],
                "ai_insights": ai_response
            }
        except Exception as e:
            print(f"⚠️ AI enhancement failed: {e}")
            # Fallback to basic analysis
            return {
                "summary": f"Analysis completed for {specialist_type}",
                "findings": analysis_data.get("findings", []),
                "risk_level": "Unknown",
                "risk_reasoning": "Analysis in progress",
                "recommendations": analysis_data.get("recommendations", []),
                "technical_details": analysis_data.get("technical_details", ""),
                "next_steps": ["Review findings"],
                "ai_insights": "AI enhancement temporarily unavailable"
            }
    
    async def _create_report_content(
        self, 
        specialist_type: str, 
        analysis: Dict[str, Any], 
        customer_request: str,
        user_email: str
    ) -> Dict[str, Any]:
        """Create structured report content"""
        
        # Create meaningful fallback content
        summary = analysis.get("summary", "")
        if not summary:
            summary = f"Professional analysis completed by {specialist_type.replace('_', ' ').title()} based on customer request: '{customer_request}'"
        
        analysis_content = analysis.get("technical_details", "")
        if not analysis_content:
            analysis_content = f"Conversation with {specialist_type.replace('_', ' ').title()} on {datetime.now().strftime('%m/%d/%Y')}"
        
        recommendations = analysis.get("recommendations", [])
        if not recommendations:
            recommendations = ["Detailed recommendations will be provided based on further analysis"]
        
        return {
            "report_title": f"{specialist_type.replace('_', ' ').title()} Analysis Report",
            "date": datetime.now().strftime("%B %d, %Y"),
            "summary": summary,
            "risk_level": analysis.get("risk_level", "Unknown"),
            "key_findings": analysis.get("findings", [])[:5],
            "analysis": analysis_content,
            "recommendations": recommendations,
            "next_steps": analysis.get("next_steps", ["Review findings", "Implement recommendations"]),
            "ai_insights": analysis.get("ai_insights", ""),
            "customer_request": customer_request,
            "user_email": user_email
        }
    
    async def _generate_html_report(self, content: Dict[str, Any], specialist_type: str = "corrosion_engineer") -> str:
        """Generate professional HTML report using specialist-specific templates"""
        
        # Get the appropriate template for the specialist type
        template_filename = self.template_mapping.get(specialist_type, "corrosion_report_template.html")
        template_path = self.templates_dir / template_filename
        
        if template_path.exists():
            # Load template from file
            with open(template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
        else:
            # Fallback to basic template
            html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{{ report_title or 'Professional Report' }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
                .section { margin-bottom: 30px; padding: 20px; border-left: 4px solid #007bff; }
                h1, h2, h3 { color: #333; }
                .footer { margin-top: 50px; text-align: center; color: #6c757d; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ report_title or 'Professional Report' }}</h1>
                <p>Generated on: {{ date or 'N/A' }}</p>
            </div>
            
            <div class="section">
                <h2>Summary</h2>
                <p>{{ summary }}</p>
            </div>
            
            <div class="section">
                <h2>Analysis</h2>
                <p>{{ analysis }}</p>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                {% if recommendations %}
                    {% if recommendations is string %}
                        <p>{{ recommendations }}</p>
                    {% else %}
                        <ul>
                            {% for rec in recommendations %}
                                <li>{{ rec }}</li>
                            {% endfor %}
                        </ul>
                    {% endif %}
                {% else %}
                    <p>Detailed recommendations will be provided based on further analysis</p>
                {% endif %}
            </div>
            
            <div class="footer">
                <p>Generated by AgenticOne AI Platform</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        return template.render(**content)
    
    async def _generate_html_file(self, html_content: str, specialist_type: str, timestamp: str = None) -> str:
        """Generate HTML file (print-ready for PDF conversion)"""
        
        # Generate HTML file with print-optimized CSS
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"{specialist_type}_report_{timestamp}.html"
        html_path = self.reports_dir / html_filename
        
        # Add print-specific CSS for better PDF conversion
        print_optimized_html = html_content.replace(
            '<style>',
            '''<style>
                @media print {
                    body { margin: 0; padding: 20px; }
                    .container { max-width: none; }
                    .section { break-inside: avoid; page-break-inside: avoid; }
                    .header { break-after: avoid; }
                    h1, h2, h3 { break-after: avoid; }
                }
            </style>'''
        )
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(print_optimized_html)
        
        return str(html_path)
    
    async def convert_markdown_to_html(self, markdown_content: str, output_path: str = None) -> str:
        """Convert Markdown content to HTML (print-ready for PDF conversion)"""
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"report_{timestamp}.html"
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            markdown_content, 
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # Add CSS styling with print optimization
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Professional Report</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    line-height: 1.6; 
                    margin: 40px; 
                    color: #333;
                }}
                h1, h2, h3 {{ 
                    color: #333; 
                    margin-top: 30px;
                    margin-bottom: 15px;
                }}
                h1 {{ font-size: 2.2em; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                h2 {{ font-size: 1.8em; color: #667eea; }}
                h3 {{ font-size: 1.4em; }}
                table {{ 
                    border-collapse: collapse; 
                    width: 100%; 
                    margin: 20px 0; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                th, td {{ 
                    border: 1px solid #ddd; 
                    padding: 12px; 
                    text-align: left; 
                }}
                th {{ 
                    background-color: #f2f2f2; 
                    font-weight: 600;
                }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .risk-high {{ color: #dc3545; font-weight: bold; }}
                .risk-medium {{ color: #ffc107; font-weight: bold; }}
                .risk-low {{ color: #28a745; font-weight: bold; }}
                .risk-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 15px;
                    font-size: 0.8em;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .risk-high-badge {{ background: #dc3545; color: white; }}
                .risk-medium-badge {{ background: #ffc107; color: #333; }}
                .risk-low-badge {{ background: #28a745; color: white; }}
                @media print {{ 
                    body {{ margin: 0; padding: 20px; }}
                    .section {{ break-inside: avoid; page-break-inside: avoid; }}
                    h1, h2, h3 {{ break-after: avoid; }}
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Save as HTML (print-ready)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(styled_html)
        
        return output_path
    
    def get_available_reports(self) -> List[Dict[str, Any]]:
        """Get list of available reports"""
        reports = []
        
        for report_file in self.reports_dir.glob("*"):
            if report_file.is_file():
                reports.append({
                    "filename": report_file.name,
                    "path": str(report_file),
                    "size": report_file.stat().st_size,
                    "created": datetime.fromtimestamp(report_file.stat().st_ctime).isoformat(),
                    "type": "HTML"
                })
        
        return sorted(reports, key=lambda x: x['created'], reverse=True)

"""
Report Generator Service for creating comprehensive analysis reports
"""
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.config import settings
from app.models.database import db_client

class ReportGenerator:
    """Report generator for creating comprehensive analysis reports"""
    
    def __init__(self):
        self.template_path = settings.REPORT_TEMPLATE_PATH
        self.output_path = settings.REPORT_OUTPUT_PATH
        self.status = "initialized"
    
    async def generate_report(
        self, 
        analysis_ids: List[str], 
        report_type: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive report from analysis results"""
        try:
            # Get analysis results
            analyses = await self._get_analysis_results(analysis_ids)
            
            # Generate report content
            report_content = await self._generate_report_content(analyses, report_type, template)
            
            # Create report file
            report_id = str(uuid.uuid4())
            report_url = await self._save_report(report_id, report_content, report_type)
            
            # Save report metadata
            await db_client.create_report({
                "report_id": report_id,
                "analysis_ids": analysis_ids,
                "report_type": report_type,
                "template": template,
                "report_url": report_url,
                "status": "generated"
            })
            
            return {
                "report_id": report_id,
                "report_url": report_url,
                "status": "generated"
            }
            
        except Exception as e:
            raise ValueError(f"Failed to generate report: {str(e)}")
    
    async def _get_analysis_results(self, analysis_ids: List[str]) -> List[Dict[str, Any]]:
        """Get analysis results from database"""
        try:
            analyses = []
            for analysis_id in analysis_ids:
                analysis = await db_client.get_analysis(analysis_id)
                if analysis:
                    analyses.append(analysis.dict())
            return analyses
        except Exception as e:
            raise ValueError(f"Failed to get analysis results: {str(e)}")
    
    async def _generate_report_content(
        self, 
        analyses: List[Dict[str, Any]], 
        report_type: str,
        template: Optional[str]
    ) -> str:
        """Generate report content based on analyses"""
        try:
            if template:
                return await self._generate_from_template(analyses, template)
            else:
                return await self._generate_standard_report(analyses, report_type)
        except Exception as e:
            raise ValueError(f"Failed to generate report content: {str(e)}")
    
    async def _generate_standard_report(
        self, 
        analyses: List[Dict[str, Any]], 
        report_type: str
    ) -> str:
        """Generate standard report format"""
        try:
            report_sections = []
            
            # Executive Summary
            executive_summary = await self._generate_executive_summary(analyses)
            report_sections.append(executive_summary)
            
            # Analysis Results
            analysis_results = await self._generate_analysis_results(analyses)
            report_sections.append(analysis_results)
            
            # Recommendations
            recommendations = await self._generate_recommendations(analyses)
            report_sections.append(recommendations)
            
            # Technical Details
            technical_details = await self._generate_technical_details(analyses)
            report_sections.append(technical_details)
            
            # Appendices
            appendices = await self._generate_appendices(analyses)
            report_sections.append(appendices)
            
            # Combine all sections
            report_content = "\n\n".join(report_sections)
            
            return report_content
            
        except Exception as e:
            raise ValueError(f"Failed to generate standard report: {str(e)}")
    
    async def _generate_executive_summary(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate executive summary section"""
        try:
            total_analyses = len(analyses)
            agent_types = list(set(analysis.get("agent_type", "unknown") for analysis in analyses))
            
            # Calculate overall confidence
            confidences = [analysis.get("confidence", 0) for analysis in analyses]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Count critical findings
            critical_findings = 0
            for analysis in analyses:
                results = analysis.get("results", [])
                for result in results:
                    if result.get("confidence", 0) < 0.7:
                        critical_findings += 1
            
            summary = f"""
# Executive Summary

## Overview
This report presents the results of {total_analyses} analyses conducted by specialized AI agents: {', '.join(agent_types)}.

## Key Findings
- **Overall Confidence**: {avg_confidence:.2f}
- **Critical Findings**: {critical_findings}
- **Total Recommendations**: {sum(len(analysis.get('recommendations', [])) for analysis in analyses)}

## Summary
The analysis reveals several key areas requiring attention, with varying levels of confidence across different aspects of the project. The specialized agents have provided comprehensive insights into technical, safety, and operational considerations.
"""
            return summary
            
        except Exception as e:
            return f"Executive summary generation failed: {str(e)}"
    
    async def _generate_analysis_results(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate analysis results section"""
        try:
            results_section = "# Analysis Results\n\n"
            
            for i, analysis in enumerate(analyses, 1):
                agent_type = analysis.get("agent_type", "unknown")
                confidence = analysis.get("confidence", 0)
                results = analysis.get("results", [])
                
                results_section += f"## Analysis {i}: {agent_type.replace('_', ' ').title()}\n"
                results_section += f"**Confidence**: {confidence:.2f}\n\n"
                
                for j, result in enumerate(results, 1):
                    category = result.get("category", "Unknown")
                    findings = result.get("findings", [])
                    result_confidence = result.get("confidence", 0)
                    
                    results_section += f"### {category}\n"
                    results_section += f"**Confidence**: {result_confidence:.2f}\n\n"
                    
                    if findings:
                        results_section += "**Key Findings**:\n"
                        for finding in findings:
                            results_section += f"- {finding}\n"
                        results_section += "\n"
                
                results_section += "---\n\n"
            
            return results_section
            
        except Exception as e:
            return f"Analysis results generation failed: {str(e)}"
    
    async def _generate_recommendations(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate recommendations section"""
        try:
            recommendations_section = "# Recommendations\n\n"
            
            # Collect all recommendations
            all_recommendations = []
            for analysis in analyses:
                recommendations = analysis.get("recommendations", [])
                agent_type = analysis.get("agent_type", "unknown")
                
                for rec in recommendations:
                    all_recommendations.append({
                        "recommendation": rec,
                        "agent": agent_type,
                        "priority": self._assess_priority(rec)
                    })
            
            # Sort by priority
            all_recommendations.sort(key=lambda x: x["priority"], reverse=True)
            
            # Group by priority
            high_priority = [r for r in all_recommendations if r["priority"] == "high"]
            medium_priority = [r for r in all_recommendations if r["priority"] == "medium"]
            low_priority = [r for r in all_recommendations if r["priority"] == "low"]
            
            if high_priority:
                recommendations_section += "## High Priority\n\n"
                for rec in high_priority:
                    recommendations_section += f"- **{rec['agent'].replace('_', ' ').title()}**: {rec['recommendation']}\n"
                recommendations_section += "\n"
            
            if medium_priority:
                recommendations_section += "## Medium Priority\n\n"
                for rec in medium_priority:
                    recommendations_section += f"- **{rec['agent'].replace('_', ' ').title()}**: {rec['recommendation']}\n"
                recommendations_section += "\n"
            
            if low_priority:
                recommendations_section += "## Low Priority\n\n"
                for rec in low_priority:
                    recommendations_section += f"- **{rec['agent'].replace('_', ' ').title()}**: {rec['recommendation']}\n"
                recommendations_section += "\n"
            
            return recommendations_section
            
        except Exception as e:
            return f"Recommendations generation failed: {str(e)}"
    
    async def _generate_technical_details(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate technical details section"""
        try:
            technical_section = "# Technical Details\n\n"
            
            # Document information
            technical_section += "## Document Information\n"
            technical_section += f"- **Total Analyses**: {len(analyses)}\n"
            technical_section += f"- **Report Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
            technical_section += f"- **Report Type**: Technical Analysis Report\n\n"
            
            # Agent performance
            technical_section += "## Agent Performance\n"
            for analysis in analyses:
                agent_type = analysis.get("agent_type", "unknown")
                confidence = analysis.get("confidence", 0)
                technical_section += f"- **{agent_type.replace('_', ' ').title()}**: {confidence:.2f} confidence\n"
            technical_section += "\n"
            
            # Analysis metadata
            technical_section += "## Analysis Metadata\n"
            for i, analysis in enumerate(analyses, 1):
                technical_section += f"### Analysis {i}\n"
                technical_section += f"- **Agent**: {analysis.get('agent_type', 'unknown')}\n"
                technical_section += f"- **Type**: {analysis.get('analysis_type', 'unknown')}\n"
                technical_section += f"- **Created**: {analysis.get('created_at', 'unknown')}\n"
                technical_section += f"- **Document ID**: {analysis.get('document_id', 'unknown')}\n\n"
            
            return technical_section
            
        except Exception as e:
            return f"Technical details generation failed: {str(e)}"
    
    async def _generate_appendices(self, analyses: List[Dict[str, Any]]) -> str:
        """Generate appendices section"""
        try:
            appendices_section = "# Appendices\n\n"
            
            # Appendix A: Raw Analysis Data
            appendices_section += "## Appendix A: Raw Analysis Data\n\n"
            for i, analysis in enumerate(analyses, 1):
                appendices_section += f"### Analysis {i} Raw Data\n"
                appendices_section += f"```json\n{analysis}\n```\n\n"
            
            # Appendix B: Agent Capabilities
            appendices_section += "## Appendix B: Agent Capabilities\n\n"
            agent_capabilities = {
                "discipline_head": ["project_oversight", "decision_making", "coordination"],
                "methods_specialist": ["method_analysis", "procedure_optimization", "best_practices"],
                "corrosion_engineer": ["corrosion_analysis", "material_selection", "prevention_strategies"],
                "subsea_engineer": ["subsea_systems", "underwater_operations", "marine_engineering"]
            }
            
            for agent, capabilities in agent_capabilities.items():
                appendices_section += f"### {agent.replace('_', ' ').title()}\n"
                for capability in capabilities:
                    appendices_section += f"- {capability}\n"
                appendices_section += "\n"
            
            return appendices_section
            
        except Exception as e:
            return f"Appendices generation failed: {str(e)}"
    
    def _assess_priority(self, recommendation: str) -> str:
        """Assess priority level of recommendation"""
        high_priority_keywords = ["critical", "urgent", "immediate", "safety", "failure"]
        medium_priority_keywords = ["important", "recommend", "consider", "review"]
        
        rec_lower = recommendation.lower()
        
        if any(keyword in rec_lower for keyword in high_priority_keywords):
            return "high"
        elif any(keyword in rec_lower for keyword in medium_priority_keywords):
            return "medium"
        else:
            return "low"
    
    async def _generate_from_template(
        self, 
        analyses: List[Dict[str, Any]], 
        template: str
    ) -> str:
        """Generate report from custom template"""
        try:
            # In production, you would load and process the template
            # For now, we'll create a simple template-based report
            template_content = f"""
# Custom Report Template

## Template: {template}

## Analysis Results
{await self._generate_analysis_results(analyses)}

## Recommendations
{await self._generate_recommendations(analyses)}
"""
            return template_content
            
        except Exception as e:
            raise ValueError(f"Failed to generate from template: {str(e)}")
    
    async def _save_report(
        self, 
        report_id: str, 
        content: str, 
        report_type: str
    ) -> str:
        """Save report to storage and return URL"""
        try:
            # In production, you would save to cloud storage
            # For now, we'll create a mock URL
            report_url = f"https://storage.googleapis.com/{settings.CLOUD_STORAGE_BUCKET}/reports/{report_id}.md"
            
            # In production, you would actually save the content:
            # await self._save_to_cloud_storage(report_id, content, report_type)
            
            return report_url
            
        except Exception as e:
            raise ValueError(f"Failed to save report: {str(e)}")
    
    async def get_report_status(self, report_id: str) -> Dict[str, Any]:
        """Get report generation status"""
        try:
            report = await db_client.get_report(report_id)
            if report:
                return {
                    "report_id": report_id,
                    "status": report.status,
                    "report_url": report.report_url,
                    "created_at": report.created_at
                }
            else:
                return {"error": "Report not found"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get report generator service status"""
        return {
            "status": self.status,
            "template_path": self.template_path,
            "output_path": self.output_path,
            "capabilities": [
                "executive_summary",
                "analysis_results",
                "recommendations",
                "technical_details",
                "custom_templates"
            ]
        }

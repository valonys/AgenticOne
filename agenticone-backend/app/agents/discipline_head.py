"""
Discipline Head Agent - Overall project coordination and decision making
"""
from typing import Dict, List, Any
from app.agents.base_agent import BaseAgent
from app.models.schemas import AnalysisResult

class DisciplineHead(BaseAgent):
    """Discipline Head Agent for overall project coordination"""
    
    def __init__(self, rag_service, vision_service):
        super().__init__(rag_service, vision_service)
        self.capabilities = [
            "project_oversight",
            "decision_making", 
            "coordination",
            "risk_assessment",
            "compliance_review"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities
    
    async def analyze(self, document_id: str, analysis_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis as discipline head"""
        try:
            await self.update_status("analyzing")
            
            # Preprocess document
            preprocessed = await self.preprocess_document(document_id)
            context = preprocessed["context"]
            relevant_docs = preprocessed["relevant_documents"]
            image_analysis = preprocessed["image_analysis"]
            
            # Perform comprehensive analysis
            results = []
            
            # Project overview analysis
            project_analysis = await self._analyze_project_overview(context, relevant_docs)
            results.append(project_analysis)
            
            # Risk assessment
            risk_analysis = await self._analyze_risks(context, relevant_docs)
            results.append(risk_analysis)
            
            # Compliance review
            compliance_analysis = await self._analyze_compliance(context, relevant_docs)
            results.append(compliance_analysis)
            
            # Decision points identification
            decision_analysis = await self._identify_decision_points(context, relevant_docs)
            results.append(decision_analysis)
            
            # Postprocess results
            processed_results = await self.postprocess_results(results)
            
            # Save analysis
            analysis_id = await self.save_analysis({
                "document_id": document_id,
                "agent_type": "discipline_head",
                "analysis_type": analysis_type,
                "results": [result.dict() for result in results],
                "confidence": processed_results["confidence"],
                "recommendations": processed_results["recommendations"]
            })
            
            await self.update_status("completed")
            
            return {
                "analysis_id": analysis_id,
                "results": [result.dict() for result in results],
                "confidence": processed_results["confidence"],
                "recommendations": processed_results["recommendations"]
            }
            
        except Exception as e:
            await self.update_status("error", {"error": str(e)})
            raise
    
    async def _analyze_project_overview(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze project overview and scope"""
        findings = []
        confidence = 0.8
        
        # Analyze document type and content
        if context["document_type"] == "pdf":
            findings.append("Technical document identified - requires detailed review")
            confidence += 0.1
        
        # Check for project scope indicators
        content_lower = context["content"].lower()
        if "project scope" in content_lower or "objectives" in content_lower:
            findings.append("Project scope clearly defined")
            confidence += 0.1
        
        if "timeline" in content_lower or "schedule" in content_lower:
            findings.append("Project timeline identified")
            confidence += 0.05
        
        # Check relevant documents for context
        if relevant_docs:
            findings.append(f"Found {len(relevant_docs)} related documents for context")
            confidence += 0.05
        
        return self.create_analysis_result(
            category="Project Overview",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"document_type": context["document_type"], "related_docs": len(relevant_docs)}
        )
    
    async def _analyze_risks(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze project risks and mitigation strategies"""
        findings = []
        confidence = 0.7
        
        content_lower = context["content"].lower()
        
        # Risk indicators
        risk_keywords = ["risk", "hazard", "safety", "failure", "critical", "urgent"]
        risk_count = sum(1 for keyword in risk_keywords if keyword in content_lower)
        
        if risk_count > 0:
            findings.append(f"Identified {risk_count} risk-related terms")
            confidence += 0.1
        
        if "safety" in content_lower:
            findings.append("Safety considerations identified")
            confidence += 0.1
        
        if "critical" in content_lower or "urgent" in content_lower:
            findings.append("Critical or urgent items identified")
            confidence += 0.15
        
        # Check for mitigation strategies
        if "mitigation" in content_lower or "prevention" in content_lower:
            findings.append("Risk mitigation strategies present")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Risk Assessment",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"risk_indicators": risk_count}
        )
    
    async def _analyze_compliance(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze compliance with standards and regulations"""
        findings = []
        confidence = 0.75
        
        content_lower = context["content"].lower()
        
        # Compliance indicators
        compliance_keywords = ["standard", "regulation", "code", "compliance", "requirement", "specification"]
        compliance_count = sum(1 for keyword in compliance_keywords if keyword in content_lower)
        
        if compliance_count > 0:
            findings.append(f"Identified {compliance_count} compliance-related terms")
            confidence += 0.1
        
        # Industry standards
        standards = ["api", "asme", "astm", "iso", "ansi", "nace"]
        found_standards = [std for std in standards if std in content_lower]
        
        if found_standards:
            findings.append(f"References to standards: {', '.join(found_standards)}")
            confidence += 0.15
        
        # Regulatory requirements
        if "regulation" in content_lower or "regulatory" in content_lower:
            findings.append("Regulatory requirements identified")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Compliance Review",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"compliance_indicators": compliance_count, "standards": found_standards}
        )
    
    async def _identify_decision_points(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Identify key decision points and recommendations"""
        findings = []
        confidence = 0.8
        
        content_lower = context["content"].lower()
        
        # Decision indicators
        decision_keywords = ["decision", "recommendation", "conclusion", "action", "next step"]
        decision_count = sum(1 for keyword in decision_keywords if keyword in content_lower)
        
        if decision_count > 0:
            findings.append(f"Identified {decision_count} decision-related terms")
            confidence += 0.1
        
        # Recommendation indicators
        if "recommend" in content_lower or "suggest" in content_lower:
            findings.append("Recommendations present in document")
            confidence += 0.1
        
        # Action items
        if "action" in content_lower or "step" in content_lower:
            findings.append("Action items identified")
            confidence += 0.1
        
        # Priority indicators
        priority_keywords = ["high priority", "urgent", "critical", "important"]
        priority_count = sum(1 for keyword in priority_keywords if keyword in content_lower)
        
        if priority_count > 0:
            findings.append(f"Identified {priority_count} priority items")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Decision Points",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"decision_indicators": decision_count, "priority_items": priority_count}
        )

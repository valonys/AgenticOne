"""
Methods Specialist Agent - Specialized in engineering methods and procedures
"""
from typing import Dict, List, Any
from app.agents.base_agent import BaseAgent
from app.models.schemas import AnalysisResult

class MethodsSpecialist(BaseAgent):
    """Methods Specialist Agent for engineering methods and procedures"""
    
    def __init__(self, rag_service, vision_service):
        super().__init__(rag_service, vision_service)
        self.capabilities = [
            "method_analysis",
            "procedure_optimization",
            "best_practices",
            "workflow_analysis",
            "process_improvement"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities
    
    async def analyze(self, document_id: str, analysis_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform methods analysis"""
        try:
            await self.update_status("analyzing")
            
            # Preprocess document
            preprocessed = await self.preprocess_document(document_id)
            context = preprocessed["context"]
            relevant_docs = preprocessed["relevant_documents"]
            image_analysis = preprocessed["image_analysis"]
            
            # Perform methods analysis
            results = []
            
            # Method identification
            method_analysis = await self._analyze_methods(context, relevant_docs)
            results.append(method_analysis)
            
            # Procedure analysis
            procedure_analysis = await self._analyze_procedures(context, relevant_docs)
            results.append(procedure_analysis)
            
            # Best practices review
            best_practices_analysis = await self._analyze_best_practices(context, relevant_docs)
            results.append(best_practices_analysis)
            
            # Workflow optimization
            workflow_analysis = await self._analyze_workflow(context, relevant_docs)
            results.append(workflow_analysis)
            
            # Postprocess results
            processed_results = await self.postprocess_results(results)
            
            # Save analysis
            analysis_id = await self.save_analysis({
                "document_id": document_id,
                "agent_type": "methods_specialist",
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
    
    async def _analyze_methods(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze engineering methods and techniques"""
        findings = []
        confidence = 0.8
        
        content_lower = context["content"].lower()
        
        # Method identification
        method_keywords = ["method", "technique", "approach", "procedure", "process", "workflow"]
        method_count = sum(1 for keyword in method_keywords if keyword in content_lower)
        
        if method_count > 0:
            findings.append(f"Identified {method_count} method-related terms")
            confidence += 0.1
        
        # Specific engineering methods
        engineering_methods = ["finite element", "computational", "simulation", "modeling", "analysis"]
        found_methods = [method for method in engineering_methods if method in content_lower]
        
        if found_methods:
            findings.append(f"Engineering methods identified: {', '.join(found_methods)}")
            confidence += 0.15
        
        # Mathematical/analytical methods
        if "calculation" in content_lower or "formula" in content_lower:
            findings.append("Mathematical calculations present")
            confidence += 0.1
        
        # Testing methods
        if "test" in content_lower or "testing" in content_lower:
            findings.append("Testing methods identified")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Method Analysis",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"method_indicators": method_count, "engineering_methods": found_methods}
        )
    
    async def _analyze_procedures(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze procedures and workflows"""
        findings = []
        confidence = 0.75
        
        content_lower = context["content"].lower()
        
        # Procedure indicators
        procedure_keywords = ["procedure", "process", "workflow", "step", "sequence", "protocol"]
        procedure_count = sum(1 for keyword in procedure_keywords if keyword in content_lower)
        
        if procedure_count > 0:
            findings.append(f"Identified {procedure_count} procedure-related terms")
            confidence += 0.1
        
        # Step-by-step processes
        if "step" in content_lower and ("1" in content_lower or "first" in content_lower):
            findings.append("Step-by-step procedure identified")
            confidence += 0.15
        
        # Quality control procedures
        if "quality" in content_lower and "control" in content_lower:
            findings.append("Quality control procedures present")
            confidence += 0.1
        
        # Safety procedures
        if "safety" in content_lower and "procedure" in content_lower:
            findings.append("Safety procedures identified")
            confidence += 0.1
        
        # Documentation requirements
        if "document" in content_lower and ("record" in content_lower or "log" in content_lower):
            findings.append("Documentation requirements identified")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Procedure Analysis",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"procedure_indicators": procedure_count}
        )
    
    async def _analyze_best_practices(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze best practices and standards"""
        findings = []
        confidence = 0.8
        
        content_lower = context["content"].lower()
        
        # Best practice indicators
        best_practice_keywords = ["best practice", "standard", "guideline", "recommendation", "optimal"]
        best_practice_count = sum(1 for keyword in best_practice_keywords if keyword in content_lower)
        
        if best_practice_count > 0:
            findings.append(f"Identified {best_practice_count} best practice indicators")
            confidence += 0.1
        
        # Industry standards
        standards = ["api", "asme", "astm", "iso", "ansi", "nace", "aws"]
        found_standards = [std for std in standards if std in content_lower]
        
        if found_standards:
            findings.append(f"Industry standards referenced: {', '.join(found_standards)}")
            confidence += 0.15
        
        # Optimization indicators
        if "optimize" in content_lower or "efficient" in content_lower:
            findings.append("Optimization considerations present")
            confidence += 0.1
        
        # Lessons learned
        if "lesson" in content_lower and "learned" in content_lower:
            findings.append("Lessons learned documented")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Best Practices",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"best_practice_indicators": best_practice_count, "standards": found_standards}
        )
    
    async def _analyze_workflow(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze workflow and process optimization"""
        findings = []
        confidence = 0.7
        
        content_lower = context["content"].lower()
        
        # Workflow indicators
        workflow_keywords = ["workflow", "process", "sequence", "order", "timeline", "schedule"]
        workflow_count = sum(1 for keyword in workflow_keywords if keyword in content_lower)
        
        if workflow_count > 0:
            findings.append(f"Identified {workflow_count} workflow-related terms")
            confidence += 0.1
        
        # Dependencies
        if "dependency" in content_lower or "dependent" in content_lower:
            findings.append("Dependencies identified")
            confidence += 0.1
        
        # Parallel processes
        if "parallel" in content_lower or "simultaneous" in content_lower:
            findings.append("Parallel processes identified")
            confidence += 0.1
        
        # Bottlenecks
        if "bottleneck" in content_lower or "constraint" in content_lower:
            findings.append("Potential bottlenecks identified")
            confidence += 0.1
        
        # Efficiency indicators
        if "efficient" in content_lower or "optimize" in content_lower:
            findings.append("Efficiency considerations present")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Workflow Analysis",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"workflow_indicators": workflow_count}
        )

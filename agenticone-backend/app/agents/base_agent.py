"""
Base agent class for all specialized agents
"""
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.models.schemas import AnalysisResult, AnalysisType
from app.services.rag_service import RAGService
from app.services.vision_service import VisionService
from app.models.database import db_client

class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, rag_service: RAGService, vision_service: VisionService):
        self.rag_service = rag_service
        self.vision_service = vision_service
        self.agent_id = self.__class__.__name__.lower()
        self.capabilities = []
        self.status = "initialized"
    
    @abstractmethod
    async def analyze(self, document_id: str, analysis_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analysis on a document"""
        pass
    
    async def chat(self, message: str) -> Dict[str, Any]:
        """Handle chat interactions with the agent"""
        try:
            # Use the vision service to generate a response
            if self.vision_service:
                response = await self.vision_service.generate_text_response(
                    message, 
                    agent_type=self.agent_id
                )
                return {
                    "response": response,
                    "agent_type": self.agent_id,
                    "status": "success"
                }
            else:
                # Fallback response if vision service is not available
                return {
                    "response": f"I'm the {self.agent_id} agent. I received your message: '{message}'. However, I'm currently not fully configured to respond.",
                    "agent_type": self.agent_id,
                    "status": "limited"
                }
        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "agent_type": self.agent_id,
                "status": "error"
            }
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        pass
    
    async def get_document_context(self, document_id: str) -> Dict[str, Any]:
        """Get document context and metadata"""
        try:
            # Get document from database
            document = await db_client.get_document(document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            # Get document content from RAG service
            content = await self.rag_service.get_document_content(document_id)
            
            return {
                "document_id": document_id,
                "filename": document.filename,
                "document_type": document.document_type,
                "metadata": document.metadata,
                "content": content
            }
        except Exception as e:
            raise ValueError(f"Failed to get document context: {str(e)}")
    
    async def search_relevant_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents using RAG service"""
        try:
            results = await self.rag_service.search_documents(query, limit)
            return results
        except Exception as e:
            raise ValueError(f"Failed to search documents: {str(e)}")
    
    async def analyze_images(self, document_id: str) -> List[Dict[str, Any]]:
        """Analyze images in document using vision service"""
        try:
            # Get document content
            context = await self.get_document_context(document_id)
            
            # Extract and analyze images
            image_analysis = await self.vision_service.analyze_document_images(
                context["content"],
                context["document_type"]
            )
            
            return image_analysis
        except Exception as e:
            raise ValueError(f"Failed to analyze images: {str(e)}")
    
    def create_analysis_result(
        self,
        category: str,
        findings: List[str],
        confidence: float,
        details: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """Create a standardized analysis result"""
        return AnalysisResult(
            category=category,
            findings=findings,
            confidence=confidence,
            details=details or {}
        )
    
    async def save_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Save analysis results to database"""
        try:
            analysis_id = await db_client.create_analysis(analysis_data)
            return analysis_id
        except Exception as e:
            raise ValueError(f"Failed to save analysis: {str(e)}")
    
    async def get_previous_analyses(self, document_id: str) -> List[Dict[str, Any]]:
        """Get previous analyses for the same document"""
        try:
            analyses = await db_client.get_analyses_by_document(document_id)
            return [analysis.dict() for analysis in analyses]
        except Exception as e:
            raise ValueError(f"Failed to get previous analyses: {str(e)}")
    
    def generate_recommendations(self, results: List[AnalysisResult]) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        for result in results:
            if result.confidence < 0.7:
                recommendations.append(f"Review {result.category} analysis - low confidence score")
            
            if "critical" in result.category.lower() or "urgent" in result.category.lower():
                recommendations.append(f"Immediate attention required for {result.category}")
            
            if result.confidence > 0.9:
                recommendations.append(f"High confidence in {result.category} findings")
        
        return recommendations
    
    async def update_status(self, status: str, details: Optional[Dict[str, Any]] = None):
        """Update agent status in database"""
        try:
            status_data = {
                "agent_id": self.agent_id,
                "status": status,
                "updated_at": datetime.utcnow(),
                "details": details or {}
            }
            await db_client.update_agent_status(self.agent_id, status_data)
        except Exception as e:
            # Log error but don't fail the analysis
            print(f"Failed to update agent status: {str(e)}")
    
    def validate_parameters(self, parameters: Dict[str, Any], required_params: List[str]) -> bool:
        """Validate required parameters"""
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")
        return True
    
    async def preprocess_document(self, document_id: str) -> Dict[str, Any]:
        """Preprocess document for analysis"""
        try:
            await self.update_status("preprocessing")
            
            # Get document context
            context = await self.get_document_context(document_id)
            
            # Search for relevant documents
            relevant_docs = await self.search_relevant_documents(
                f"document type: {context['document_type']}"
            )
            
            # Analyze images if present
            image_analysis = []
            if context["document_type"] in ["pdf", "image"]:
                image_analysis = await self.analyze_images(document_id)
            
            return {
                "context": context,
                "relevant_documents": relevant_docs,
                "image_analysis": image_analysis
            }
        except Exception as e:
            await self.update_status("error", {"error": str(e)})
            raise
    
    async def postprocess_results(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Postprocess analysis results"""
        try:
            await self.update_status("postprocessing")
            
            # Generate recommendations
            recommendations = self.generate_recommendations(results)
            
            # Calculate overall confidence
            overall_confidence = sum(result.confidence for result in results) / len(results) if results else 0.0
            
            return {
                "results": results,
                "recommendations": recommendations,
                "confidence": overall_confidence
            }
        except Exception as e:
            await self.update_status("error", {"error": str(e)})
            raise

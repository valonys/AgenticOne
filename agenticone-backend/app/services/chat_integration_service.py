"""
Chat Integration Service for AgenticOne
Captures and processes chat conversations from agents for report generation
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.services.vertex_ai_service import VertexAIService
from app.services.report_generator import ReportGenerator
from app.services.pdf_report_generator import PDFReportGenerator


class ChatIntegrationService:
    """Service to integrate chat conversations with report generation"""
    
    def __init__(self):
        self.vertex_ai_service = VertexAIService()
        self.report_generator = ReportGenerator()
        self.pdf_report_generator = PDFReportGenerator()
        self.conversations_dir = Path("conversations")
        self.conversations_dir.mkdir(exist_ok=True)
    
    async def capture_chat_conversation(
        self,
        specialist_type: str,
        user_message: str,
        agent_response: str,
        user_email: str,
        user_name: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Capture a chat conversation for later report generation"""
        
        if not conversation_id:
            conversation_id = f"{specialist_type}_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract user name from email if not provided
        if not user_name:
            user_name = user_email.split('@')[0].replace('.', ' ').title()
        
        conversation_data = {
            "conversation_id": conversation_id,
            "specialist_type": specialist_type,
            "user_message": user_message,
            "agent_response": agent_response,
            "user_email": user_email,
            "user_name": user_name,
            "timestamp": datetime.now().isoformat(),
            "processed": False
        }
        
        # Save conversation
        conversation_file = self.conversations_dir / f"{conversation_id}.json"
        with open(conversation_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2)
        
        print(f"💬 Chat conversation captured: {conversation_id}")
        return conversation_data
    
    async def generate_report_from_conversation(
        self,
        conversation_id: str,
        customer_request: str,
        report_format: str = "both"  # "html", "pdf", or "both"
    ) -> Dict[str, Any]:
        """Generate report from captured chat conversation"""
        
        # Load conversation
        conversation_file = self.conversations_dir / f"{conversation_id}.json"
        if not conversation_file.exists():
            raise ValueError(f"Conversation {conversation_id} not found")
        
        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
        
        # Extract conversation data
        specialist_type = conversation["specialist_type"]
        user_message = conversation["user_message"]
        agent_response = conversation["agent_response"]
        user_email = conversation["user_email"]
        
        # Create analysis data from conversation
        analysis_data = await self._extract_analysis_from_conversation(
            specialist_type, user_message, agent_response
        )
        
        results = {}
        
        # Generate HTML report if requested
        if report_format in ["html", "both"]:
            try:
                html_report = await self.report_generator.generate_specialist_report(
                    specialist_type=specialist_type,
                    analysis_data=analysis_data,
                    customer_request=customer_request,
                    user_email=user_email
                )
                results["html_report"] = html_report
                print(f"✅ HTML report generated from conversation: {conversation_id}")
            except Exception as e:
                print(f"❌ HTML report generation failed: {e}")
                results["html_error"] = str(e)
        
        # Generate PDF report if requested
        if report_format in ["pdf", "both"]:
            try:
                pdf_report = await self.pdf_report_generator.generate_specialist_pdf_report(
                    specialist_type=specialist_type,
                    analysis_data=analysis_data,
                    customer_request=customer_request,
                    user_email=user_email,
                    user_name=conversation.get("user_name", user_email.split('@')[0].replace('.', ' ').title())
                )
                results["pdf_report"] = pdf_report
                print(f"✅ PDF report generated from conversation: {conversation_id}")
            except Exception as e:
                print(f"❌ PDF report generation failed: {e}")
                results["pdf_error"] = str(e)
        
        # Mark conversation as processed
        conversation["processed"] = True
        conversation["processed_at"] = datetime.now().isoformat()
        with open(conversation_file, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=2)
        
        return {
            "conversation_id": conversation_id,
            "specialist_type": specialist_type,
            "customer_request": customer_request,
            "results": results,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _extract_analysis_from_conversation(
        self,
        specialist_type: str,
        user_message: str,
        agent_response: str
    ) -> Dict[str, Any]:
        """Extract structured analysis data from chat conversation"""
        
        # Use AI to analyze the conversation and extract structured data
        analysis_prompt = f"""
        Analyze this conversation between a user and a {specialist_type} specialist:
        
        User Message: {user_message}
        Agent Response: {agent_response}
        
        Extract the following information and format as JSON:
        1. Key findings from the agent's response
        2. Technical recommendations provided
        3. Risk assessment mentioned
        4. Next steps or actions suggested
        5. Technical details discussed
        
        Format as JSON with keys: findings, recommendations, risk_level, risk_reasoning, technical_details, next_steps
        """
        
        try:
            # Use Vertex AI to analyze the conversation
            ai_analysis = await self.vertex_ai_service.generate_text(analysis_prompt)
            
            # Try to parse JSON response
            try:
                analysis_data = json.loads(ai_analysis)
                print(f"🤖 AI analysis extracted from conversation")
                return analysis_data
            except json.JSONDecodeError:
                # Fallback to manual extraction
                return await self._manual_extraction_from_conversation(
                    specialist_type, user_message, agent_response
                )
                
        except Exception as e:
            print(f"⚠️ AI analysis failed, using manual extraction: {e}")
            return await self._manual_extraction_from_conversation(
                specialist_type, user_message, agent_response
            )
    
    async def _manual_extraction_from_conversation(
        self,
        specialist_type: str,
        user_message: str,
        agent_response: str
    ) -> Dict[str, Any]:
        """Manually extract analysis data from conversation when AI fails"""
        
        # Extract key information from the agent response
        findings = []
        recommendations = []
        technical_details = agent_response
        
        # Look for common patterns in agent responses
        if "recommend" in agent_response.lower():
            recommendations.append("Follow agent recommendations")
        if "risk" in agent_response.lower():
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Extract findings based on response content
        if "analysis" in agent_response.lower():
            findings.append("Analysis completed by specialist")
        if "assessment" in agent_response.lower():
            findings.append("Assessment performed")
        if "evaluation" in agent_response.lower():
            findings.append("Evaluation conducted")
        
        return {
            "findings": findings if findings else ["Specialist consultation completed"],
            "recommendations": recommendations if recommendations else ["Follow specialist guidance"],
            "risk_level": risk_level,
            "risk_reasoning": "Based on specialist assessment",
            "technical_details": technical_details,
            "next_steps": ["Review specialist recommendations", "Implement suggested actions"]
        }
    
    async def list_conversations(self) -> List[Dict[str, Any]]:
        """List all captured conversations"""
        conversations = []
        
        for conversation_file in self.conversations_dir.glob("*.json"):
            try:
                with open(conversation_file, 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
                conversations.append(conversation)
            except Exception as e:
                print(f"Error loading conversation {conversation_file}: {e}")
        
        return sorted(conversations, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get a specific conversation by ID"""
        conversation_file = self.conversations_dir / f"{conversation_id}.json"
        
        if not conversation_file.exists():
            raise ValueError(f"Conversation {conversation_id} not found")
        
        with open(conversation_file, 'r', encoding='utf-8') as f:
            return json.load(f)

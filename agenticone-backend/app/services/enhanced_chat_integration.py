"""
Enhanced Chat Integration Service with Automatic Report Detection
Detects when users request reports and automatically generates them in multiple formats
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from app.services.multi_format_report_generator import MultiFormatReportGenerator
from app.services.vertex_ai_service import VertexAIService


class EnhancedChatIntegrationService:
    """Enhanced chat service with automatic report generation capabilities"""
    
    def __init__(self):
        self.report_generator = MultiFormatReportGenerator()
        self.vertex_ai_service = VertexAIService()
        self.conversations_dir = Path("conversations")
        self.conversations_dir.mkdir(exist_ok=True)
        
        # Report request patterns
        self.report_triggers = [
            r'\b(generate|create|produce|make|give me|provide)\s+(a\s+)?(report|summary|analysis|assessment|findings|document)\b',
            r'\breport\s+(on|about|regarding|for)\b',
            r'\b(can|could|would)\s+you\s+(generate|create|produce|make|give|provide)\b',
            r'\b(insights|findings|results)\s+(report|summary|document)\b',
            r'\b(download|export|save)\s+(as|to|in)\s+(pdf|html|markdown|md)\b',
            r'\bwant\s+(the|a)\s+(report|analysis|summary)\b',
            r'\bneed\s+(the|a)\s+(report|analysis|summary|findings)\b',
            r'\bshow\s+me\s+(the|a)\s+(report|results|analysis)\b',
            r'\b(inspection|assessment)\s+(report|findings|results)\b',
        ]
        
        self.compiled_triggers = [re.compile(pattern, re.IGNORECASE) for pattern in self.report_triggers]
    
    async def process_chat_message(
        self,
        specialist_type: str,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        user_email: str,
        user_name: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process chat message and automatically detect report requests
        
        Returns:
            Dictionary containing:
            - agent_response: The chat response
            - report_generated: Boolean indicating if report was generated
            - report_data: Report information if generated
        """
        
        # Check if message is a report request
        is_report_request, report_context = await self._detect_report_request(user_message)
        
        # Get agent response
        agent_response = await self._get_agent_response(
            specialist_type=specialist_type,
            user_message=user_message,
            conversation_history=conversation_history,
            is_report_request=is_report_request
        )
        
        # Update conversation history
        conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        conversation_history.append({
            "role": "assistant",
            "content": agent_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save conversation
        if not conversation_id:
            conversation_id = f"{specialist_type}_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        await self._save_conversation(
            conversation_id=conversation_id,
            specialist_type=specialist_type,
            messages=conversation_history,
            user_email=user_email,
            user_name=user_name
        )
        
        result = {
            "conversation_id": conversation_id,
            "agent_response": agent_response,
            "report_generated": False,
            "report_data": None
        }
        
        # Generate report if requested
        if is_report_request:
            print(f"🎯 Report request detected in chat with {specialist_type}")
            
            try:
                # Extract analysis from conversation
                analysis_data = await self._extract_analysis_from_history(
                    specialist_type=specialist_type,
                    conversation_history=conversation_history
                )
                
                # Determine report formats
                formats = self._determine_report_formats(user_message)
                
                # Generate multi-format report using the proper MultiFormatReportGenerator
                report_manifest = await self.report_generator.generate_chat_report(
                    specialist_type=specialist_type,
                    conversation_data={
                        "conversation_id": conversation_id,
                        "messages": conversation_history
                    },
                    analysis_data=analysis_data,
                    customer_request=report_context or user_message,
                    user_email=user_email,
                    user_name=user_name,
                    formats=formats
                )
                
                result["report_generated"] = True
                result["report_data"] = report_manifest
                
                # Add report generation message to response
                report_message = self._create_report_message(report_manifest)
                result["agent_response"] += f"\n\n{report_message}"
                
                print(f"✅ Report generated successfully: {report_manifest['report_id']}")
                
            except Exception as e:
                print(f"❌ Report generation failed: {e}")
                result["agent_response"] += f"\n\nI encountered an issue generating the report: {str(e)}. Please try again or contact support."
        
        return result
    
    async def _detect_report_request(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if message is requesting a report
        
        Returns:
            Tuple of (is_request, context)
        """
        
        # Check against compiled patterns
        for pattern in self.compiled_triggers:
            match = pattern.search(message)
            if match:
                # Extract context (what the report should be about)
                context = self._extract_report_context(message, match)
                return True, context
        
        return False, None
    
    def _extract_report_context(self, message: str, match: re.Match) -> str:
        """Extract what the report should be about from the message"""
        
        # Try to find context words near the match
        context_words = []
        
        # Look for key phrases
        context_patterns = [
            r'(about|on|regarding|for)\s+([^.,!?]+)',
            r'(inspection|assessment|analysis|review)\s+(of|for|about)\s+([^.,!?]+)',
        ]
        
        for pattern in context_patterns:
            ctx_match = re.search(pattern, message, re.IGNORECASE)
            if ctx_match:
                context_words.append(ctx_match.group(0))
        
        if context_words:
            return ' '.join(context_words)
        
        # Fallback: return the matched sentence
        sentences = message.split('.')
        for sentence in sentences:
            if match.group(0).lower() in sentence.lower():
                return sentence.strip()
        
        return message
    
    def _determine_report_formats(self, message: str) -> List[str]:
        """Determine which formats to generate based on user request"""
        
        message_lower = message.lower()
        formats = []
        
        # Check for specific format requests
        if any(word in message_lower for word in ['pdf', '.pdf']):
            formats.append('pdf')
        if any(word in message_lower for word in ['html', '.html', 'web']):
            formats.append('html')
        if any(word in message_lower for word in ['markdown', '.md', 'md', 'text']):
            formats.append('markdown')
        
        # If no specific format mentioned, generate all formats
        if not formats:
            formats = ['html', 'pdf']
        
        return formats
    
    async def _get_agent_response(
        self,
        specialist_type: str,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        is_report_request: bool
    ) -> str:
        """Get response from specialist agent"""
        
        try:
            # Create context from conversation history
            context = self._build_conversation_context(conversation_history)
            
            # Create specialist-specific prompt
            system_prompt = self._get_specialist_prompt(specialist_type, is_report_request)
            
            # Generate response using Vertex AI
            full_prompt = f"{context}\n\nUser: {user_message}\n\nAssistant:"
            
            response = await self.vertex_ai_service.generate_text(
                prompt=full_prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            print(f"Error generating agent response: {e}")
            return self._get_fallback_response(specialist_type, user_message, is_report_request)
    
    def _build_conversation_context(self, history: List[Dict[str, Any]], max_messages: int = 5) -> str:
        """Build conversation context from history"""
        
        # Get last N messages
        recent_messages = history[-max_messages:] if len(history) > max_messages else history
        
        context_parts = []
        for msg in recent_messages:
            role = msg.get('role', 'user').title()
            content = msg.get('content', '')
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def _get_specialist_prompt(self, specialist_type: str, is_report_request: bool) -> str:
        """Get specialist-specific system prompt"""
        
        base_prompts = {
            "corrosion_engineer": "You are an expert Corrosion Engineer specializing in material degradation analysis, corrosion prevention, and protective coating systems. Provide technical, accurate, and actionable advice.",
            "subsea_engineer": "You are an expert Subsea Engineer specializing in underwater operations, marine systems, and subsea infrastructure. Provide technical guidance on subsea equipment and operations.",
            "methods_specialist": "You are a Methods Specialist expert in operational procedures, engineering methods, and process optimization. Provide guidance on best practices and methodology.",
            "discipline_head": "You are a Discipline Head responsible for project oversight, coordination, and strategic decision-making. Provide high-level guidance and recommendations."
        }
        
        prompt = base_prompts.get(specialist_type, base_prompts["methods_specialist"])
        
        if is_report_request:
            prompt += "\n\nThe user has requested a report. Acknowledge this request and explain what will be included in the report based on your analysis of the conversation."
        
        return prompt
    
    def _get_fallback_response(self, specialist_type: str, user_message: str, is_report_request: bool) -> str:
        """Generate fallback response when AI service fails"""
        
        specialist_title = specialist_type.replace('_', ' ').title()
        
        if is_report_request:
            return f"As a {specialist_title}, I've analyzed our conversation and I'm now generating a comprehensive report for you. The report will include my findings, technical analysis, risk assessment, and recommendations based on our discussion."
        
        return f"As a {specialist_title}, I'm here to help with your inquiry. Could you provide more details so I can give you the most accurate and helpful information?"
    
    async def _extract_analysis_from_history(
        self,
        specialist_type: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract structured analysis from conversation history"""
        
        # Combine all assistant messages (specialist responses)
        specialist_responses = [
            msg['content'] for msg in conversation_history 
            if msg.get('role') == 'assistant'
        ]
        
        combined_analysis = '\n\n'.join(specialist_responses)
        
        # Try to use AI to structure the analysis
        try:
            structure_prompt = f"""
            Analyze the following conversation with a {specialist_type.replace('_', ' ')} and extract structured information.
            
            Conversation:
            {combined_analysis}
            
            Extract and format as JSON with these keys:
            - summary: Brief overview of the consultation
            - findings: List of key findings (array)
            - recommendations: List of recommendations (array)
            - risk_level: Risk assessment (Low/Medium/High)
            - risk_reasoning: Explanation of risk level
            - technical_details: Detailed technical information
            - next_steps: List of next actions (array)
            
            Return ONLY valid JSON.
            """
            
            ai_response = await self.vertex_ai_service.generate_text(
                prompt=structure_prompt,
                max_tokens=1500,
                temperature=0.3
            )
            
            # Try to parse JSON
            analysis = json.loads(ai_response)
            return analysis
            
        except Exception as e:
            print(f"AI analysis extraction failed: {e}, using fallback")
            
            # Fallback: create structured analysis manually
            return await self._create_fallback_analysis(
                specialist_type=specialist_type,
                responses=specialist_responses
            )
    
    async def _create_fallback_analysis(
        self,
        specialist_type: str,
        responses: List[str]
    ) -> Dict[str, Any]:
        """Create fallback analysis structure"""
        
        combined_text = ' '.join(responses)
        
        # Extract sentences that look like findings
        findings = []
        for response in responses:
            sentences = response.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in ['found', 'identified', 'observed', 'detected', 'noted']):
                    findings.append(sentence.strip())
        
        # Extract sentences that look like recommendations
        recommendations = []
        for response in responses:
            sentences = response.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in ['recommend', 'suggest', 'should', 'advise', 'propose']):
                    recommendations.append(sentence.strip())
        
        # Determine risk level based on keywords
        risk_keywords_high = ['critical', 'severe', 'immediate', 'urgent', 'danger']
        risk_keywords_medium = ['concern', 'moderate', 'attention', 'monitor']
        
        if any(keyword in combined_text.lower() for keyword in risk_keywords_high):
            risk_level = "High"
        elif any(keyword in combined_text.lower() for keyword in risk_keywords_medium):
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            "summary": f"Comprehensive {specialist_type.replace('_', ' ')} consultation completed based on customer inquiry.",
            "findings": findings[:5] if findings else [
                "Technical assessment performed",
                "Analysis completed",
                "Conditions evaluated"
            ],
            "recommendations": recommendations[:5] if recommendations else [
                "Follow specialist guidance",
                "Implement suggested measures",
                "Schedule follow-up as needed"
            ],
            "risk_level": risk_level,
            "risk_reasoning": "Based on specialist assessment and identified conditions",
            "technical_details": combined_text[:500] if combined_text else "Detailed technical consultation provided.",
            "next_steps": [
                "Review specialist recommendations",
                "Implement action items",
                "Schedule follow-up consultation if needed"
            ]
        }
    
    
    def _create_report_message(self, report_manifest: Dict[str, Any]) -> str:
        """Create message informing user about generated report"""
        
        files = report_manifest.get('files', {})
        download_links = report_manifest.get('download_links', {})
        
        message = "📊 **Report Generated Successfully!**\n\n"
        message += "I've created a comprehensive report based on our conversation. Your report is available in multiple formats:\n\n"
        
        format_icons = {
            'html': '🌐',
            'pdf': '📕'
        }
        
        for format_type, file_path in files.items():
            icon = format_icons.get(format_type, '📄')
            filename = Path(file_path).name
            link = download_links.get(format_type, file_path)
            message += f"{icon} **{format_type.upper()}**: [{filename}]({link})\n"
        
        message += "\n**What's included in your report:**\n"
        message += "• Executive summary of our consultation\n"
        message += "• Detailed findings and analysis\n"
        message += "• Risk assessment\n"
        message += "• Recommendations and action items\n"
        message += "• Next steps and follow-up plan\n"
        message += "• Complete conversation transcript\n\n"
        
        message += "💾 You can download the report in your preferred format using the links above."
        
        return message
    
    async def _save_conversation(
        self,
        conversation_id: str,
        specialist_type: str,
        messages: List[Dict[str, Any]],
        user_email: str,
        user_name: Optional[str] = None
    ) -> None:
        """Save conversation to disk"""
        
        conversation_data = {
            "conversation_id": conversation_id,
            "specialist_type": specialist_type,
            "user_email": user_email,
            "user_name": user_name,
            "messages": messages,
            "last_updated": datetime.now().isoformat(),
            "message_count": len(messages)
        }
        
        conversation_file = self.conversations_dir / f"{conversation_id}.json"
        with open(conversation_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2)
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation from disk"""
        
        conversation_file = self.conversations_dir / f"{conversation_id}.json"
        
        if not conversation_file.exists():
            return None
        
        with open(conversation_file, 'r', encoding='utf-8') as f:
            return json.load(f)

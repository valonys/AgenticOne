"""
Chat Integration API Endpoints
Handles chat conversation capture and report generation from conversations
"""

from fastapi import APIRouter, Depends, HTTPException, Form
from typing import List, Dict, Any, Optional
import json

from app.services.chat_integration_service import ChatIntegrationService

router = APIRouter(prefix="/api/chat", tags=["Chat Integration"])

def get_chat_integration_service() -> ChatIntegrationService:
    return ChatIntegrationService()

@router.post("/capture")
async def capture_chat_conversation(
    specialist_type: str = Form(...),
    user_message: str = Form(...),
    agent_response: str = Form(...),
    user_email: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    chat_service: ChatIntegrationService = Depends(get_chat_integration_service)
):
    """Capture a chat conversation for later report generation"""
    try:
        conversation = await chat_service.capture_chat_conversation(
            specialist_type=specialist_type,
            user_message=user_message,
            agent_response=agent_response,
            user_email=user_email,
            conversation_id=conversation_id
        )
        
        return {
            "status": "success",
            "message": "Chat conversation captured successfully",
            "conversation": conversation
        }
        
    except Exception as e:
        print(f"❌ Chat capture error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to capture conversation: {str(e)}")

@router.post("/generate-report")
async def generate_report_from_conversation(
    conversation_id: str = Form(...),
    customer_request: str = Form(...),
    report_format: str = Form("both"),
    chat_service: ChatIntegrationService = Depends(get_chat_integration_service)
):
    """Generate report from captured chat conversation"""
    try:
        result = await chat_service.generate_report_from_conversation(
            conversation_id=conversation_id,
            customer_request=customer_request,
            report_format=report_format
        )
        
        return {
            "status": "success",
            "message": f"Report generated from conversation {conversation_id}",
            "result": result
        }
        
    except Exception as e:
        print(f"❌ Report generation from conversation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/conversations")
async def list_conversations(
    chat_service: ChatIntegrationService = Depends(get_chat_integration_service)
):
    """List all captured conversations"""
    try:
        conversations = await chat_service.list_conversations()
        
        return {
            "status": "success",
            "conversations": conversations,
            "count": len(conversations)
        }
        
    except Exception as e:
        print(f"❌ List conversations error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    chat_service: ChatIntegrationService = Depends(get_chat_integration_service)
):
    """Get a specific conversation by ID"""
    try:
        conversation = await chat_service.get_conversation(conversation_id)
        
        return {
            "status": "success",
            "conversation": conversation
        }
        
    except Exception as e:
        print(f"❌ Get conversation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")

@router.post("/chat-with-agent")
async def chat_with_agent_and_capture(
    specialist_type: str = Form(...),
    user_message: str = Form(...),
    user_email: str = Form(...),
    chat_service: ChatIntegrationService = Depends(get_chat_integration_service)
):
    """Chat with an agent and automatically capture the conversation"""
    try:
        # This would integrate with the existing agent chat functionality
        # For now, we'll simulate an agent response
        agent_response = f"Thank you for your message: '{user_message}'. As a {specialist_type}, I'll analyze your request and provide detailed recommendations. Based on your inquiry, I recommend scheduling a comprehensive assessment to evaluate the current conditions and develop an appropriate action plan."
        
        # Capture the conversation
        conversation = await chat_service.capture_chat_conversation(
            specialist_type=specialist_type,
            user_message=user_message,
            agent_response=agent_response,
            user_email=user_email
        )
        
        return {
            "status": "success",
            "message": "Chat completed and conversation captured",
            "agent_response": agent_response,
            "conversation": conversation
        }
        
    except Exception as e:
        print(f"❌ Chat with agent error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to chat with agent: {str(e)}")

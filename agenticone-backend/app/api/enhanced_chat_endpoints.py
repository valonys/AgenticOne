"""
Enhanced Chat Integration API Endpoints
Handles automatic report detection and generation during chat conversations
"""

from fastapi import APIRouter, Depends, HTTPException, Form
from typing import List, Dict, Any, Optional
import json

from app.services.enhanced_chat_integration import EnhancedChatIntegrationService

router = APIRouter(prefix="/api/chat", tags=["Enhanced Chat Integration"])

def get_enhanced_chat_service() -> EnhancedChatIntegrationService:
    return EnhancedChatIntegrationService()

@router.post("/enhanced-chat")
async def enhanced_chat_with_agent(
    specialist_type: str = Form(...),
    user_message: str = Form(...),
    user_email: str = Form(...),
    user_name: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    chat_service: EnhancedChatIntegrationService = Depends(get_enhanced_chat_service)
):
    """Enhanced chat with automatic report detection and generation"""
    try:
        # Load existing conversation if continuing
        conversation_history = []
        if conversation_id:
            existing_conv = await chat_service.get_conversation(conversation_id)
            if existing_conv:
                conversation_history = existing_conv['messages']
        
        # Process message (automatically detects and generates reports)
        result = await chat_service.process_chat_message(
            specialist_type=specialist_type,
            user_message=user_message,
            conversation_history=conversation_history,
            user_email=user_email,
            user_name=user_name,
            conversation_id=conversation_id
        )
        
        return {
            "conversation_id": result["conversation_id"],
            "response": result["agent_response"],
            "report_generated": result["report_generated"],
            "report_downloads": result.get("report_data", {}).get("download_links") if result["report_generated"] else None,
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        print(f"❌ Enhanced chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")

@router.post("/capture-enhanced")
async def capture_enhanced_conversation(
    specialist_type: str = Form(...),
    user_message: str = Form(...),
    agent_response: str = Form(...),
    user_email: str = Form(...),
    user_name: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    chat_service: EnhancedChatIntegrationService = Depends(get_enhanced_chat_service)
):
    """Capture a chat conversation with enhanced features"""
    try:
        conversation = await chat_service.capture_chat_conversation(
            specialist_type=specialist_type,
            user_message=user_message,
            agent_response=agent_response,
            user_email=user_email,
            user_name=user_name,
            conversation_id=conversation_id
        )
        
        return {
            "status": "success",
            "message": "Enhanced chat conversation captured successfully",
            "conversation": conversation
        }
        
    except Exception as e:
        print(f"❌ Enhanced conversation capture error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to capture conversation: {str(e)}")

@router.post("/generate-enhanced-report")
async def generate_enhanced_report_from_conversation(
    conversation_id: str = Form(...),
    customer_request: str = Form(...),
    report_format: str = Form("both"),
    chat_service: EnhancedChatIntegrationService = Depends(get_enhanced_chat_service)
):
    """Generate enhanced report from captured chat conversation"""
    try:
        # Load conversation
        conversation = await chat_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Extract analysis from conversation
        analysis_data = await chat_service._extract_analysis_from_history(
            specialist_type=conversation['specialist_type'],
            conversation_history=conversation['messages']
        )
        
        # Get first user message as request
        customer_request = next(
            (msg['content'] for msg in conversation['messages'] if msg.get('role') == 'user'),
            customer_request
        )
        
        # Generate multi-format report
        report_manifest = await chat_service._generate_multi_format_report(
            specialist_type=conversation['specialist_type'],
            conversation_data=conversation,
            analysis_data=analysis_data,
            customer_request=customer_request,
            user_email=conversation['user_email'],
            user_name=conversation.get('user_name'),
            formats=["html", "pdf"] if report_format == "both" else [report_format]
        )
        
        return {
            "status": "success",
            "message": f"Enhanced report generated from conversation {conversation_id}",
            "report_manifest": report_manifest
        }
        
    except Exception as e:
        print(f"❌ Enhanced report generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate enhanced report: {str(e)}")

@router.get("/conversations-enhanced")
async def list_enhanced_conversations(
    chat_service: EnhancedChatIntegrationService = Depends(get_enhanced_chat_service)
):
    """List all captured enhanced conversations"""
    try:
        conversations = []
        
        # List all conversation files
        for conv_file in chat_service.conversations_dir.glob("*.json"):
            with open(conv_file, 'r', encoding='utf-8') as f:
                conversation = json.load(f)
                conversations.append({
                    "conversation_id": conversation["conversation_id"],
                    "specialist_type": conversation["specialist_type"],
                    "user_email": conversation["user_email"],
                    "user_name": conversation.get("user_name"),
                    "message_count": conversation.get("message_count", 0),
                    "last_updated": conversation.get("last_updated")
                })
        
        return {
            "status": "success",
            "conversations": conversations,
            "count": len(conversations)
        }
        
    except Exception as e:
        print(f"❌ List enhanced conversations error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")

@router.get("/conversations-enhanced/{conversation_id}")
async def get_enhanced_conversation(
    conversation_id: str,
    chat_service: EnhancedChatIntegrationService = Depends(get_enhanced_chat_service)
):
    """Get a specific enhanced conversation by ID"""
    try:
        conversation = await chat_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "status": "success",
            "conversation": conversation
        }
        
    except Exception as e:
        print(f"❌ Get enhanced conversation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")

@router.post("/test-report-detection")
async def test_report_detection(
    message: str = Form(...),
    chat_service: EnhancedChatIntegrationService = Depends(get_enhanced_chat_service)
):
    """Test if a message would trigger report generation"""
    try:
        is_report_request, context = await chat_service._detect_report_request(message)
        
        return {
            "status": "success",
            "message": message,
            "is_report_request": is_report_request,
            "context": context,
            "would_trigger_report": is_report_request
        }
        
    except Exception as e:
        print(f"❌ Report detection test error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test report detection: {str(e)}")

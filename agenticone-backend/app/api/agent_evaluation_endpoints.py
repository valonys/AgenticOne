"""
Agent Evaluation API Endpoints
Provides endpoints for evaluating agent performance and retrieving evaluation data
"""

from fastapi import APIRouter, Depends, HTTPException, Form
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta

from app.services.agent_evaluation_service import AgentEvaluationService, AgentEvaluation, EvaluationScore, EvaluationMetric

router = APIRouter(prefix="/api/evaluation", tags=["Agent Evaluation"])

def get_evaluation_service() -> AgentEvaluationService:
    return AgentEvaluationService()

@router.post("/evaluate-conversation")
async def evaluate_conversation_endpoint(
    agent_role: str = Form(...),
    user_email: str = Form(...),
    conversation_id: str = Form(...),
    conversation_data: str = Form(...),  # JSON string
    user_feedback: Optional[str] = Form(None),  # JSON string
    evaluation_service: AgentEvaluationService = Depends(get_evaluation_service)
):
    """Evaluate a complete conversation"""
    try:
        # Parse conversation data
        try:
            parsed_conversation_data = json.loads(conversation_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid conversation_data JSON format")
        
        # Parse user feedback if provided
        parsed_user_feedback = None
        if user_feedback:
            try:
                parsed_user_feedback = json.loads(user_feedback)
            except json.JSONDecodeError:
                print(f"Warning: Invalid user_feedback JSON format: {user_feedback}")
        
        # Perform evaluation
        evaluation = await evaluation_service.evaluate_conversation(
            agent_role=agent_role,
            user_email=user_email,
            conversation_id=conversation_id,
            conversation_data=parsed_conversation_data,
            user_feedback=parsed_user_feedback
        )
        
        return {
            "status": "success",
            "message": f"Evaluation completed for {agent_role}",
            "evaluation": {
                "agent_role": evaluation.agent_role,
                "user_email": evaluation.user_email,
                "conversation_id": evaluation.conversation_id,
                "overall_score": evaluation.overall_score,
                "individual_scores": [
                    {
                        "metric": score.metric.value,
                        "score": score.score,
                        "weight": score.weight,
                        "feedback": score.feedback
                    }
                    for score in evaluation.individual_scores
                ],
                "strengths": evaluation.strengths,
                "improvements": evaluation.improvements,
                "recommendations": evaluation.recommendations,
                "evaluation_date": evaluation.evaluation_date.isoformat(),
                "evaluator_type": evaluation.evaluator_type
            }
        }
        
    except Exception as e:
        print(f"Error evaluating conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate conversation: {str(e)}")

@router.get("/performance-summary/{agent_role}")
async def get_performance_summary_endpoint(
    agent_role: str,
    user_email: Optional[str] = None,
    days: int = 30,
    evaluation_service: AgentEvaluationService = Depends(get_evaluation_service)
):
    """Get performance summary for an agent"""
    try:
        summary = await evaluation_service.get_agent_performance_summary(
            agent_role=agent_role,
            user_email=user_email,
            days=days
        )
        
        return {
            "status": "success",
            "summary": summary
        }
        
    except Exception as e:
        print(f"Error getting performance summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance summary: {str(e)}")

@router.post("/submit-user-feedback")
async def submit_user_feedback_endpoint(
    conversation_id: str = Form(...),
    agent_role: str = Form(...),
    user_email: str = Form(...),
    satisfaction_score: float = Form(...),  # 0.0 to 1.0
    feedback_text: Optional[str] = Form(None),
    evaluation_service: AgentEvaluationService = Depends(get_evaluation_service)
):
    """Submit user feedback for a conversation"""
    try:
        # Validate satisfaction score
        if not 0.0 <= satisfaction_score <= 1.0:
            raise HTTPException(status_code=400, detail="satisfaction_score must be between 0.0 and 1.0")
        
        user_feedback = {
            "satisfaction_score": satisfaction_score,
            "feedback_text": feedback_text,
            "submitted_at": datetime.now().isoformat()
        }
        
        # Save user feedback (this could be extended to trigger re-evaluation)
        feedback_data = {
            "conversation_id": conversation_id,
            "agent_role": agent_role,
            "user_email": user_email,
            "user_feedback": user_feedback
        }
        
        # For now, we'll just return success. In a full implementation,
        # this would save to a database and potentially trigger re-evaluation
        return {
            "status": "success",
            "message": "User feedback submitted successfully",
            "feedback": feedback_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting user feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit user feedback: {str(e)}")

@router.get("/evaluation-metrics")
async def get_evaluation_metrics_endpoint():
    """Get available evaluation metrics and their descriptions"""
    metrics_info = [
        {
            "metric": metric.value,
            "name": metric.value.replace("_", " ").title(),
            "description": _get_metric_description(metric),
            "weight": _get_metric_weight(metric)
        }
        for metric in EvaluationMetric
    ]
    
    return {
        "status": "success",
        "metrics": metrics_info,
        "total_weight": sum(_get_metric_weight(metric) for metric in EvaluationMetric)
    }

@router.get("/evaluation-history/{agent_role}")
async def get_evaluation_history_endpoint(
    agent_role: str,
    user_email: Optional[str] = None,
    limit: int = 10,
    evaluation_service: AgentEvaluationService = Depends(get_evaluation_service)
):
    """Get evaluation history for an agent"""
    try:
        # This would typically query a database for evaluation history
        # For now, we'll return a placeholder response
        return {
            "status": "success",
            "message": "Evaluation history endpoint ready",
            "agent_role": agent_role,
            "user_email": user_email,
            "limit": limit,
            "note": "Full implementation would query evaluation database"
        }
        
    except Exception as e:
        print(f"Error getting evaluation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation history: {str(e)}")

def _get_metric_description(metric: EvaluationMetric) -> str:
    """Get human-readable description for a metric"""
    descriptions = {
        EvaluationMetric.RESPONSE_QUALITY: "Quality and comprehensiveness of agent responses",
        EvaluationMetric.TECHNICAL_ACCURACY: "Technical accuracy and domain expertise",
        EvaluationMetric.COMMUNICATION_CLARITY: "Clarity and effectiveness of communication",
        EvaluationMetric.PROBLEM_SOLVING: "Problem-solving approach and methodology",
        EvaluationMetric.USER_SATISFACTION: "User satisfaction and engagement level",
        EvaluationMetric.RESPONSE_TIME: "Speed and efficiency of response generation",
        EvaluationMetric.CONTEXT_UNDERSTANDING: "Understanding and retention of conversation context"
    }
    return descriptions.get(metric, "Evaluation metric")

def _get_metric_weight(metric: EvaluationMetric) -> float:
    """Get weight for a metric"""
    weights = {
        EvaluationMetric.RESPONSE_QUALITY: 0.25,
        EvaluationMetric.TECHNICAL_ACCURACY: 0.25,
        EvaluationMetric.COMMUNICATION_CLARITY: 0.20,
        EvaluationMetric.PROBLEM_SOLVING: 0.15,
        EvaluationMetric.USER_SATISFACTION: 0.10,
        EvaluationMetric.RESPONSE_TIME: 0.03,
        EvaluationMetric.CONTEXT_UNDERSTANDING: 0.02
    }
    return weights.get(metric, 0.0)

"""
Enhanced Agent Evaluation System
Provides comprehensive evaluation metrics and feedback for AI agents
"""

import json
import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class EvaluationMetric(Enum):
    """Types of evaluation metrics"""
    RESPONSE_QUALITY = "response_quality"
    TECHNICAL_ACCURACY = "technical_accuracy"
    COMMUNICATION_CLARITY = "communication_clarity"
    PROBLEM_SOLVING = "problem_solving"
    USER_SATISFACTION = "user_satisfaction"
    RESPONSE_TIME = "response_time"
    CONTEXT_UNDERSTANDING = "context_understanding"

@dataclass
class EvaluationScore:
    """Individual evaluation score"""
    metric: EvaluationMetric
    score: float  # 0.0 to 1.0
    weight: float  # Importance weight
    feedback: str
    timestamp: datetime

@dataclass
class AgentEvaluation:
    """Complete agent evaluation"""
    agent_role: str
    user_email: str
    conversation_id: str
    overall_score: float
    individual_scores: List[EvaluationScore]
    strengths: List[str]
    improvements: List[str]
    recommendations: List[str]
    evaluation_date: datetime
    evaluator_type: str  # "user", "system", "peer"

class AgentEvaluationService:
    """Service for evaluating agent performance"""
    
    def __init__(self):
        self.evaluations_dir = Path("evaluations")
        self.evaluations_dir.mkdir(exist_ok=True)
        
        # Evaluation criteria weights
        self.metric_weights = {
            EvaluationMetric.RESPONSE_QUALITY: 0.25,
            EvaluationMetric.TECHNICAL_ACCURACY: 0.25,
            EvaluationMetric.COMMUNICATION_CLARITY: 0.20,
            EvaluationMetric.PROBLEM_SOLVING: 0.15,
            EvaluationMetric.USER_SATISFACTION: 0.10,
            EvaluationMetric.RESPONSE_TIME: 0.03,
            EvaluationMetric.CONTEXT_UNDERSTANDING: 0.02
        }
    
    async def evaluate_conversation(
        self,
        agent_role: str,
        user_email: str,
        conversation_id: str,
        conversation_data: Dict[str, Any],
        user_feedback: Optional[Dict[str, Any]] = None
    ) -> AgentEvaluation:
        """Evaluate a complete conversation"""
        
        # Extract conversation metrics
        messages = conversation_data.get("messages", [])
        response_times = self._calculate_response_times(messages)
        
        # Generate individual scores
        individual_scores = []
        
        # Response Quality
        response_quality_score = await self._evaluate_response_quality(messages)
        individual_scores.append(EvaluationScore(
            metric=EvaluationMetric.RESPONSE_QUALITY,
            score=response_quality_score,
            weight=self.metric_weights[EvaluationMetric.RESPONSE_QUALITY],
            feedback=self._generate_response_quality_feedback(response_quality_score),
            timestamp=datetime.now()
        ))
        
        # Technical Accuracy
        technical_score = await self._evaluate_technical_accuracy(messages, agent_role)
        individual_scores.append(EvaluationScore(
            metric=EvaluationMetric.TECHNICAL_ACCURACY,
            score=technical_score,
            weight=self.metric_weights[EvaluationMetric.TECHNICAL_ACCURACY],
            feedback=self._generate_technical_feedback(technical_score, agent_role),
            timestamp=datetime.now()
        ))
        
        # Communication Clarity
        clarity_score = await self._evaluate_communication_clarity(messages)
        individual_scores.append(EvaluationScore(
            metric=EvaluationMetric.COMMUNICATION_CLARITY,
            score=clarity_score,
            weight=self.metric_weights[EvaluationMetric.COMMUNICATION_CLARITY],
            feedback=self._generate_clarity_feedback(clarity_score),
            timestamp=datetime.now()
        ))
        
        # Problem Solving
        problem_solving_score = await self._evaluate_problem_solving(messages)
        individual_scores.append(EvaluationScore(
            metric=EvaluationMetric.PROBLEM_SOLVING,
            score=problem_solving_score,
            weight=self.metric_weights[EvaluationMetric.PROBLEM_SOLVING],
            feedback=self._generate_problem_solving_feedback(problem_solving_score),
            timestamp=datetime.now()
        ))
        
        # User Satisfaction (from user feedback if available)
        user_satisfaction_score = 0.5  # Default neutral score
        if user_feedback:
            user_satisfaction_score = user_feedback.get("satisfaction_score", 0.5)
        
        individual_scores.append(EvaluationScore(
            metric=EvaluationMetric.USER_SATISFACTION,
            score=user_satisfaction_score,
            weight=self.metric_weights[EvaluationMetric.USER_SATISFACTION],
            feedback=self._generate_user_satisfaction_feedback(user_satisfaction_score),
            timestamp=datetime.now()
        ))
        
        # Response Time
        avg_response_time = sum(response_times) / len(response_times) if response_times else 5.0
        response_time_score = max(0.0, min(1.0, 1.0 - (avg_response_time / 10.0)))  # Normalize to 0-1
        
        individual_scores.append(EvaluationScore(
            metric=EvaluationMetric.RESPONSE_TIME,
            score=response_time_score,
            weight=self.metric_weights[EvaluationMetric.RESPONSE_TIME],
            feedback=self._generate_response_time_feedback(avg_response_time),
            timestamp=datetime.now()
        ))
        
        # Context Understanding
        context_score = await self._evaluate_context_understanding(messages)
        individual_scores.append(EvaluationScore(
            metric=EvaluationMetric.CONTEXT_UNDERSTANDING,
            score=context_score,
            weight=self.metric_weights[EvaluationMetric.CONTEXT_UNDERSTANDING],
            feedback=self._generate_context_feedback(context_score),
            timestamp=datetime.now()
        ))
        
        # Calculate overall score
        overall_score = sum(score.score * score.weight for score in individual_scores)
        
        # Generate insights
        strengths = self._identify_strengths(individual_scores)
        improvements = self._identify_improvements(individual_scores)
        recommendations = self._generate_recommendations(individual_scores, agent_role)
        
        # Create evaluation
        evaluation = AgentEvaluation(
            agent_role=agent_role,
            user_email=user_email,
            conversation_id=conversation_id,
            overall_score=overall_score,
            individual_scores=individual_scores,
            strengths=strengths,
            improvements=improvements,
            recommendations=recommendations,
            evaluation_date=datetime.now(),
            evaluator_type="system"
        )
        
        # Save evaluation
        await self._save_evaluation(evaluation)
        
        return evaluation
    
    def _calculate_response_times(self, messages: List[Dict[str, Any]]) -> List[float]:
        """Calculate response times between messages"""
        response_times = []
        
        for i in range(1, len(messages), 2):  # Every other message (assistant responses)
            if i < len(messages):
                try:
                    user_time = datetime.fromisoformat(messages[i-1]["timestamp"])
                    assistant_time = datetime.fromisoformat(messages[i]["timestamp"])
                    response_time = (assistant_time - user_time).total_seconds()
                    response_times.append(response_time)
                except (KeyError, ValueError):
                    continue
        
        return response_times
    
    async def _evaluate_response_quality(self, messages: List[Dict[str, Any]]) -> float:
        """Evaluate the quality of responses"""
        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
        
        if not assistant_messages:
            return 0.0
        
        quality_indicators = 0
        total_indicators = 0
        
        for message in assistant_messages:
            content = message.get("content", "").lower()
            
            # Check for quality indicators
            if len(content) > 50:  # Substantial response
                quality_indicators += 1
            total_indicators += 1
            
            if any(word in content for word in ["analysis", "recommendation", "suggestion", "consider"]):
                quality_indicators += 1
            total_indicators += 1
            
            if any(word in content for word in ["based on", "according to", "in my experience"]):
                quality_indicators += 1
            total_indicators += 1
        
        return quality_indicators / total_indicators if total_indicators > 0 else 0.0
    
    async def _evaluate_technical_accuracy(self, messages: List[Dict[str, Any]], agent_role: str) -> float:
        """Evaluate technical accuracy based on agent role"""
        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
        
        if not assistant_messages:
            return 0.0
        
        # Role-specific technical keywords
        technical_keywords = {
            "corrosion_engineer": ["corrosion", "material", "degradation", "prevention", "inspection", "coating"],
            "subsea_engineer": ["subsea", "underwater", "ROV", "pipeline", "structure", "marine"],
            "methods_specialist": ["methodology", "procedure", "process", "optimization", "efficiency", "standard"],
            "discipline_head": ["strategy", "management", "coordination", "oversight", "planning", "leadership"]
        }
        
        keywords = technical_keywords.get(agent_role, [])
        technical_score = 0.0
        
        for message in assistant_messages:
            content = message.get("content", "").lower()
            keyword_count = sum(1 for keyword in keywords if keyword in content)
            technical_score += min(1.0, keyword_count / len(keywords)) if keywords else 0.5
        
        return technical_score / len(assistant_messages) if assistant_messages else 0.0
    
    async def _evaluate_communication_clarity(self, messages: List[Dict[str, Any]]) -> float:
        """Evaluate communication clarity"""
        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
        
        if not assistant_messages:
            return 0.0
        
        clarity_score = 0.0
        
        for message in assistant_messages:
            content = message.get("content", "")
            
            # Check for clarity indicators
            if len(content.split()) > 10:  # Substantial content
                clarity_score += 0.3
            
            if any(word in content.lower() for word in ["clearly", "specifically", "in summary", "to clarify"]):
                clarity_score += 0.2
            
            if content.count(".") > 0:  # Proper sentence structure
                clarity_score += 0.2
            
            if len(content) > 100:  # Detailed response
                clarity_score += 0.3
        
        return min(1.0, clarity_score / len(assistant_messages)) if assistant_messages else 0.0
    
    async def _evaluate_problem_solving(self, messages: List[Dict[str, Any]]) -> float:
        """Evaluate problem-solving approach"""
        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
        
        if not assistant_messages:
            return 0.0
        
        problem_solving_score = 0.0
        
        for message in assistant_messages:
            content = message.get("content", "").lower()
            
            # Check for problem-solving indicators
            if any(word in content for word in ["solution", "approach", "strategy", "method"]):
                problem_solving_score += 0.4
            
            if any(word in content for word in ["step", "process", "procedure", "workflow"]):
                problem_solving_score += 0.3
            
            if any(word in content for word in ["recommend", "suggest", "propose", "advise"]):
                problem_solving_score += 0.3
        
        return min(1.0, problem_solving_score / len(assistant_messages)) if assistant_messages else 0.0
    
    async def _evaluate_context_understanding(self, messages: List[Dict[str, Any]]) -> float:
        """Evaluate context understanding"""
        if len(messages) < 2:
            return 0.0
        
        context_score = 0.0
        
        # Check if assistant references previous conversation
        for i, message in enumerate(messages):
            if message.get("role") == "assistant" and i > 0:
                content = message.get("content", "").lower()
                
                if any(word in content for word in ["as mentioned", "previously", "earlier", "before"]):
                    context_score += 0.5
                
                if any(word in content for word in ["based on your", "considering your", "given your"]):
                    context_score += 0.5
        
        return min(1.0, context_score)
    
    def _generate_response_quality_feedback(self, score: float) -> str:
        """Generate feedback for response quality"""
        if score >= 0.8:
            return "Excellent response quality with comprehensive and detailed answers."
        elif score >= 0.6:
            return "Good response quality with adequate detail and structure."
        elif score >= 0.4:
            return "Fair response quality, could benefit from more detailed explanations."
        else:
            return "Response quality needs improvement. Consider providing more comprehensive answers."
    
    def _generate_technical_feedback(self, score: float, agent_role: str) -> str:
        """Generate technical accuracy feedback"""
        role_name = agent_role.replace("_", " ").title()
        
        if score >= 0.8:
            return f"Excellent technical accuracy for {role_name} with strong domain knowledge."
        elif score >= 0.6:
            return f"Good technical accuracy for {role_name} with solid domain understanding."
        elif score >= 0.4:
            return f"Fair technical accuracy for {role_name}, consider strengthening domain expertise."
        else:
            return f"Technical accuracy needs improvement for {role_name}. Focus on domain-specific knowledge."
    
    def _generate_clarity_feedback(self, score: float) -> str:
        """Generate communication clarity feedback"""
        if score >= 0.8:
            return "Excellent communication clarity with well-structured and understandable responses."
        elif score >= 0.6:
            return "Good communication clarity with clear and coherent explanations."
        elif score >= 0.4:
            return "Fair communication clarity, consider improving sentence structure and explanations."
        else:
            return "Communication clarity needs improvement. Focus on clearer explanations and structure."
    
    def _generate_problem_solving_feedback(self, score: float) -> str:
        """Generate problem-solving feedback"""
        if score >= 0.8:
            return "Excellent problem-solving approach with systematic and strategic thinking."
        elif score >= 0.6:
            return "Good problem-solving approach with logical reasoning and suggestions."
        elif score >= 0.4:
            return "Fair problem-solving approach, consider providing more structured solutions."
        else:
            return "Problem-solving approach needs improvement. Focus on systematic solution development."
    
    def _generate_user_satisfaction_feedback(self, score: float) -> str:
        """Generate user satisfaction feedback"""
        if score >= 0.8:
            return "High user satisfaction with positive feedback and engagement."
        elif score >= 0.6:
            return "Good user satisfaction with generally positive interactions."
        elif score >= 0.4:
            return "Fair user satisfaction, consider improving user experience and engagement."
        else:
            return "User satisfaction needs improvement. Focus on better user experience and interaction."
    
    def _generate_response_time_feedback(self, avg_time: float) -> str:
        """Generate response time feedback"""
        if avg_time <= 2.0:
            return f"Excellent response time ({avg_time:.1f}s) with quick and efficient responses."
        elif avg_time <= 5.0:
            return f"Good response time ({avg_time:.1f}s) with reasonable response speed."
        elif avg_time <= 10.0:
            return f"Fair response time ({avg_time:.1f}s), consider optimizing for faster responses."
        else:
            return f"Response time needs improvement ({avg_time:.1f}s). Focus on faster response generation."
    
    def _generate_context_feedback(self, score: float) -> str:
        """Generate context understanding feedback"""
        if score >= 0.8:
            return "Excellent context understanding with strong conversation memory and continuity."
        elif score >= 0.6:
            return "Good context understanding with adequate conversation awareness."
        elif score >= 0.4:
            return "Fair context understanding, consider improving conversation continuity."
        else:
            return "Context understanding needs improvement. Focus on better conversation memory."
    
    def _identify_strengths(self, scores: List[EvaluationScore]) -> List[str]:
        """Identify agent strengths"""
        strengths = []
        
        for score in scores:
            if score.score >= 0.8:
                strengths.append(f"Strong {score.metric.value.replace('_', ' ')}")
        
        return strengths if strengths else ["Consistent performance across all metrics"]
    
    def _identify_improvements(self, scores: List[EvaluationScore]) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        
        for score in scores:
            if score.score < 0.6:
                improvements.append(f"Improve {score.metric.value.replace('_', ' ')}")
        
        return improvements if improvements else ["Maintain current performance levels"]
    
    def _generate_recommendations(self, scores: List[EvaluationScore], agent_role: str) -> List[str]:
        """Generate specific recommendations"""
        recommendations = []
        
        # Find lowest scoring metrics
        lowest_scores = sorted(scores, key=lambda x: x.score)[:2]
        
        for score in lowest_scores:
            if score.metric == EvaluationMetric.TECHNICAL_ACCURACY:
                recommendations.append(f"Enhance {agent_role.replace('_', ' ')} domain knowledge and technical expertise")
            elif score.metric == EvaluationMetric.COMMUNICATION_CLARITY:
                recommendations.append("Improve communication skills and response structure")
            elif score.metric == EvaluationMetric.PROBLEM_SOLVING:
                recommendations.append("Develop more systematic problem-solving approaches")
            elif score.metric == EvaluationMetric.RESPONSE_TIME:
                recommendations.append("Optimize response generation for faster delivery")
        
        return recommendations if recommendations else ["Continue current performance trajectory"]
    
    async def _save_evaluation(self, evaluation: AgentEvaluation) -> None:
        """Save evaluation to disk"""
        evaluation_file = self.evaluations_dir / f"{evaluation.conversation_id}_evaluation.json"
        
        evaluation_data = {
            "agent_role": evaluation.agent_role,
            "user_email": evaluation.user_email,
            "conversation_id": evaluation.conversation_id,
            "overall_score": evaluation.overall_score,
            "individual_scores": [
                {
                    "metric": score.metric.value,
                    "score": score.score,
                    "weight": score.weight,
                    "feedback": score.feedback,
                    "timestamp": score.timestamp.isoformat()
                }
                for score in evaluation.individual_scores
            ],
            "strengths": evaluation.strengths,
            "improvements": evaluation.improvements,
            "recommendations": evaluation.recommendations,
            "evaluation_date": evaluation.evaluation_date.isoformat(),
            "evaluator_type": evaluation.evaluator_type
        }
        
        with open(evaluation_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_data, f, indent=2)
    
    async def get_agent_performance_summary(
        self, 
        agent_role: str, 
        user_email: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance summary for an agent"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        evaluations = []
        
        # Load all evaluations for the agent
        for evaluation_file in self.evaluations_dir.glob("*_evaluation.json"):
            try:
                with open(evaluation_file, 'r', encoding='utf-8') as f:
                    eval_data = json.load(f)
                
                if eval_data["agent_role"] == agent_role:
                    if user_email is None or eval_data["user_email"] == user_email:
                        eval_date = datetime.fromisoformat(eval_data["evaluation_date"])
                        if eval_date >= cutoff_date:
                            evaluations.append(eval_data)
            except Exception as e:
                print(f"Error loading evaluation {evaluation_file}: {e}")
                continue
        
        if not evaluations:
            return {"message": "No evaluations found for the specified criteria"}
        
        # Calculate summary statistics
        overall_scores = [eval_data["overall_score"] for eval_data in evaluations]
        
        summary = {
            "agent_role": agent_role,
            "user_email": user_email,
            "period_days": days,
            "total_evaluations": len(evaluations),
            "average_score": sum(overall_scores) / len(overall_scores),
            "highest_score": max(overall_scores),
            "lowest_score": min(overall_scores),
            "score_trend": self._calculate_score_trend(evaluations),
            "common_strengths": self._get_common_items(evaluations, "strengths"),
            "common_improvements": self._get_common_items(evaluations, "improvements"),
            "top_recommendations": self._get_common_items(evaluations, "recommendations"),
            "evaluation_dates": [eval_data["evaluation_date"] for eval_data in evaluations]
        }
        
        return summary
    
    def _calculate_score_trend(self, evaluations: List[Dict[str, Any]]) -> str:
        """Calculate score trend over time"""
        if len(evaluations) < 2:
            return "insufficient_data"
        
        # Sort by date
        sorted_evals = sorted(evaluations, key=lambda x: x["evaluation_date"])
        recent_scores = [eval_data["overall_score"] for eval_data in sorted_evals[-3:]]
        older_scores = [eval_data["overall_score"] for eval_data in sorted_evals[:3]]
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg + 0.1:
            return "improving"
        elif recent_avg < older_avg - 0.1:
            return "declining"
        else:
            return "stable"
    
    def _get_common_items(self, evaluations: List[Dict[str, Any]], field: str) -> List[str]:
        """Get most common items from evaluations"""
        all_items = []
        for eval_data in evaluations:
            all_items.extend(eval_data.get(field, []))
        
        # Count occurrences
        item_counts = {}
        for item in all_items:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        # Return most common items
        sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        return [item for item, count in sorted_items[:5]]

"""
FastAPI main application for AgenticOne Backend
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.config import settings
from app.agents.discipline_head import DisciplineHead
from app.agents.methods_specialist import MethodsSpecialist
from app.agents.corrosion_engineer import CorrosionEngineer
from app.agents.subsea_engineer import SubseaEngineer
from app.services.rag_service import RAGService
from app.services.vision_service import VisionService
from app.services.report_generator import ReportGenerator
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    DocumentUpload,
    ReportRequest,
    ReportResponse
)
from app.api.oauth_handler import router as oauth_router

# Global services
rag_service = None
vision_service = None
report_generator = None
agents = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global rag_service, vision_service, report_generator, agents
    
    try:
        # Initialize services
        rag_service = RAGService()
        vision_service = VisionService()
        report_generator = ReportGenerator()
        
        # Initialize agents
        agents = {
            "discipline_head": DisciplineHead(rag_service, vision_service),
            "methods_specialist": MethodsSpecialist(rag_service, vision_service),
            "corrosion_engineer": CorrosionEngineer(rag_service, vision_service),
            "subsea_engineer": SubseaEngineer(rag_service, vision_service)
        }
    except Exception as e:
        print(f"Warning: Some services could not be initialized: {e}")
        # Initialize with None values for development
        rag_service = None
        vision_service = None
        report_generator = None
        agents = {}
    
    yield
    
    # Cleanup
    if rag_service:
        await rag_service.close()

# Create FastAPI app
app = FastAPI(
    title="AgenticOne Backend",
    description="AI-powered engineering analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include OAuth router
app.include_router(oauth_router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AgenticOne Backend API", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "rag": rag_service is not None,
            "vision": vision_service is not None,
            "report_generator": report_generator is not None,
            "agents": len(agents) if agents else 0
        }
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(request: AnalysisRequest):
    """Analyze document using specialized agents"""
    try:
        # Route to appropriate agent based on document type or analysis type
        agent_type = request.agent_type or "discipline_head"
        
        if agent_type not in agents:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        agent = agents[agent_type]
        result = await agent.analyze(request.document_id, request.analysis_type, request.parameters)
        
        return AnalysisResponse(
            analysis_id=result["analysis_id"],
            agent_type=agent_type,
            results=result["results"],
            confidence=result["confidence"],
            recommendations=result["recommendations"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=dict)
async def upload_document(document: DocumentUpload):
    """Upload and process document"""
    try:
        # Process document through RAG service
        document_id = await rag_service.process_document(
            document.content,
            document.filename,
            document.metadata
        )
        
        return {
            "document_id": document_id,
            "status": "processed",
            "message": "Document uploaded and processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate comprehensive analysis report"""
    try:
        report = await report_generator.generate_report(
            request.analysis_ids,
            request.report_type,
            request.template
        )
        
        return ReportResponse(
            report_id=report["report_id"],
            report_url=report["report_url"],
            status="generated"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List available agents and their capabilities"""
    return {
        "agents": {
            "discipline_head": {
                "name": "Discipline Head",
                "description": "Overall project coordination and decision making",
                "capabilities": ["project_oversight", "decision_making", "coordination"]
            },
            "methods_specialist": {
                "name": "Methods Specialist", 
                "description": "Specialized in engineering methods and procedures",
                "capabilities": ["method_analysis", "procedure_optimization", "best_practices"]
            },
            "corrosion_engineer": {
                "name": "Corrosion Engineer",
                "description": "Expert in corrosion analysis and prevention",
                "capabilities": ["corrosion_analysis", "material_selection", "prevention_strategies"]
            },
            "subsea_engineer": {
                "name": "Subsea Engineer",
                "description": "Specialized in subsea systems and operations",
                "capabilities": ["subsea_systems", "underwater_operations", "marine_engineering"]
            }
        }
    }

@app.post("/chat")
async def chat_with_agent(request: dict):
    """Chat with a specific agent"""
    try:
        agent_type = request.get("agent_type", "methods_specialist")
        message = request.get("message", "")
        
        if agent_type not in agents:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        if not agents[agent_type]:
            raise HTTPException(status_code=503, detail=f"Agent {agent_type} is not available")
        
        agent = agents[agent_type]
        
        # Use the agent's chat method if available, otherwise use analyze
        if hasattr(agent, 'chat'):
            response = await agent.chat(message)
        else:
            # Fallback to analyze method
            response = await agent.analyze(
                document_id="chat",
                analysis_type="conversation",
                parameters={"message": message}
            )
        
        return {
            "agent_type": agent_type,
            "response": response.get("results", response),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

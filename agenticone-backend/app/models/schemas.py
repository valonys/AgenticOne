"""
Pydantic schemas for API requests and responses
"""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    """Available agent types"""
    DISCIPLINE_HEAD = "discipline_head"
    METHODS_SPECIALIST = "methods_specialist"
    CORROSION_ENGINEER = "corrosion_engineer"
    SUBSEA_ENGINEER = "subsea_engineer"

class AnalysisType(str, Enum):
    """Available analysis types"""
    DOCUMENT_ANALYSIS = "document_analysis"
    IMAGE_ANALYSIS = "image_analysis"
    CORROSION_ANALYSIS = "corrosion_analysis"
    SUBSEA_ANALYSIS = "subsea_analysis"
    METHODS_ANALYSIS = "methods_analysis"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"

class ReportType(str, Enum):
    """Available report types"""
    TECHNICAL_REPORT = "technical_report"
    ANALYSIS_SUMMARY = "analysis_summary"
    RECOMMENDATIONS = "recommendations"
    COMPLIANCE_REPORT = "compliance_report"

# Request Models
class AnalysisRequest(BaseModel):
    """Request for document analysis"""
    document_id: str = Field(..., description="ID of the document to analyze")
    analysis_type: AnalysisType = Field(..., description="Type of analysis to perform")
    agent_type: Optional[AgentType] = Field(None, description="Specific agent to use")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Analysis parameters")

class DocumentUpload(BaseModel):
    """Document upload request"""
    content: bytes = Field(..., description="Document content")
    filename: str = Field(..., description="Original filename")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Document metadata")
    document_type: Optional[str] = Field(None, description="Type of document (pdf, image, etc.)")

class ReportRequest(BaseModel):
    """Request for report generation"""
    analysis_ids: List[str] = Field(..., description="IDs of analyses to include in report")
    report_type: ReportType = Field(..., description="Type of report to generate")
    template: Optional[str] = Field(None, description="Custom report template")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Report parameters")

# Response Models
class AnalysisResult(BaseModel):
    """Individual analysis result"""
    category: str = Field(..., description="Result category")
    findings: List[str] = Field(..., description="Key findings")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")

class AnalysisResponse(BaseModel):
    """Response for analysis request"""
    analysis_id: str = Field(..., description="Unique analysis ID")
    agent_type: str = Field(..., description="Agent that performed the analysis")
    results: List[AnalysisResult] = Field(..., description="Analysis results")
    confidence: float = Field(..., ge=0, le=1, description="Overall confidence score")
    recommendations: List[str] = Field(..., description="Recommendations")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")

class ReportResponse(BaseModel):
    """Response for report generation"""
    report_id: str = Field(..., description="Unique report ID")
    report_url: str = Field(..., description="URL to access the report")
    status: str = Field(..., description="Report generation status")

class DocumentMetadata(BaseModel):
    """Document metadata"""
    document_id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    document_type: str = Field(..., description="Document type")
    size: int = Field(..., description="File size in bytes")
    upload_date: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AgentCapability(BaseModel):
    """Agent capability description"""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Required parameters")

class AgentInfo(BaseModel):
    """Agent information"""
    agent_id: str = Field(..., description="Agent identifier")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")
    status: str = Field(..., description="Agent status")

# Database Models
class AnalysisRecord(BaseModel):
    """Analysis record for database storage"""
    analysis_id: str
    document_id: str
    agent_type: str
    analysis_type: str
    results: Dict[str, Any]
    confidence: float
    recommendations: List[str]
    created_at: datetime
    updated_at: datetime

class DocumentRecord(BaseModel):
    """Document record for database storage"""
    document_id: str
    filename: str
    document_type: str
    size: int
    storage_path: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ReportRecord(BaseModel):
    """Report record for database storage"""
    report_id: str
    analysis_ids: List[str]
    report_type: str
    template: Optional[str]
    report_url: str
    status: str
    created_at: datetime
    updated_at: datetime

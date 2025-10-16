"""
Firestore database models and operations
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.config import settings
from app.models.schemas import AnalysisRecord, DocumentRecord, ReportRecord

class FirestoreClient:
    """Firestore database client"""
    
    def __init__(self):
        self.db = None
        self.collections = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Initialize the Firestore client if not already done"""
        if not self._initialized:
            try:
                self.db = firestore.Client(
                    project=settings.FIRESTORE_PROJECT_ID,
                    database=settings.FIRESTORE_DATABASE_ID
                )
                self.collections = {
                    "documents": self.db.collection("documents"),
                    "analyses": self.db.collection("analyses"),
                    "reports": self.db.collection("reports"),
                    "agents": self.db.collection("agents")
                }
                self._initialized = True
            except Exception as e:
                print(f"Warning: Could not initialize Firestore client: {e}")
                # Create mock collections for development
                self.collections = {
                    "documents": None,
                    "analyses": None,
                    "reports": None,
                    "agents": None
                }
                self._initialized = True
    
    async def create_document(self, document_data: Dict[str, Any]) -> str:
        """Create a new document record"""
        self._ensure_initialized()
        document_id = str(uuid.uuid4())
        document_record = DocumentRecord(
            document_id=document_id,
            filename=document_data["filename"],
            document_type=document_data["document_type"],
            size=document_data["size"],
            storage_path=document_data["storage_path"],
            metadata=document_data.get("metadata", {}),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        if self.collections["documents"]:
            self.collections["documents"].document(document_id).set(document_record.dict())
        return document_id
    
    async def get_document(self, document_id: str) -> Optional[DocumentRecord]:
        """Get document by ID"""
        self._ensure_initialized()
        if not self.collections["documents"]:
            return None
        doc = self.collections["documents"].document(document_id).get()
        if doc.exists:
            return DocumentRecord(**doc.to_dict())
        return None
    
    async def create_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Create a new analysis record"""
        analysis_id = str(uuid.uuid4())
        analysis_record = AnalysisRecord(
            analysis_id=analysis_id,
            document_id=analysis_data["document_id"],
            agent_type=analysis_data["agent_type"],
            analysis_type=analysis_data["analysis_type"],
            results=analysis_data["results"],
            confidence=analysis_data["confidence"],
            recommendations=analysis_data["recommendations"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.collections["analyses"].document(analysis_id).set(analysis_record.dict())
        return analysis_id
    
    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisRecord]:
        """Get analysis by ID"""
        doc = self.collections["analyses"].document(analysis_id).get()
        if doc.exists:
            return AnalysisRecord(**doc.to_dict())
        return None
    
    async def get_analyses_by_document(self, document_id: str) -> List[AnalysisRecord]:
        """Get all analyses for a document"""
        query = self.collections["analyses"].where(
            filter=FieldFilter("document_id", "==", document_id)
        )
        docs = query.stream()
        
        analyses = []
        for doc in docs:
            analyses.append(AnalysisRecord(**doc.to_dict()))
        return analyses
    
    async def create_report(self, report_data: Dict[str, Any]) -> str:
        """Create a new report record"""
        report_id = str(uuid.uuid4())
        report_record = ReportRecord(
            report_id=report_id,
            analysis_ids=report_data["analysis_ids"],
            report_type=report_data["report_type"],
            template=report_data.get("template"),
            report_url=report_data["report_url"],
            status=report_data["status"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.collections["reports"].document(report_id).set(report_record.dict())
        return report_id
    
    async def get_report(self, report_id: str) -> Optional[ReportRecord]:
        """Get report by ID"""
        doc = self.collections["reports"].document(report_id).get()
        if doc.exists:
            return ReportRecord(**doc.to_dict())
        return None
    
    async def update_analysis(self, analysis_id: str, updates: Dict[str, Any]) -> bool:
        """Update analysis record"""
        try:
            updates["updated_at"] = datetime.utcnow()
            self.collections["analyses"].document(analysis_id).update(updates)
            return True
        except Exception:
            return False
    
    async def update_report(self, report_id: str, updates: Dict[str, Any]) -> bool:
        """Update report record"""
        try:
            updates["updated_at"] = datetime.utcnow()
            self.collections["reports"].document(report_id).update(updates)
            return True
        except Exception:
            return False
    
    async def search_documents(self, filters: Dict[str, Any]) -> List[DocumentRecord]:
        """Search documents with filters"""
        query = self.collections["documents"]
        
        for field, value in filters.items():
            query = query.where(filter=FieldFilter(field, "==", value))
        
        docs = query.stream()
        documents = []
        for doc in docs:
            documents.append(DocumentRecord(**doc.to_dict()))
        return documents
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent status"""
        doc = self.collections["agents"].document(agent_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    async def update_agent_status(self, agent_id: str, status: Dict[str, Any]) -> bool:
        """Update agent status"""
        try:
            status["updated_at"] = datetime.utcnow()
            self.collections["agents"].document(agent_id).set(status, merge=True)
            return True
        except Exception:
            return False

# Global database client instance
db_client = FirestoreClient()

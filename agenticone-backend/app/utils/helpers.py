"""
Helper functions and utilities
"""
import uuid
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def generate_hash(content: str) -> str:
    """Generate hash for content"""
    return hashlib.md5(content.encode()).hexdigest()

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format timestamp to ISO string"""
    if timestamp is None:
        timestamp = datetime.utcnow()
    return timestamp.isoformat()

def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string to datetime"""
    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_document_type(filename: str) -> str:
    """Validate and determine document type"""
    import mimetypes
    mime_type, _ = mimetypes.guess_type(filename)
    
    if mime_type:
        return mime_type
    
    # Fallback to file extension
    extension = filename.lower().split('.')[-1]
    extension_map = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'tiff': 'image/tiff',
        'txt': 'text/plain',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    return extension_map.get(extension, 'application/octet-stream')

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:255-len(ext)-1] + '.' + ext
    return sanitized

def calculate_confidence(factors: List[float]) -> float:
    """Calculate overall confidence from multiple factors"""
    if not factors:
        return 0.0
    
    # Weighted average with higher weights for more reliable factors
    weights = [1.0] * len(factors)
    weighted_sum = sum(f * w for f, w in zip(factors, weights))
    total_weight = sum(weights)
    
    return weighted_sum / total_weight if total_weight > 0 else 0.0

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text"""
    import re
    
    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might'
    }
    
    filtered_words = [word for word in words if word not in stop_words]
    
    # Count frequency
    word_count = {}
    for word in filtered_words:
        word_count[word] = word_count.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def create_error_response(message: str, code: str = "UNKNOWN_ERROR") -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "error": True,
        "message": message,
        "code": code,
        "timestamp": format_timestamp()
    }

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": format_timestamp()
    }

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate required fields in data"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    return missing_fields

def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def parse_json_safe(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def get_time_ago(timestamp: datetime) -> str:
    """Get human readable time ago string"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"

def create_pagination_metadata(
    page: int, 
    per_page: int, 
    total: int
) -> Dict[str, Any]:
    """Create pagination metadata"""
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }

def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
    """Mask sensitive data in dictionary"""
    masked_data = data.copy()
    
    for field in sensitive_fields:
        if field in masked_data:
            value = masked_data[field]
            if isinstance(value, str) and len(value) > 4:
                masked_data[field] = value[:2] + "*" * (len(value) - 4) + value[-2:]
            else:
                masked_data[field] = "***"
    
    return masked_data

def validate_confidence_score(confidence: float) -> bool:
    """Validate confidence score is between 0 and 1"""
    return 0.0 <= confidence <= 1.0

def normalize_confidence_score(confidence: float) -> float:
    """Normalize confidence score to 0-1 range"""
    return max(0.0, min(1.0, confidence))

def create_analysis_id(agent_type: str, document_id: str) -> str:
    """Create analysis ID from agent type and document ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{agent_type}_{document_id[:8]}_{timestamp}"

def format_analysis_results(results: List[Dict[str, Any]]) -> str:
    """Format analysis results for display"""
    if not results:
        return "No results available"
    
    formatted = []
    for i, result in enumerate(results, 1):
        category = result.get("category", "Unknown")
        findings = result.get("findings", [])
        confidence = result.get("confidence", 0)
        
        formatted.append(f"{i}. {category} (Confidence: {confidence:.2f})")
        for finding in findings:
            formatted.append(f"   - {finding}")
        formatted.append("")
    
    return "\n".join(formatted)

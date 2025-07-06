"""
Utility helper functions for the Design Gallery API.
"""

import re
import hashlib
import secrets
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def generate_unique_id(length: int = 8) -> str:
    """Generate a unique ID of specified length."""
    return secrets.token_hex(length)


def validate_image_file(filename: str, allowed_extensions: List[str] = None) -> bool:
    """Validate if a file is a valid image based on extension."""
    if not allowed_extensions:
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    
    if not filename:
        return False
    
    ext = filename.lower().split('.')[-1]
    return f'.{ext}' in allowed_extensions


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing special characters."""
    if not filename:
        return "unnamed"
    
    # Remove path separators and special characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_{2,}', '_', filename)
    
    # Trim underscores from start and end
    filename = filename.strip('_')
    
    return filename or "unnamed"


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA256 hash of file content."""
    return hashlib.sha256(file_content).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def parse_search_query(query: str) -> List[str]:
    """Parse search query into individual terms."""
    if not query:
        return []
    
    # Split by spaces and filter out empty strings
    terms = [term.strip() for term in query.split() if term.strip()]
    
    # Remove duplicates while preserving order
    unique_terms = []
    seen = set()
    for term in terms:
        if term.lower() not in seen:
            unique_terms.append(term)
            seen.add(term.lower())
    
    return unique_terms


def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary."""
    return {k: v for k, v in data.items() if v is not None}


def paginate_results(
    items: List[Any], 
    page: int, 
    per_page: int
) -> Dict[str, Any]:
    """Paginate a list of items."""
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    paginated_items = items[start_index:end_index]
    
    return {
        'items': paginated_items,
        'total': total_items,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text by removing common words."""
    if not text:
        return []
    
    # Common words to exclude
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
        'have', 'had', 'what', 'said', 'each', 'which', 'their', 'time',
        'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
        'her', 'would', 'make', 'like', 'him', 'into', 'has', 'more',
        'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call',
        'who', 'its', 'did', 'get', 'may', 'day', 'use', 'how', 'man',
        'new', 'now', 'old', 'see', 'come', 'made', 'work', 'part'
    }
    
    # Extract words and filter
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    return keywords


def build_search_conditions(
    search_term: str, 
    fields: List[str]
) -> tuple[str, List[str]]:
    """Build SQL search conditions for multiple fields."""
    if not search_term or not fields:
        return "", []
    
    conditions = []
    params = []
    
    for field in fields:
        conditions.append(f"{field} LIKE ?")
        params.append(f"%{search_term}%")
    
    where_clause = " OR ".join(conditions)
    return where_clause, params


def log_api_call(
    method: str,
    endpoint: str,
    user_id: Optional[int] = None,
    status_code: int = 200,
    response_time: float = 0.0
) -> None:
    """Log API call for monitoring."""
    logger.info(
        f"API Call - {method} {endpoint} - "
        f"User: {user_id or 'Anonymous'} - "
        f"Status: {status_code} - "
        f"Time: {response_time:.2f}s"
    )


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data like API keys."""
    if not data or len(data) <= visible_chars:
        return data
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)


def convert_to_snake_case(name: str) -> str:
    """Convert camelCase to snake_case."""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def convert_to_camel_case(name: str) -> str:
    """Convert snake_case to camelCase."""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def is_valid_uuid(uuid_string: str) -> bool:
    """Check if string is a valid UUID."""
    try:
        from uuid import UUID
        UUID(uuid_string)
        return True
    except ValueError:
        return False


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix 
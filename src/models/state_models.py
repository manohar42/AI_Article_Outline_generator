from typing import TypedDict
from typing import List, Dict, Any, Optional, Tuple
from .content_models import  KeywordData, ContentBrief

class OutlineState(TypedDict):

    keywords: KeywordData
    user_preference: Dict[str, Any]

    word_count: int
    word_count_range: Tuple[int, int]
    
    serper_results: List[Dict[str, Any]]
    competitor_analysis: Dict[str,Any]
    research_context : str

    content_gaps: List[Dict[str, Any]]

    content_strategy: Dict[str,Any]
    Outline: Optional[ContentBrief]

    version_history : List[Dict[str, Any]]
    current_version: int
    user_feedback: str
    feedback_intent: str

    errors: List[str]
    processing_time: Dict[str, float]
    confidence_scores: Dict[str,float]
    
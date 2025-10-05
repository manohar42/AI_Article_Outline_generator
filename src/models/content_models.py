from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

class ContentTypeSearchIntent(BaseModel):
    ContentType : str = Field(description="ContentType of the keyword.")
    SearchIntent : str = Field(description="Search Intent of the Article.")
    PriorityScore : str = Field(description="")
class ContentType(str, Enum):
    ULTIMATE_GUIDE = "ultimate_guide"
    HOW_TO = "how_to"
    COMPARISON = "comparison"
    LISTICLE = "listicle"
    REVIEW = "review"

class SearchIntent(str, Enum):
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"

class KeywordData(BaseModel):
    primary: str
    secondary: List[str] = []
    lsi: List[str] = []
    longtail: List[str] = []

class ContentGap(BaseModel):
    topic: str
    description: str
    opportunity_score: int = Field(ge=1, le=10)

class OutlineSection(BaseModel):
    section_id: str
    section_title: str
    short_description: str
    target_keywords: List[str]
    suggested_word_count: int = Field(ge=100, le=2000)
    subsections: List[str] = []
    research_notes: List[str] = []

class FAQ(BaseModel):
    question: str
    answer_brief: str
    target_keywords: List[str] = []

class ContentBrief(BaseModel):
    title: str
    meta_description: str
    content_type: ContentType
    search_intent: SearchIntent
    target_audience: str
    total_word_count: int
    sections: List[OutlineSection]
    faqs: List[FAQ]
    content_gaps_addressed: List[ContentGap]
    internal_link_opportunities: List[str] = []
    
    @field_validator('title')
    @classmethod
    def title_must_contain_primary_keyword(cls, v, values):
        if 'target_keywords' in values and values['target_keywords']:
            primary = values['target_keywords'][0].lower()
            if primary not in v.lower():
                raise ValueError(f"Title should contain primary keyword: {primary}")
        return v

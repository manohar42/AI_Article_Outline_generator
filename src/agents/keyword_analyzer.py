from langchain_openai import ChatOpenAI 
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from src.models.state_models import OutlineState
from typing import List, TypedDict, Tuple
from src.models.content_models import ContentType, SearchIntent, ContentTypeSearchIntent
import re
from dotenv import load_dotenv
import json
from src.agents.tester import Scorer

load_dotenv()

def analyze_keywords(state: OutlineState)-> OutlineState:
    """Analyze keywords and determine content strategy"""

    keywords = state["keywords"]
    primary = keywords.primary
    
    content_type, search_intent = _get_Content_Type_Search_Intent(primary)
    final_score = Scorer().final_score(primary,keywords.secondary)

    strategy = {
        'content_type' : content_type,
        'search_intent':search_intent,
        'target_audience':"general audience",
        'estimated_word_count': state["word_count"],
        'priority_score': final_score["final"]
    }

    state['content_strategy'] = strategy
    state['confidence_scores']['keyword_analysis'] = 0.85

    return state

def _get_Content_Type_Search_Intent(primary_keyword:str) -> tuple[ContentType, SearchIntent]:
    
    llm = ChatOpenAI(model="gpt-4o-mini")
    parser = PydanticOutputParser(pydantic_object=ContentTypeSearchIntent)

    # Generate JSON schema via Pydantic V2 API
    raw_schema_dict = ContentTypeSearchIntent.model_json_schema()  # returns dict
    raw_schema = json.dumps(raw_schema_dict, indent=2)
    # Escape braces so ChatPromptTemplate treats them literally
    escaped_schema = raw_schema.replace("{", "{{").replace("}", "}}")

    # Build prompt messages
    messages = [
        ("system", "Respond **only** with valid JSON matching this schema:"),
        ("system", escaped_schema),
        ("system", "Do not include any commentary or extra keys."),
        ("human", "Primary Keyword: {primary_keyword}")
    ]

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm | parser

    # Invoke with mapping for the single placeholder
    result = chain.invoke({"primary_keyword": primary_keyword})
    return result.ContentType, result.SearchIntent

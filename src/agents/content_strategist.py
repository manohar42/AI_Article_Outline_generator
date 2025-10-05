from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.models.state_models import OutlineState
from src.models.content_models import ContentBrief, OutlineSection, FAQ, ContentGap
import json

def generate_content_strategy(state: OutlineState) -> OutlineState:
    """Generate comprehensive content strategy and outline"""
    
    # Extract data from state
    keywords = state['keywords']
    content_strategy = state.get('content_strategy', {})
    competitor_analysis = state.get('competitor_analysis', {})
    serper_results = state.get('serper_results', [])
    content_gaps = state.get('content_gaps', [])
    
    # Build context for LLM
    context = _build_strategy_context(keywords, content_strategy, competitor_analysis, serper_results, content_gaps)
    
    # Generate outline using LLM
    outline = _generate_outline_with_llm(context, keywords, content_strategy)
    
    if outline:
        state['outline'] = outline.dict() if hasattr(outline, 'dict') else outline
        state['confidence_scores']['content_strategy'] = 0.9
    else:
        state['errors'].append("Failed to generate content outline")
        state['confidence_scores']['content_strategy'] = 0.3
    
    return state

def _build_strategy_context(keywords, content_strategy, competitor_analysis, serper_results, content_gaps):
    """Build comprehensive context for strategy generation"""
    
    context_parts = []
    
    # Handle both dict and KeywordData object formats
    if isinstance(keywords, dict):
        primary_keyword = keywords.get('primary', '')
        secondary_keywords = keywords.get('secondary', [])
        lsi_keywords = keywords.get('lsi', [])
        longtail_keywords =None
    else:
        # KeywordData object
        primary_keyword = keywords.primary
        secondary_keywords = keywords.secondary
        lsi_keywords = keywords.lsi
        longtail_keywords = None
    
    # Keywords context
    context_parts.append(f"PRIMARY KEYWORD: {primary_keyword}")
    if secondary_keywords:
        context_parts.append(f"SECONDARY KEYWORDS: {', '.join(secondary_keywords)}")
    if lsi_keywords:
        context_parts.append(f"LSI KEYWORDS: {', '.join(lsi_keywords)}")
    if longtail_keywords:
        context_parts.append(f"LONGTAIL KEYWORDS: {', '.join(longtail_keywords)}")
    
    # Rest of the function remains the same
    context_parts.append(f"CONTENT TYPE: {content_strategy.get('content_type', 'guide')}")
    context_parts.append(f"SEARCH INTENT: {content_strategy.get('search_intent', 'informational')}")
    context_parts.append(f"TARGET WORD COUNT: {content_strategy.get('estimated_word_count', 2500)}")
    
    # Competitor insights
    if competitor_analysis.get('common_topics'):
        context_parts.append(f"COMPETITOR TOPICS: {', '.join(competitor_analysis['common_topics'][:10])}")
    
    # PAA questions
    if serper_results:
        paa_questions = [paa.get('question', '') for paa in serper_results[0].get('people_also_ask', [])][:5]
        if paa_questions:
            context_parts.append(f"PEOPLE ALSO ASK: {'; '.join(paa_questions)}")
    
    # Content gaps
    if content_gaps:
        gap_topics = [gap.get('topic', '') for gap in content_gaps[:3]]
        context_parts.append(f"CONTENT GAPS TO ADDRESS: {'; '.join(gap_topics)}")
    
    return "\n".join(context_parts)


def _generate_outline_with_llm(context, keywords, content_strategy):
    """Generate structured outline using LLM with Pydantic parser"""
    
    parser = PydanticOutputParser(pydantic_object=ContentBrief)
    
    system_prompt = """You are an expert content strategist specializing in SEO-optimized article outlines. 
    Create a comprehensive, well-structured outline that:
    
    1. Targets the primary keyword naturally throughout
    2. Incorporates secondary and LSI keywords strategically
    3. Addresses search intent and user needs
    4. Covers competitor gaps and unique angles
    5. Includes actionable, specific section titles
    6. Maps People Also Ask questions to relevant sections or FAQs
    
    Focus on creating content that provides genuine value while being optimized for search visibility."""
    
    human_template = """Based on the following research context, create a detailed content outline:
    
    {context}
    
    REQUIREMENTS:
    - Create engaging, specific section titles (not generic)
    - Ensure each section targets relevant keywords naturally
    - Include practical subsections with actionable information
    - Address content gaps identified from competitor analysis
    - Create FAQ section from People Also Ask data
    - Provide brief research notes for each section
    
    {format_instructions}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_template)
    ])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
    try:
        chain = prompt | llm | parser
        
        result = chain.invoke({
            "context": context,
            "format_instructions": parser.get_format_instructions()
        })
        
        return result
        
    except Exception as e:
        # Fallback: try without parser
        try:
            simple_chain = prompt | llm
            raw_result = simple_chain.invoke({
                "context": context,
                "format_instructions": parser.get_format_instructions()
            })
            
            # Attempt to parse manually
            return _parse_outline_manually(raw_result.content, keywords, content_strategy)
            
        except Exception as fallback_error:
            return None

def _parse_outline_manually(raw_content, keywords, content_strategy):
    """Fallback manual parsing if Pydantic parser fails"""
    
    # This is a simplified fallback - in production, you'd want more robust parsing
    try:
        # Try to extract JSON from the raw content
        import re
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            parsed = json.loads(json_str)
            return parsed
    except:
        pass
    
    # Create minimal fallback outline
    return {
        "title": f"Complete Guide to {keywords.primary.title()}",
        "meta_description": f"Discover everything about {keywords.primary}. Expert insights and recommendations.",
        "content_type": content_strategy.get('content_type', 'ultimate_guide'),
        "search_intent": content_strategy.get('search_intent', 'informational'),
        "target_audience": content_strategy.get('target_audience', 'general audience'),
        "total_word_count": content_strategy.get('estimated_word_count', 2500),
        "sections": [
            {
                "section_id": "introduction",
                "section_title": f"What is {keywords.primary.title()}?",
                "short_description": "Introduction and overview",
                "target_keywords": [keywords.primary],
                "suggested_word_count": 300,
                "subsections": ["Overview", "Key Benefits"],
                "research_notes": ["Define the topic clearly"]
            }
        ],
        "faqs": [],
        "content_gaps_addressed": [],
        "internal_link_opportunities": []
    }

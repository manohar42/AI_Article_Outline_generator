# src/workflow/strategy_graph.py

import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Simple approach - direct function calls instead of LangGraph for now
load_dotenv()

# Simple Keywords class
class Keywords:
    def __init__(self, primary="", secondary=None, lsi=None):
        self.primary = str(primary) if primary else ""
        self.secondary = list(secondary) if secondary else []
        self.lsi = list(lsi) if lsi else []
    
    def to_dict(self):
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "lsi": self.lsi
        }

def create_initial_state(topic=None, keywords=None, word_count=2500):
    """Create a consistent initial state"""
    return {
        'topic': topic or '',
        'keywords': keywords or Keywords(),
        'user_preferences': {},
        'serper_results': [],
        'word_count': word_count,
        'word_count_range': f"{word_count-300}-{word_count+300}",
        'competitor_analysis': {},
        'research_context': '',
        'content_gaps': [],
        'content_strategy': {},
        'outline': {},
        'version_history': [],
        'current_version': 1,
        'user_feedback': '',
        'feedback_intent': '',
        'errors': [],
        'processing_time': {},
        'confidence_scores': {},
        'research_metadata': {},
        'research_articles_content': '',
        'all_extracted_keywords': []
    }

def run_keyword_research(state):
    """Run keyword research using the research agent"""
    topic = state.get('topic', '')
    if not topic:
        state['errors'].append("No topic provided for research")
        return state
    
    print(f"🔍 Starting keyword research for: {topic}")
    
    try:
        # Import and run the research agent
        from src.agents.keywords_generator import Research_agent_langgraph
        
        research_results = Research_agent_langgraph(topic)
        
        # Extract keywords from research results
        ordered_keywords = research_results.get('keywords_ordered', {})
        print(ordered_keywords)
        
        # Create Keywords object
        primary = topic  # fallback
        if ordered_keywords.get('Primary Keywords') and len(ordered_keywords['Primary Keywords']) > 0:
            primary = ordered_keywords['Primary Keywords'][0]
        
        secondary = ordered_keywords.get('Secondary Keywords', [])[:10]  # limit to 10
        lsi = ordered_keywords.get('LSI Keywords', [])[:8]  # limit to 8
        
        state['keywords'] = Keywords(primary=primary, secondary=secondary, lsi=lsi)
        state['research_metadata'] = research_results.get('metadata', {})
        state['all_extracted_keywords'] = research_results.get('keywords', [])
        
        print(f"✅ Research completed. Primary: '{state['keywords'].primary}', Secondary: {len(state['keywords'].secondary)}")
        
    except Exception as e:
        print(f"❌ Research failed: {e}")
        state['errors'].append(f"Research failed: {str(e)}")
        state['keywords'] = Keywords(primary=topic, secondary=[], lsi=[])
    
    return state

def run_keyword_analysis(state):
    """Run keyword analysis"""
    try:
        from src.agents.keyword_analyzer import analyze_keywords
        state = analyze_keywords(state)
        print("✅ Keyword analysis completed")
    except Exception as e:
        print(f"❌ Keyword analysis failed: {e}")
        state['errors'].append(f"Keyword analysis failed: {str(e)}")
    
    return state

def run_serper_research(state):
    """Run SERPER research"""
    try:
        from src.agents.serper_research_agent import serper_research
        state = serper_research(state)
        
        serp_results = state.get('serper_results', [])
        count = len(serp_results[0].get('organic', [])) if serp_results else 0
        print(f"✅ SERPER research completed: {count} results")
    except Exception as e:
        print(f"❌ SERPER research failed: {e}")
        state['errors'].append(f"SERPER research failed: {str(e)}")
        state['serper_results'] = []
    
    return state

def run_competitor_analysis(state):
    """Run competitor analysis"""
    try:
        from src.agents.competitor_analysis_agent import competitor_analysis
        state = competitor_analysis(state)
        
        comp_data = state.get('competitor_analysis', {})
        count = comp_data.get('competitors_analyzed', 0)
        print(f"✅ Competitor analysis completed: {count} competitors")
    except Exception as e:
        print(f"❌ Competitor analysis failed: {e}")
        state['errors'].append(f"Competitor analysis failed: {str(e)}")
        state['competitor_analysis'] = {'competitors_analyzed': 0}
    
    return state

def run_content_strategy(state):
    """Run content strategy generation"""
    try:
        from src.agents.content_strategist import generate_content_strategy
        state = generate_content_strategy(state)
        
        outline_exists = bool(state.get('outline'))
        print(f"✅ Content strategy completed: Outline {'generated' if outline_exists else 'failed'}")
    except Exception as e:
        print(f"❌ Content strategy failed: {e}")
        state['errors'].append(f"Content strategy failed: {str(e)}")
        
        # Create fallback outline
        if not state.get('outline'):
            state['outline'] = create_fallback_outline(state)
    
    return state

def create_fallback_outline(state):
    """Create a basic fallback outline if generation fails"""
    keywords = state.get('keywords', Keywords())
    primary = keywords.primary if hasattr(keywords, 'primary') else str(keywords.get('primary', 'Unknown Topic'))
    
    return {
        "title": f"Complete Guide to {primary.title()}",
        "meta_description": f"Learn everything about {primary}. Complete guide with expert insights.",
        "content_type": "guide",
        "search_intent": "informational",
        "target_audience": "general audience",
        "total_word_count": state.get('word_count', 2500),
        "sections": [
            {
                "section_id": "introduction",
                "section_title": f"Introduction to {primary.title()}",
                "short_description": f"Overview of {primary}",
                "target_keywords": [primary],
                "suggested_word_count": 400,
                "subsections": ["What is it?", "Why it matters"],
                "research_notes": ["Define the topic clearly"]
            },
            {
                "section_id": "main_content",
                "section_title": f"Key Aspects of {primary.title()}",
                "short_description": f"Main content about {primary}",
                "target_keywords": [primary],
                "suggested_word_count": 800,
                "subsections": ["Important points", "Key benefits"],
                "research_notes": ["Cover main aspects"]
            }
        ],
        "faqs": [],
        "content_gaps_addressed": [],
        "internal_link_opportunities": []
    }

def generate_outline_from_topic(topic: str, word_count: int = 2500, user_preferences: dict = None) -> dict:
    """Generate outline starting from a topic (includes keyword research)"""
    
    print(f"🚀 Starting full pipeline for topic: '{topic}'")
    
    # Create initial state
    state = create_initial_state(topic=topic, word_count=word_count)
    state['user_preferences'] = user_preferences or {}
    
    # Run the pipeline step by step
    state = run_keyword_research(state)
    state = run_keyword_analysis(state)
    state = run_serper_research(state)
    state = run_competitor_analysis(state)
    state = run_content_strategy(state)
    
    # Convert Keywords object to dict for JSON serialization
    if hasattr(state.get('keywords'), 'to_dict'):
        state['keywords'] = state['keywords'].to_dict()
    
    # Show summary
    errors = len(state.get('errors', []))
    outline_exists = bool(state.get('outline'))
    print(f"🏁 Pipeline completed. Outline: {'✅' if outline_exists else '❌'}, Errors: {errors}")
    
    return state

def generate_outline(keywords_data: dict, word_count: int = 2500, user_preferences: dict = None) -> dict:
    """Generate outline from existing keywords"""
    
    primary = keywords_data.get('primary', 'Unknown Topic')
    print(f"🚀 Starting pipeline from keywords. Primary: '{primary}'")
    
    # Create Keywords object
    keywords_obj = Keywords(
        primary=keywords_data.get('primary', ''),
        secondary=keywords_data.get('secondary', []),
        lsi=keywords_data.get('lsi', [])
    )
    
    # Create initial state
    state = create_initial_state(keywords=keywords_obj, word_count=word_count)
    state['user_preferences'] = user_preferences or {}
    
    # Run the pipeline (skip research)
    state = run_keyword_analysis(state)
    state = run_serper_research(state)
    state = run_competitor_analysis(state)
    state = run_content_strategy(state)
    
    # Convert Keywords object to dict for JSON serialization
    if hasattr(state.get('keywords'), 'to_dict'):
        state['keywords'] = state['keywords'].to_dict()
    
    # Show summary
    errors = len(state.get('errors', []))
    outline_exists = bool(state.get('outline'))
    print(f"🏁 Pipeline completed. Outline: {'✅' if outline_exists else '❌'}, Errors: {errors}")
    
    return state

def process_outline_feedback(current_state: dict, feedback: str) -> dict:
    """Process user feedback on existing outline"""
    try:
        from src.agents.feedback_processor import process_user_feedback
        
        current_state['user_feedback'] = feedback
        result = process_user_feedback(current_state)
        
        print(f"✅ Feedback processed: {feedback[:50]}...")
        return result
        
    except Exception as e:
        print(f"❌ Feedback processing failed: {e}")
        current_state['errors'].append(f"Feedback processing failed: {str(e)}")
        return current_state

# Test the functions directly
if __name__ == "__main__":
    print("🔬 Testing strategy_graph functions...")
    
    # Test 1: From topic
    print("\n" + "="*50)
    print("TEST 1: Generate from topic")
    result1 = generate_outline_from_topic("AI in healthcare", word_count=2500)
    
    keywords1 = result1.get('keywords', {})
    outline1 = result1.get('outline', {})
    print(f"Keywords: {keywords1.get('primary', 'None')}")
    print(f"Outline: {outline1.get('title', 'None')}")
    print(f"Sections: {len(outline1.get('sections', []))}")
    print(f"Errors: {len(result1.get('errors', []))}")
    
    # Test 2: From keywords
    print("\n" + "="*50)
    print("TEST 2: Generate from keywords")
    keywords = {
        'primary': 'Machine Learning in Healthcare',
        'secondary': ['AI diagnosis', 'medical algorithms', 'patient data'],
        'lsi': ['clinical AI', 'healthcare automation']
    }
    
    result2 = generate_outline(keywords, word_count=3000)
    
    outline2 = result2.get('outline', {})
    print(f"Outline: {outline2.get('title', 'None')}")
    print(f"Sections: {len(outline2.get('sections', []))}")
    print(f"Errors: {len(result2.get('errors', []))}")
    
    print("\n✅ All tests completed!")

# feedback_processor.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from ..models.state_models import OutlineState
import time
import json
from dotenv import load_dotenv

load_dotenv()
def process_user_feedback(state: OutlineState) -> OutlineState:
    """Process user feedback and update outline accordingly"""
    
    feedback = state.get('user_feedback', '')
    if not feedback:
        return state
    
    # Save current version
    _save_version(state)
    
    # Get updated outline via LLM
    updated_outline = _revise_outline_with_feedback(
        current_outline=state.get('outline', {}),
        feedback=feedback,
        keywords=state.get('keywords', {})
    )
    
    if updated_outline:
        state['outline'] = updated_outline
        state['current_version'] = state.get('current_version', 1) + 1
        state['confidence_scores']['feedback_processing'] = 0.85
    else:
        state['errors'] = state.get('errors', [])
        state['errors'].append("Failed to process feedback")
        state['confidence_scores']['feedback_processing'] = 0.3
    
    return state

def _save_version(state: OutlineState):
    """Save current outline to version history"""
    if 'version_history' not in state:
        state['version_history'] = []
    
    state['version_history'].append({
        'version': state.get('current_version', 1),
        'outline': state.get('outline', {}),
        'timestamp': time.time(),
        'feedback': state.get('user_feedback', '')
    })

def _revise_outline_with_feedback(current_outline: dict, feedback: str, keywords: dict) -> dict:
    """Use LLM to revise outline based on feedback"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert content strategist. Revise the given outline based on user feedback.
        
        MAINTAIN:
        - Overall structure and format
        - Primary keyword optimization
        - Professional quality
        
        MODIFY based on feedback:
        - Add/remove/reorder sections
        - Update section titles and descriptions
        - Adjust word counts
        - Modify subsections
        
        Return valid JSON matching the original outline format."""),
        
        ("human", """Current outline:
{current_outline}

Primary keyword: {primary_keyword}
Secondary keywords: {secondary_keywords}

User feedback: {feedback}

Please revise the outline addressing the feedback while maintaining SEO optimization.""")
    ])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    chain = prompt | llm
    
    try:
        result = chain.invoke({
            "current_outline": json.dumps(current_outline, indent=2),
            "primary_keyword": keywords.get('primary', ''),
            "secondary_keywords": ', '.join(keywords.get('secondary', [])),
            "feedback": feedback
        })
        
        # Extract JSON from response
        content = result.content.strip()
        
        # Try to find JSON in the response
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start >= 0 and end > start:
            json_str = content[start:end]
            return json.loads(json_str)
        
        return None
        
    except Exception as e:
        return None

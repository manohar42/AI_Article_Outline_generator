# test_feedback_processor.py

import os
import sys
import json

# Add project root to path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv()

from src.agents.feedback_processor import process_user_feedback

def create_test_state():
    """Create a test OutlineState with existing outline"""
    return {
        "keywords": {
            "primary": "AI in healthcare",
            "secondary": ["machine learning", "telemedicine", "predictive analytics"]
        },
        "outline": {
            "title": "Complete Guide to AI in Healthcare",
            "meta_description": "Comprehensive guide covering AI applications in healthcare",
            "content_type": "ultimate_guide",
            "search_intent": "informational",
            "target_audience": "healthcare professionals",
            "total_word_count": 2500,
            "sections": [
                {
                    "section_id": "introduction",
                    "section_title": "Introduction to AI in Healthcare",
                    "short_description": "Overview of AI applications",
                    "target_keywords": ["AI in healthcare"],
                    "suggested_word_count": 400,
                    "subsections": ["What is AI", "Current Applications"],
                    "research_notes": ["Define AI clearly"]
                },
                {
                    "section_id": "benefits",
                    "section_title": "Benefits of AI in Medicine",
                    "short_description": "Key advantages and improvements",
                    "target_keywords": ["AI benefits", "healthcare automation"],
                    "suggested_word_count": 500,
                    "subsections": ["Improved Diagnostics", "Cost Reduction"],
                    "research_notes": ["Include specific examples"]
                },
                {
                    "section_id": "challenges",
                    "section_title": "Challenges and Limitations",
                    "short_description": "Current obstacles and concerns",
                    "target_keywords": ["AI challenges", "healthcare ethics"],
                    "suggested_word_count": 450,
                    "subsections": ["Privacy Concerns", "Regulatory Issues"],
                    "research_notes": ["Address common concerns"]
                }
            ],
            "faqs": [
                {"question": "Is AI safe in healthcare?", "answer": "When properly implemented..."}
            ]
        },
        "current_version": 1,
        "version_history": [],
        "confidence_scores": {},
        "errors": []
    }

def test_structural_feedback():
    """Test adding a new section based on feedback"""
    print("=== Testing Structural Change ===")
    
    state = create_test_state()
    state['user_feedback'] = "Add a section about AI implementation costs and ROI analysis"
    
    original_sections = len(state['outline']['sections'])
    print(f"Original sections: {original_sections}")
    
    updated_state = process_user_feedback(state)
    
    if 'outline' in updated_state:
        new_sections = len(updated_state['outline']['sections'])
        print(f"Updated sections: {new_sections}")
        
        # Show new/modified sections
        for i, section in enumerate(updated_state['outline']['sections']):
            print(f"  {i+1}. {section.get('section_title', 'Untitled')}")
        
        print(f"Version: {updated_state.get('current_version', 1)}")
        print(f"Confidence: {updated_state.get('confidence_scores', {}).get('feedback_processing', 'N/A')}")
    else:
        print("❌ No outline in result")
        print("Errors:", updated_state.get('errors', []))

def test_content_revision():
    """Test modifying existing section content"""
    print("\n=== Testing Content Revision ===")
    
    state = create_test_state()
    state['user_feedback'] = "Make the benefits section more technical and add specific AI algorithms used in diagnostics"
    
    updated_state = process_user_feedback(state)
    
    if 'outline' in updated_state:
        # Find benefits section
        benefits_section = None
        for section in updated_state['outline']['sections']:
            if 'benefit' in section.get('section_title', '').lower():
                benefits_section = section
                break
        
        if benefits_section:
            print("Updated Benefits Section:")
            print(f"  Title: {benefits_section.get('section_title')}")
            print(f"  Description: {benefits_section.get('short_description')}")
            print(f"  Subsections: {benefits_section.get('subsections', [])}")
        else:
            print("Benefits section not found")
    else:
        print("❌ No outline in result")

def test_section_removal():
    """Test removing a section"""
    print("\n=== Testing Section Removal ===")
    
    state = create_test_state()
    state['user_feedback'] = "Remove the challenges section, I want to focus only on positive aspects"
    
    original_titles = [s['section_title'] for s in state['outline']['sections']]
    print(f"Original sections: {original_titles}")
    
    updated_state = process_user_feedback(state)
    
    if 'outline' in updated_state:
        updated_titles = [s['section_title'] for s in updated_state['outline']['sections']]
        print(f"Updated sections: {updated_titles}")
        
        if len(updated_titles) < len(original_titles):
            print("✅ Section removed successfully")
        else:
            print("⚠️  No sections removed")
    else:
        print("❌ No outline in result")

def test_keyword_focus():
    """Test keyword optimization changes"""
    print("\n=== Testing Keyword Focus ===")
    
    state = create_test_state()
    state['user_feedback'] = "Focus more on 'clinical decision support' keyword and add it to relevant sections"
    
    updated_state = process_user_feedback(state)
    
    if 'outline' in updated_state:
        print("Keyword usage after update:")
        for section in updated_state['outline']['sections']:
            keywords = section.get('target_keywords', [])
            if any('clinical' in kw.lower() for kw in keywords):
                print(f"  {section['section_title']}: {keywords}")
    else:
        print("❌ No outline in result")

def test_version_history():
    """Test version tracking"""
    print("\n=== Testing Version History ===")
    
    state = create_test_state()
    
    # First feedback
    state['user_feedback'] = "Add introduction subsection about AI history"
    state = process_user_feedback(state)
    
    # Second feedback
    state['user_feedback'] = "Make the title more specific to clinical applications"
    state = process_user_feedback(state)
    
    print(f"Current version: {state.get('current_version', 1)}")
    print(f"Version history entries: {len(state.get('version_history', []))}")
    
    for i, version in enumerate(state.get('version_history', [])):
        print(f"  Version {version['version']}: {version['feedback'][:50]}...")

def main():
    """Run all tests"""
    print("🚀 Testing Feedback Processor\n")
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    test_structural_feedback()
    test_content_revision()
    test_section_removal()
    test_keyword_focus()
    test_version_history()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()

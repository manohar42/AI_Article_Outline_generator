# test_keyword_analyzer.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.state_models import OutlineState
from src.agents.keyword_analyzer import analyze_keywords
from src.models.content_models import KeywordData
from dotenv import load_dotenv

load_dotenv()

def test_keyword_analysis():
    # Create test state matching your OutlineState structure
    test_state = {
        "keywords": KeywordData(
            primary="AI in healthcare",
            secondary=[
                "machine learning",
                "telemedicine", 
                "predictive analytics",
                "health informatics",
                "medical imaging",
                "drug discovery",
                "healthcare tools",
                "personalized medicine",
                "robotic surgery",
                "patient monitoring"
            ]
        ),
        "word_count": 2000,
        "content_strategy": {},
        "confidence_scores": {}
    }
    
    print("Testing keyword analysis...")
    print(f"Primary keyword: {test_state['keywords'].primary}")
    print(f"Secondary keywords: {test_state['keywords'].secondary[:3]}...")
    
    try:
        # Run the analysis
        result = analyze_keywords(test_state)
        
        # Print results
        print("\n✅ Analysis completed successfully!")
        print(f"Content Type: {result['content_strategy']['content_type']}")
        print(f"Search Intent: {result['content_strategy']['search_intent']}")
        print(f"Priority Score: {result['content_strategy']['priority_score']}")
        print(f"Confidence Score: {result['confidence_scores']['keyword_analysis']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_keyword_analysis()

# test_serper_agent.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from src.models.state_models import OutlineState
from src.models.content_models import KeywordData
from src.agents.serper_research_agent import serper_research
from dotenv import load_dotenv

load_dotenv()

def test_serper_research():
    """Test the Serper research functionality"""
    
    # Check if API key is available
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("❌ Error: SERPER_API_KEY not found in environment variables")
        print("Add SERPER_API_KEY=your_key_here to your .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    # Create test state
    test_state = {
        "keywords": KeywordData(
            primary="AI in healthcare",
            secondary=[
                "machine learning", "telemedicine", "predictive analytics"
            ]
        ),
        "word_count": 2000,
        "serper_results": [],
        "confidence_scores": {}
    }
    
    print(f"\n🔍 Testing Serper research for: '{test_state['keywords'].primary}'")
    
    try:
        # Run the research
        print("Making API request...")
        result = serper_research(test_state)
        
        # Validate results
        if 'serper_results' not in result:
            print("❌ Error: No serper_results in response")
            return False
            
        serper_data = result['serper_results'][0]
        
        print("\n✅ Research completed successfully!")
        print(f"📊 Results Summary:")
        print(f"   - Organic results: {len(serper_data.get('organic', []))}")
        print(f"   - People Also Ask: {len(serper_data.get('people_also_ask', []))}")
        print(f"   - Related searches: {len(serper_data.get('related_searches', []))}")
        print(f"   - Total results: {serper_data.get('total_results', 0)}")
        print(f"   - Confidence score: {result['confidence_scores'].get('serper_research', 'N/A')}")
        
        # Show sample organic results
        organic = serper_data.get('organic', [])
        if organic:
            print(f"\n📄 Sample Organic Results:")
            for i, result in enumerate(organic[:3]):
                print(f"   {i+1}. {result.get('title', 'No title')}")
                print(f"      URL: {result.get('link', 'No URL')}")
        
        # Show People Also Ask
        paa = serper_data.get('people_also_ask', [])
        if paa:
            print(f"\n❓ People Also Ask:")
            for i, question in enumerate(paa[:3]):
                print(f"   {i+1}. {question.get('question', 'No question')}")
        
        # Show Related searches
        related = serper_data.get('related_searches', [])
        if related:
            print(f"\n🔗 Related Searches:")
            for i, search in enumerate(related[:5]):
                print(f"   {i+1}. {search.get('query', 'No query')}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        print("The API response might not be valid JSON")
        return False
    except KeyError as e:
        print(f"❌ Missing Key Error: {e}")
        print("Expected key not found in API response")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_with_different_keywords():
    """Test with multiple different keywords"""
    test_keywords = [
        "Python programming",
        "best laptop 2024", 
        "how to cook pasta",
        "machine learning tutorial"
    ]
    
    print("\n🧪 Testing with different keywords...")
    
    for keyword in test_keywords:
        print(f"\n--- Testing: {keyword} ---")
        
        test_state = {
            "keywords": KeywordData(primary=keyword, secondary=[]),
            "word_count": 1500,
            "serper_results": [],
            "confidence_scores": {}
        }
        
        try:
            result = serper_research(test_state)
            total_results = result['serper_results'][0].get('total_results', 0)
            confidence = result['confidence_scores'].get('serper_research', 0)
            
            print(f"✅ Success - Total: {total_results}, Confidence: {confidence}")
            
        except Exception as e:
            print(f"❌ Failed - {e}")

if __name__ == "__main__":
    print("🚀 Starting Serper API Tests...\n")
    
    # Run basic test
    success = test_serper_research()
    
    if success:
        # Run additional tests if basic test passes
        test_with_different_keywords()
        print(f"\n🎉 All tests completed!")
    else:
        print(f"\n❌ Basic test failed. Fix issues before running additional tests.")

# src/workflow/test_strategy_graph.py

import os
import sys
import json
import time

# Add project root to path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv()

# Import our working functions
from src.workflows.strategy_graph import generate_outline_from_topic, generate_outline

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["SERPER_API_KEY"]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        raise Exception(f"Missing required environment variables: {', '.join(missing_required)}")
    
    if missing_optional:
        print(f"⚠️  Missing optional variables: {', '.join(missing_optional)} (some features may not work)")
    
    print("✅ Environment variables checked")

def display_results(result, test_name):
    """Display test results in a readable format"""
    print(f"\n📊 {test_name} Results:")
    print("-" * 40)
    
    # Keywords
    keywords = result.get('keywords', {})
    if isinstance(keywords, dict):
        print(f"Keywords: {keywords.get('primary', 'None')}")
        print(f"Secondary: {len(keywords.get('secondary', []))} items")
        print(f"LSI: {len(keywords.get('lsi', []))} items")
    else:
        print(f"Keywords: {keywords}")
    
    # SERP results
    serp_results = result.get('serper_results', [])
    if serp_results and len(serp_results) > 0:
        organic_count = len(serp_results[0].get('organic', []))
        print(f"SERP results: {organic_count} organic results found")
    else:
        print("SERP results: None")
    
    # Competitor analysis
    comp_analysis = result.get('competitor_analysis', {})
    competitors_count = comp_analysis.get('competitors_analyzed', 0)
    print(f"Competitors analyzed: {competitors_count}")
    
    # Content strategy
    content_strategy = result.get('content_strategy', {})
    print(f"Content strategy: {'✅' if content_strategy else '❌'}")
    
    # Outline
    outline = result.get('outline', {})
    if outline:
        print(f"Outline: ✅ '{outline.get('title', 'Untitled')}'")
        print(f"Sections: {len(outline.get('sections', []))}")
        print(f"Target words: {outline.get('total_word_count', 'N/A')}")
        
        # Show first few sections
        sections = outline.get('sections', [])
        if sections:
            print("First 3 sections:")
            for i, section in enumerate(sections):
                title = section.get('section_title', 'Untitled')
                words = section.get('suggested_word_count', '?')
                print(f"  {i+1}. {title} ({words} words)")
    else:
        print("Outline: ❌ Not generated")
    
    # Errors
    errors = result.get('errors', [])
    if errors:
        print(f"Errors: {len(errors)} errors occurred")
        for i, error in enumerate(errors[:3]):
            print(f"  {i+1}. {error}")
    else:
        print("Errors: None")
    
    # Confidence scores
    confidence = result.get('confidence_scores', {})
    if confidence:
        print("Confidence scores:")
        for stage, score in confidence.items():
            print(f"  {stage}: {score}")

def test_topic_to_outline():
    """Test generating outline from a topic"""
    print("\n🧪 TEST 1: Topic to Outline Generation")
    print("="*60)
    
    topic = "Reasons for Heart attack."
    word_count = 2800
    
    print(f"Topic: {topic}")
    print(f"Target word count: {word_count}")
    
    try:
        start_time = time.time()
        result = generate_outline_from_topic(
            topic=topic,
            word_count=word_count,
            user_preferences={"tone": "professional", "audience": "healthcare professionals"}
        )
        end_time = time.time()
        
        print(f"⏱️  Processing time: {end_time - start_time:.2f} seconds")
        
        display_results(result, "Topic to Outline")
        
        # Save results
        output_file = os.path.join(ROOT, "test_topic_to_outline.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"📁 Results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_keywords_to_outline():
    """Test generating outline from existing keywords"""
    print("\n🧪 TEST 2: Keywords to Outline Generation")
    print("="*60)
    
    keywords = {
        'primary': 'AI in healthcare',
        'secondary': [
            'machine learning in medicine',
            'medical AI applications',
            'healthcare automation',
            'clinical decision support',
            'medical image analysis',
            'predictive healthcare analytics'
        ],
        'lsi': [
            'artificial intelligence medicine',
            'healthcare machine learning',
            'clinical AI systems',
            'medical diagnosis AI',
            'patient care automation'
        ]
    }
    
    word_count = 3200
    
    print(f"Primary keyword: {keywords['primary']}")
    print(f"Secondary keywords: {len(keywords['secondary'])} items")
    print(f"LSI keywords: {len(keywords['lsi'])} items")
    print(f"Target word count: {word_count}")
    
    try:
        start_time = time.time()
        result = generate_outline(
            keywords_data=keywords,
            word_count=word_count,
            user_preferences={"tone": "professional", "depth": "comprehensive"}
        )
        end_time = time.time()
        
        print(f"⏱️  Processing time: {end_time - start_time:.2f} seconds")
        
        display_results(result, "Keywords to Outline")
        
        # Save results
        output_file = os.path.join(ROOT, "test_keywords_to_outline.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"📁 Results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_comparison():
    """Compare results from both methods"""
    print("\n🧪 TEST 3: Comparison Analysis")
    print("="*60)
    
    # This is a placeholder - you would run both tests and compare
    print("Run both tests above to compare:")
    print("- Topic-based generation includes keyword research")
    print("- Keywords-based generation skips research phase")
    print("- Both should produce similar quality outlines")

def main():
    """Run all tests"""
    print("🚀 Strategy Graph Test Suite")
    print("="*80)
    
    try:
        # Check environment
        check_environment()
        
        # Run tests
        result1 = test_topic_to_outline()
        result2 = test_keywords_to_outline()
        test_comparison()
        
        # Summary
        print("\n📋 TEST SUMMARY")
        print("="*60)
        
        test1_success = result1 is not None and bool(result1.get('outline'))
        test2_success = result2 is not None and bool(result2.get('outline'))
        
        print(f"1. Topic to Outline: {'✅ PASSED' if test1_success else '❌ FAILED'}")
        print(f"2. Keywords to Outline: {'✅ PASSED' if test2_success else '❌ FAILED'}")
        
        if test1_success and test2_success:
            print("\n🎉 All tests passed! Strategy graph is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
        
        return test1_success and test2_success
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

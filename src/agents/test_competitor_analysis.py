# src/agents/test_competitor_analysis.py
import os
import sys

# # Ensure project root on sys.path so "src" imports work when running as a module
# ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# if ROOT not in sys.path:
#     sys.path.insert(0, ROOT)

from src.agents.competitor_analysis_agent import competitor_analysis

def make_state():
    # Minimal OutlineState-like dict for testing
    return {
        "keywords": {
            "primary": "AI in healthcare",
            "secondary": []
        },
        "serper_results": [{
            "organic": [
                {"link": "https://en.wikipedia.org/wiki/Artificial_intelligence_in_healthcare"},
                {"link": "https://www.healthit.gov/topic/scientific-initiatives/artificial-intelligence-and-machine-learning"},
                {"link": "https://www.nih.gov/news-events/nih-research-matters/ai-healthcare-overview"},
                {"link": "https://www.mayoclinic.org/medical-professionals/digital-health/news/how-ai-is-transforming-health-care/mac-20581034"},
                {"link": "https://www.who.int/health-topics/artificial-intelligence#tab=tab_1"}
            ],
            "people_also_ask": [
                {"question": "How is AI used in healthcare?"},
                {"question": "What are the risks of AI in medicine?"},
                {"question": "Which AI tools are used by doctors?"},
                {"question": "Is AI reliable for diagnosis?"}
            ]
        }],
        "confidence_scores": {}
    }

if __name__ == "__main__":
    state = make_state()
    updated = competitor_analysis(state)

    summary = updated.get("competitor_analysis", {})
    print("competitors_analyzed:", summary.get("competitors_analyzed", 0))
    print("avg_word_count:", summary.get("avg_word_count", 0))
    print("avg_sections:", summary.get("avg_sections", 0))
    print("gaps_found:", len(summary.get("content_gaps", [])))

    data = summary.get("competitor_data", [])
    content_gaps = summary.get("content_gaps",[])
    print("Content Gaps",content_gaps)
    if data:
        sample = data[0]
        for key, value in sample.items():
            print(key, value)
            print("\n\n")
        

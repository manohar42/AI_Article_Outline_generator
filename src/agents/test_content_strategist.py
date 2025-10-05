# src/agents/test_content_strategy.py
import os
import sys


from dotenv import load_dotenv
load_dotenv()  # expects OPENAI_API_KEY for ChatOpenAI

# Import the function under test
from src.agents.content_strategist import generate_content_strategy

# Optional: import your models if needed to build nicer objects
# from src.models.state_models import OutlineState, Keywords

def make_outline_state():
    # Build a dict shaped like OutlineState that your function expects
    return {
        "keywords": {
            "primary": "AI in healthcare",
            "secondary": [
                "machine learning",
                "telemedicine",
                "predictive analytics",
                "health informatics"
            ],
            "lsi": [
                "clinical decision support",
                "medical imaging AI",
                "patient monitoring"
            ]
        },
        "content_strategy": {
            "content_type": "ultimate_guide",
            "search_intent": "informational",
            "target_audience": "healthcare professionals",
            "estimated_word_count": 2200
        },
        "competitor_analysis": {
            "common_topics": [
                "AI diagnostics",
                "telemedicine workflows",
                "privacy and ethics",
                "EMR integration",
                "regulatory considerations"
            ],
            "competitor_data": [],
        },
        "serper_results": [{
            "people_also_ask": [
                {"question": "How is AI used in healthcare?"},
                {"question": "What are the risks of AI in medicine?"},
                {"question": "Is AI accurate for diagnosis?"}
            ]
        }],
        "content_gaps": [
            {"topic": "AI bias in clinical settings"},
            {"topic": "Data interoperability with HL7 FHIR"}
        ],
        "confidence_scores": {},
        "errors": []
    }

def main():
    state = make_outline_state()

    print("Running generate_content_strategy...")
    updated = generate_content_strategy(state)

    # Assert basic keys
    if "outline" not in updated:
        print("❌ No outline produced.")
    else:
        outline = updated["outline"]
        print("✅ Outline produced.")
        # If parser returned Pydantic model converted to dict, it should have these keys
        print("Title:", outline.get("title", "(missing)"))
        print("Type:", outline.get("content_type", "(missing)"))
        print("Intent:", outline.get("search_intent", "(missing)"))
        print("Target audience:", outline.get("target_audience", "(missing)"))
        print("Total words:", outline.get("total_word_count", "(missing)"))

        # Sections preview
        sections = outline.get("sections", [])
        print(f"Sections: {len(sections)}")
        for i, sec in enumerate(sections):
            print(f"  {i+1}. {sec.get('section_title', '(no title)')} "
                  f"- {sec.get('suggested_word_count', 'n/a')} words")

        # FAQs preview
        faqs = outline.get("faqs", [])
        print(f"FAQs: {len(faqs)}")
        for i, faq in enumerate(faqs[:3]):
            print(f"  Q: {faq.get('question','(no)')}")

    # Confidence and errors
    cs = updated.get("confidence_scores", {}).get("content_strategy")
    print("Confidence score:", cs)
    errs = updated.get("errors", [])
    if errs:
        print("Errors:", errs)

if __name__ == "__main__":
    main()

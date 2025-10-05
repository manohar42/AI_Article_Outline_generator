# scoring.py
import json
import re
from typing import List, TypedDict
# pip install openai
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Prefer setting OPENAI_API_KEY in your environment or .env
# setx OPENAI_API_KEY "sk-..."

class LLMIntentResult(TypedDict):
        intent: str            # one of: informational, commercial, navigational
        commercial_strength: int  # 0-3
        rationale: str

class Scorer:

    def __init__(self):
        self.INTENT_KEYWORDS = {
        "commercial": ({"best", "top", "review", "buy", "compare", "cheap"}, 2),
        "informational": ({"how to", "what is", "guide", "tutorial", "tips"}, 1),
        "navigational": ({"login", "sign in", "dashboard", "portal"}, 1),
    }

    def heuristic_score(self, primary: str, secondary: List[str]) -> float:
        BASE, MAX = 4.0, 10.0
        text = primary.lower()
        score = BASE

        # Term matches by category
        for (_, (terms, w)) in self.INTENT_KEYWORDS.items():
            matches = sum(bool(re.search(rf"\b{re.escape(t)}\b", text)) for t in terms)
            score += matches * w

        # Frequency boost
        all_terms = set().union(*(t for t, _ in self.INTENT_KEYWORDS.values()))
        trigger_count = sum(text.count(t) for t in all_terms)
        score += min(trigger_count // 2, 2)

        # Secondary coverage
        uniq = {w.lower() for w in secondary if w}
        length_score = sum(min(len(w.split()), 3) for w in uniq)
        score += min(length_score, 3)

        return max(1.0, min(score, MAX))


    def llm_intent_score(self,keyword: str, client) -> LLMIntentResult:
        schema = {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "enum": ["informational", "commercial", "navigational"]},
                "commercial_strength": {"type": "integer", "minimum": 0, "maximum": 3},
                "rationale": {"type": "string"}
            },
            "required": ["intent", "commercial_strength"]
        }
        schema_text = json.dumps(schema, separators=(",", ":"))  # compact to reduce token use

        system = (
            "Classify the keyword. Respond with ONLY valid JSON conforming to the provided schema. "
            "No extra text."
        )
        user = (
            f"Schema: {schema_text}\n"
            f'Keyword: "{keyword}"\n'
            "Return an object with fields: intent, commercial_strength, rationale."
        )

        # Example with OpenAI-compatible client; set temperature low for determinism
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        text = resp.choices[0].message.content.strip()

        # Validate/parse JSON; on failure, fallback to neutral output
        try:
            obj = json.loads(text)
            # Minimal validation
            if not isinstance(obj.get("commercial_strength"), int):
                raise ValueError("bad type")
            if obj.get("intent") not in {"informational", "commercial", "navigational"}:
                raise ValueError("bad intent")
            return obj  # type: ignore
        except Exception:
            return {"intent": "informational", "commercial_strength": 1, "rationale": "fallback"}  # neutral

    # 3) Fusion
    def final_score(self,primary: str, secondary: List[str]) -> dict:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        h = self.heuristic_score(primary, secondary)
        intent = self.llm_intent_score(primary, client)
        # Map intent into a modest weight; keep heuristic dominant
        intent_weights = {"informational": 0.0, "commercial": 1.0, "navigational": -0.5}
        iw = intent_weights.get(intent["intent"], 0.0)

        # Scale LLM effect: commercial_strength in [0..3] -> [0..3], then weight by 0.4
        llm_component = max(0.0, intent["commercial_strength"]) * 0.4 + iw * 0.3

        fused = 0.6 * h + 0.4 * min(10.0, max(0.0, h + llm_component))
        fused = max(1.0, min(fused, 10.0))

        return {
            "final": round(fused, 2),
            "heuristic": round(h, 2),
            "llm_intent": intent,
        }



if __name__ == "__main__":
    Primary_Keywords= "AI in healthcare"
    Secondary_Keywords = [
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
    # ma = Scorer

    result =Scorer().final_score(primary=Primary_Keywords, secondary=Secondary_Keywords)

    print(result)





# from langchain_openai import ChatOpenAI
# from langchain_core.output_parsers import PydanticOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from src.models.content_models import ContentTypeSearchIntent
# from dotenv import load_dotenv
# import json
# load_dotenv()

# def _get_Content_Type_Search_Intent(primary_keyword: str):
#     llm = ChatOpenAI(model="gpt-4o-mini")
#     parser = PydanticOutputParser(pydantic_object=ContentTypeSearchIntent)

#     # Generate JSON schema via Pydantic V2 API
#     raw_schema_dict = ContentTypeSearchIntent.model_json_schema()  # returns dict
#     raw_schema = json.dumps(raw_schema_dict, indent=2)
#     # Escape braces so ChatPromptTemplate treats them literally
#     escaped_schema = raw_schema.replace("{", "{{").replace("}", "}}")

#     # Build prompt messages
#     messages = [
#         ("system", "Respond **only** with valid JSON matching this schema:"),
#         ("system", escaped_schema),
#         ("system", "Do not include any commentary or extra keys."),
#         ("human", "Primary Keyword: {primary_keyword}")
#     ]

#     prompt = ChatPromptTemplate.from_messages(messages)
#     chain = prompt | llm | parser

#     # Invoke with mapping for the single placeholder
#     result = chain.invoke({"primary_keyword": primary_keyword})
#     return result.ContentType, result.SearchIntent

# if __name__ == "__main__":
#     ct, si = _get_Content_Type_Search_Intent("Heart Attack")
#     print(ct, si)
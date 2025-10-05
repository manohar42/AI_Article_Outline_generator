# serper_research_agent.py (fixed version)
import requests
import os
from typing import List, Dict, Any
import http.client
import json
from src.models.state_models import OutlineState

def serper_research(state: OutlineState) -> OutlineState:
    keywords = state["keywords"]
    primary = keywords.primary

    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": primary
    })
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    # Parse JSON string to dictionary
    results = json.loads(data.decode("utf-8"))  # <-- This was the bug
    
    # Extract results with safe defaults
    organic_results = results.get("organic", [])
    paa_results = results.get("peopleAlsoAsk", [])
    related_searches = results.get("relatedSearches", [])
    
    serper_data = {
        'organic': organic_results,
        'people_also_ask': paa_results,
        'related_searches': related_searches,
        'total_results': len(organic_results) + len(paa_results)
    }

    state['serper_results'] = [serper_data]
    state['confidence_scores']['serper_research'] = 0.9 if serper_data['total_results'] > 10 else 0.7
    
    return state

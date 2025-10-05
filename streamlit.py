# streamlit_app.py

import streamlit as st
import json
import time
from typing import Dict, Any
import os
import sys
from datetime import datetime

# Add project root to path
if os.path.exists("src"):
    sys.path.insert(0, os.getcwd())

from src.workflows.strategy_graph import (
    generate_outline_from_topic,
    generate_outline,
    process_outline_feedback
)

# Page config
st.set_page_config(
    page_title="AI Content Strategy Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'generated_outline' not in st.session_state:
        st.session_state.generated_outline = None
    if 'current_state' not in st.session_state:
        st.session_state.current_state = None
    if 'generation_history' not in st.session_state:
        st.session_state.generation_history = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False

init_session_state()

# Helper functions
def display_keywords(keywords):
    """Display keywords in a formatted way"""
    if isinstance(keywords, dict):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🎯 Primary Keyword")
            st.write(f"**{keywords.get('primary', 'None')}**")
        
        with col2:
            st.subheader("🔗 Secondary Keywords")
            secondary = keywords.get('secondary', [])
            if secondary:
                for kw in secondary[:5]:  # Show first 5
                    st.write(f"• {kw}")
                if len(secondary) > 5:
                    st.write(f"... and {len(secondary) - 5} more")
            else:
                st.write("None")
        
        with col3:
            st.subheader("🧠 LSI Keywords")
            lsi = keywords.get('lsi', [])
            if lsi:
                for kw in lsi[:5]:  # Show first 5
                    st.write(f"• {kw}")
                if len(lsi) > 5:
                    st.write(f"... and {len(lsi) - 5} more")
            else:
                st.write("None")

def display_outline(outline):
    """Display outline in a structured format"""
    if not outline:
        st.error("No outline generated")
        return
    
    st.subheader("📝 Generated Outline")
    
    # Basic info
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Title:** {outline.get('title', 'N/A')}")
        st.write(f"**Content Type:** {outline.get('content_type', 'N/A')}")
        st.write(f"**Search Intent:** {outline.get('search_intent', 'N/A')}")
    
    with col2:
        st.write(f"**Target Audience:** {outline.get('target_audience', 'N/A')}")
        st.write(f"**Total Word Count:** {outline.get('total_word_count', 'N/A')}")
        st.write(f"**Sections:** {len(outline.get('sections', []))}")
    
    # Meta description
    meta_desc = outline.get('meta_description', '')
    if meta_desc:
        st.write(f"**Meta Description:** {meta_desc}")
    
    # Sections
    sections = outline.get('sections', [])
    if sections:
        st.subheader("📋 Sections")
        for i, section in enumerate(sections, 1):
            with st.expander(f"{i}. {section.get('section_title', 'Untitled')} ({section.get('suggested_word_count', '?')} words)"):
                st.write(f"**Description:** {section.get('short_description', 'N/A')}")
                
                # Target keywords
                target_kw = section.get('target_keywords', [])
                if target_kw:
                    st.write(f"**Target Keywords:** {', '.join(target_kw)}")
                
                # Subsections
                subsections = section.get('subsections', [])
                if subsections:
                    st.write("**Subsections:**")
                    for sub in subsections:
                        st.write(f"• {sub}")
                
                # Research notes
                notes = section.get('research_notes', [])
                if notes:
                    st.write("**Research Notes:**")
                    for note in notes:
                        st.write(f"• {note}")

def display_stage_results(result):
    """Display results from each stage of the pipeline"""
    
    # Keywords
    with st.expander("🔍 Keywords Research", expanded=False):
        keywords = result.get('keywords', {})
        display_keywords(keywords)
        
        # Research metadata
        metadata = result.get('research_metadata', {})
        if metadata:
            st.write("**Research Metadata:**")
            st.json(metadata)
    
    # SERP Results
    with st.expander("🌐 SERP Research", expanded=False):
        serp_results = result.get('serper_results', [])
        if serp_results and len(serp_results) > 0:
            organic = serp_results[0].get('organic', [])
            st.write(f"Found **{len(organic)}** organic search results")
            
            if organic:
                st.write("**Top 5 Results:**")
                for i, item in enumerate(organic[:5], 1):
                    st.write(f"{i}. [{item.get('title', 'No title')}]({item.get('link', '#')})")
                    st.write(f"   {item.get('snippet', 'No snippet')[:100]}...")
        else:
            st.write("No SERP results found")
    
    # Competitor Analysis
    with st.expander("🏆 Competitor Analysis", expanded=False):
        comp_analysis = result.get('competitor_analysis', {})
        competitors_count = comp_analysis.get('competitors_analyzed', 0)
        
        if competitors_count > 0:
            st.write(f"**Analyzed {competitors_count} competitors**")
            
            # Content gaps
            gaps = result.get('content_gaps', [])
            if gaps:
                st.write("**Content Gaps Identified:**")
                for gap in gaps[:5]:
                    st.write(f"• {gap.get('topic', 'Unknown')}")
                    st.write(f"  _{gap.get('description', 'No description')}_")
            
            # Common topics
            common_topics = comp_analysis.get('common_topics', [])
            if common_topics:
                st.write("**Common Topics:**")
                st.write(", ".join(common_topics[:10]))
        else:
            st.write("No competitors analyzed")
    
    # Content Strategy
    with st.expander("🎯 Content Strategy", expanded=False):
        content_strategy = result.get('content_strategy', {})
        if content_strategy:
            st.json(content_strategy)
        else:
            st.write("No content strategy generated")
    
    # Errors
    errors = result.get('errors', [])
    if errors:
        with st.expander("⚠️ Errors & Warnings", expanded=False):
            for error in errors:
                st.error(error)
    
    # Confidence Scores
    confidence = result.get('confidence_scores', {})
    if confidence:
        with st.expander("📊 Confidence Scores", expanded=False):
            for stage, score in confidence.items():
                st.write(f"**{stage.replace('_', ' ').title()}:** {score}")

# Main App
def main():
    st.markdown('<h1 class="main-header">🚀 AI Content Strategy Generator</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("## ⚙️ Configuration")
    
    # Check environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")
    
    if not openai_key:
        st.sidebar.error("⚠️ OPENAI_API_KEY not found!")
        st.error("Please set your OPENAI_API_KEY in the environment variables or .env file")
        return
    
    if not serper_key:
        st.sidebar.warning("⚠️ SERPER_API_KEY not found - SERP research may be limited")
    
    st.sidebar.success("✅ API Keys configured")
    
    # Generation mode
    mode = st.sidebar.selectbox(
        "Choose Generation Mode",
        ["Topic-based (with research)", "Keywords-based (no research)"],
        help="Topic-based includes keyword research, Keywords-based uses provided keywords"
    )
    
    # Word count settings
    st.sidebar.markdown("### 📝 Content Settings")
    word_count = st.sidebar.slider("Target Word Count", 1000, 5000, 2500, 100)
    
    # User preferences
    st.sidebar.markdown("### 🎨 Preferences")
    tone = st.sidebar.selectbox("Tone", ["Professional", "Casual", "Academic", "Conversational"])
    audience = st.sidebar.selectbox("Target Audience", 
        ["General audience", "Professionals", "Students", "Experts", "Beginners"])
    
    user_preferences = {
        "tone": tone.lower(),
        "target_audience": audience.lower()
    }
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🎯 Generate Outline", "🔄 Refine with Feedback", "📊 Results & Export"])
    
    with tab1:
        st.markdown('<div class="step-header">Step 1: Generate Your Content Outline</div>', 
                   unsafe_allow_html=True)
        
        if mode == "Topic-based (with research)":
            st.markdown("### 🔍 Enter Your Topic")
            topic = st.text_input(
                "Topic",
                placeholder="e.g., AI in healthcare, Digital marketing trends, Sustainable energy",
                help="Enter the main topic you want to create content about"
            )
            
            if st.button("🚀 Generate Outline from Topic", type="primary", disabled=st.session_state.processing):
                if topic.strip():
                    st.session_state.processing = True
                    
                    with st.status("Generating outline...", expanded=True) as status:
                        st.write("🔍 Starting keyword research...")
                        
                        try:
                            start_time = time.time()
                            result = generate_outline_from_topic(
                                topic=topic.strip(),
                                word_count=word_count,
                                user_preferences=user_preferences
                            )
                            end_time = time.time()
                            
                            st.session_state.current_state = result
                            st.session_state.generated_outline = result.get('outline')
                            
                            # Add to history
                            st.session_state.generation_history.append({
                                'timestamp': datetime.now().isoformat(),
                                'mode': 'topic',
                                'input': topic,
                                'result': result,
                                'processing_time': end_time - start_time
                            })
                            
                            st.write("✅ Outline generated successfully!")
                            status.update(label="✅ Generation complete!", state="complete")
                            
                        except Exception as e:
                            st.error(f"Generation failed: {str(e)}")
                            status.update(label="❌ Generation failed!", state="error")
                        
                        finally:
                            st.session_state.processing = False
                else:
                    st.warning("Please enter a topic")
        
        else:  # Keywords-based
            st.markdown("### 🔑 Enter Your Keywords")
            
            primary_kw = st.text_input(
                "Primary Keyword",
                placeholder="e.g., artificial intelligence healthcare",
                help="Main keyword to target"
            )
            
            secondary_kw = st.text_area(
                "Secondary Keywords (one per line)",
                placeholder="machine learning medicine\nmedical AI applications\nhealthcare automation",
                help="Supporting keywords, one per line"
            )
            
            lsi_kw = st.text_area(
                "LSI Keywords (one per line)",
                placeholder="clinical decision support\nmedical diagnosis AI\npatient care automation",
                help="Latent Semantic Indexing keywords, one per line"
            )
            
            if st.button("🚀 Generate Outline from Keywords", type="primary", disabled=st.session_state.processing):
                if primary_kw.strip():
                    st.session_state.processing = True
                    
                    # Prepare keywords data
                    keywords_data = {
                        'primary': primary_kw.strip(),
                        'secondary': [kw.strip() for kw in secondary_kw.split('\n') if kw.strip()],
                        'lsi': [kw.strip() for kw in lsi_kw.split('\n') if kw.strip()]
                    }
                    
                    with st.status("Generating outline...", expanded=True) as status:
                        st.write("🎯 Processing keywords...")
                        
                        try:
                            start_time = time.time()
                            result = generate_outline(
                                keywords_data=keywords_data,
                                word_count=word_count,
                                user_preferences=user_preferences
                            )
                            end_time = time.time()
                            
                            st.session_state.current_state = result
                            st.session_state.generated_outline = result.get('outline')
                            
                            # Add to history
                            st.session_state.generation_history.append({
                                'timestamp': datetime.now().isoformat(),
                                'mode': 'keywords',
                                'input': keywords_data,
                                'result': result,
                                'processing_time': end_time - start_time
                            })
                            
                            st.write("✅ Outline generated successfully!")
                            status.update(label="✅ Generation complete!", state="complete")
                            
                        except Exception as e:
                            st.error(f"Generation failed: {str(e)}")
                            status.update(label="❌ Generation failed!", state="error")
                        
                        finally:
                            st.session_state.processing = False
                else:
                    st.warning("Please enter at least a primary keyword")
        
        # Display generated outline
        if st.session_state.generated_outline:
            st.markdown("---")
            display_outline(st.session_state.generated_outline)
    
    with tab2:
        st.markdown('<div class="step-header">Step 2: Refine Your Outline</div>', 
                   unsafe_allow_html=True)
        
        if st.session_state.current_state:
            st.markdown("### 💬 Provide Feedback")
            
            feedback = st.text_area(
                "What would you like to change?",
                placeholder="e.g., Add a section about implementation costs, Make the introduction more technical, Remove the challenges section",
                help="Describe what changes you'd like to make to the outline"
            )
            
            if st.button("🔄 Apply Feedback", disabled=st.session_state.processing):
                if feedback.strip():
                    st.session_state.processing = True
                    
                    try:
                        with st.spinner("Processing feedback..."):
                            updated_state = process_outline_feedback(
                                st.session_state.current_state,
                                feedback.strip()
                            )
                            
                            st.session_state.current_state = updated_state
                            st.session_state.generated_outline = updated_state.get('outline')
                            
                            st.success("✅ Feedback applied successfully!")
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"Feedback processing failed: {str(e)}")
                    
                    finally:
                        st.session_state.processing = False
                else:
                    st.warning("Please enter your feedback")
            
            # Version history
            if st.session_state.current_state.get('version_history'):
                st.markdown("### 📝 Version History")
                for i, version in enumerate(st.session_state.current_state['version_history']):
                    st.write(f"**Version {version.get('version', i+1)}:** {version.get('feedback', 'Initial version')[:100]}...")
        
        else:
            st.info("Generate an outline first to provide feedback")
    
    with tab3:
        st.markdown('<div class="step-header">Step 3: Review Results & Export</div>', 
                   unsafe_allow_html=True)
        
        if st.session_state.current_state:
            # Stage-by-stage results
            st.markdown("### 🔍 Pipeline Results")
            display_stage_results(st.session_state.current_state)
            
            # Export options
            st.markdown("### 📥 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 Copy Outline as Text"):
                    outline = st.session_state.generated_outline
                    if outline:
                        text_output = f"# {outline.get('title', 'Untitled')}\n\n"
                        text_output += f"**Meta Description:** {outline.get('meta_description', '')}\n\n"
                        
                        for i, section in enumerate(outline.get('sections', []), 1):
                            text_output += f"## {i}. {section.get('section_title', 'Untitled')}\n"
                            text_output += f"{section.get('short_description', '')}\n\n"
                            
                            subsections = section.get('subsections', [])
                            if subsections:
                                for sub in subsections:
                                    text_output += f"- {sub}\n"
                                text_output += "\n"
                        
                        st.code(text_output, language="markdown")
            
            with col2:
                if st.button("📄 Download JSON"):
                    if st.session_state.current_state:
                        json_str = json.dumps(st.session_state.current_state, indent=2)
                        st.download_button(
                            label="Download Complete Results",
                            data=json_str,
                            file_name=f"outline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
            
            with col3:
                if st.button("📊 View Raw Data"):
                    st.json(st.session_state.current_state)
            
            # Generation history
            if st.session_state.generation_history:
                st.markdown("### 📈 Generation History")
                for i, entry in enumerate(reversed(st.session_state.generation_history)):
                    with st.expander(f"Generation {len(st.session_state.generation_history) - i} - {entry['mode']} - {entry['timestamp'][:19]}"):
                        st.write(f"**Mode:** {entry['mode']}")
                        st.write(f"**Processing Time:** {entry['processing_time']:.2f} seconds")
                        st.write(f"**Input:** {str(entry['input'])[:200]}...")
                        st.write(f"**Errors:** {len(entry['result'].get('errors', []))}")
        
        else:
            st.info("Generate an outline first to see results")

if __name__ == "__main__":
    main()

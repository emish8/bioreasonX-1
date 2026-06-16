import streamlit as st
import sys
from pathlib import Path

# Add project root to path for local module imports
sys.path.append(str(Path(__file__).resolve().parent))

# Import render pages
from frontend.pages.Home import render_home
from frontend.pages.Analysis import render_analysis
from frontend.pages.EvidenceExplorer import render_evidence_explorer
from frontend.pages.ExplainableAI import render_explainable_ai
from frontend.pages.ReportGenerator import render_report_generator

from backend.utils.config import has_gemini_credentials, logger

def main():
    # 1. Config main Streamlit frame
    st.set_page_case = st.set_page_config(
        page_title="BioReason-X | Clinical Intelligence Platform",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Premium styling injections
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Inter:wght@300;400;600;700&display=swap');
            
            /* Global Font Updates */
            html, body, [class*="css"], .stMarkdown {
                font-family: 'Inter', sans-serif;
            }
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Montserrat', sans-serif;
                font-weight: 600;
            }

            /* Custom styling for primary actions button */
            div.stButton > button:first-child {
                background-color: #1A365D;
                color: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #1A365D;
                font-weight: 600;
                transition: all 0.25s ease;
            }
            div.stButton > button:first-child:hover {
                background-color: #2B6CB0;
                border-color: #2B6CB0;
                color: #FFFFFF;
                box-shadow: 0 4px 10px rgba(43, 108, 176, 0.25);
            }
            
            /* Sidebar customizations */
            [data-testid="stSidebar"] {
                background-color: #F7FAFC;
                border-right: 1px solid #E2E8F0;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 3. Sidebar management
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 10px 0;">
            <h2 style="font-family: 'Montserrat', sans-serif; font-size: 1.5rem; color: #1A365D; margin: 0;">🧬 BioReason-X</h2>
            <span style="font-size: 0.8rem; color: #718096; font-weight: 600;">v1.0.0 (Enterprise)</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display environment statuses
    is_live_api = has_gemini_credentials()
    status_label = "Gemini Live API Mode" if is_live_api else "Clinical Simulation Mode"
    status_color = "#319795" if is_live_api else "#DD6B20"
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; padding: 5px; margin: 10px 0; background-color: #EDF2F7; border-radius: 8px;">
            <span style="font-size: 0.8rem; font-weight: 700; color: {status_color};">&bull; {status_label}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Active page tracker in session state
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "🏠 Home Overview"

    # Sidebar Navigation Option list
    nav_options = [
        "🏠 Home Overview",
        "📊 Analysis Dashboard",
        "🔍 Evidence Explorer",
        "🧠 Explainable AI",
        "📄 Report Generator"
    ]
    
    # Render sidebar selections
    selection = st.sidebar.radio(
        "Navigation Menu:",
        options=nav_options,
        index=nav_options.index(st.session_state["active_page"])
    )
    
    st.session_state["active_page"] = selection

    # Sidebar utility: Current target indicator
    if "pipeline_results" in st.session_state:
        current_mut = st.session_state["pipeline_results"].get("mutation_input", "None")
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"🧬 **Current Target:**  \n`{current_mut}`")
        
        if st.sidebar.button("🗑️ Reset Analysis Session", use_container_width=True):
            logger.info("Clearing active pipeline analysis session.")
            st.session_state.pop("pipeline_results", None)
            st.session_state.pop("mutation_query", None)
            st.session_state["active_page"] = "🏠 Home Overview"
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info("Designed for molecular tumor boards and genomics research institutes.")

    # 4. Route views
    if selection == "🏠 Home Overview":
        render_home()
    elif selection == "📊 Analysis Dashboard":
        render_analysis()
    elif selection == "🔍 Evidence Explorer":
        render_evidence_explorer()
    elif selection == "🧠 Explainable AI":
        render_explainable_ai()
    elif selection == "📄 Report Generator":
        render_report_generator()

if __name__ == "__main__":
    main()

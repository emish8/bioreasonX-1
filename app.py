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
                background-color: var(--primary-color, #1A365D);
                color: #FFFFFF;
                border-radius: 8px;
                border: 1px solid var(--primary-color, #1A365D);
                font-weight: 600;
                transition: all 0.25s ease;
            }
            div.stButton > button:first-child:hover {
                background-color: var(--primary-color, #2B6CB0);
                border-color: var(--primary-color, #2B6CB0);
                color: #FFFFFF;
                box-shadow: 0 4px 10px rgba(43, 108, 176, 0.25);
                opacity: 0.9;
            }
            
            /* Sidebar customizations adapting to dark theme */
            [data-testid="stSidebar"] {
                background-color: var(--secondary-background-color);
                border-right: 1px solid var(--border-color, #E2E8F0);
            }

            /* Sidebar Title */
            .sidebar-title {
                font-family: 'Montserrat', sans-serif;
                font-size: 1.5rem;
                color: var(--text-color);
                margin: 0;
            }
            
            /* Home page styles */
            .hero-subtitle {
                font-size: 1.25rem;
                font-weight: 400;
                color: var(--text-color);
                opacity: 0.8;
                margin-top: 10px;
            }
            .analysis-card {
                background-color: var(--secondary-background-color);
                border: 1.5px solid var(--border-color, #E2E8F0);
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            }
            .analysis-card h4 {
                margin-top: 0;
                font-family: 'Montserrat', sans-serif;
                color: var(--text-color);
            }

            /* Evidence Explorer styles */
            .evidence-card {
                background-color: var(--secondary-background-color);
                border: 1px solid var(--border-color, #E2E8F0);
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            }
            .evidence-title {
                margin: 10px 0;
                font-size: 1.15rem;
                font-family: 'Montserrat', sans-serif;
                color: var(--text-color);
            }
            .evidence-abstract {
                font-size: 0.95rem;
                line-height: 1.5;
                color: var(--text-color);
                opacity: 0.8;
                margin-top: 10px;
                font-style: italic;
            }
            .evidence-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
                flex-wrap: wrap;
                gap: 8px;
            }
            .badge {
                font-size: 0.85rem;
                font-weight: 600;
                padding: 4px 10px;
                border-radius: 6px;
            }
            .badge-id {
                font-weight: 700;
                font-size: 0.95rem;
                color: var(--primary-color);
                background-color: rgba(43, 108, 176, 0.15);
            }
            .badge-source {
                color: var(--text-color);
                background-color: rgba(128, 128, 128, 0.15);
            }
            .badge-relevance {
                font-weight: 700;
                color: #319795;
                background-color: rgba(49, 151, 149, 0.15);
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 3. Sidebar management
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 10px 0;">
            <h2 class="sidebar-title">🧬 BioReason-X</h2>
            <span style="font-size: 0.8rem; color: #718096; font-weight: 600;">v1.0.0 (Enterprise)</span>
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

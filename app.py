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
    st.set_page_config(
        page_title="BioReason-X | Clinical Intelligence Platform",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Premium styling injections
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Global Font Updates & Custom Scrollbar */
            html, body, [class*="css"], .stMarkdown {
                font-family: 'Inter', sans-serif;
            }
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Outfit', sans-serif;
                font-weight: 600;
                letter-spacing: -0.5px;
            }
            
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: transparent;
            }
            ::-webkit-scrollbar-thumb {
                background: rgba(128, 128, 128, 0.3);
                border-radius: 10px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(128, 128, 128, 0.5);
            }

            /* Custom styling for primary actions button */
            div.stButton > button:first-child {
                background: linear-gradient(135deg, #1e3a8a, #0d9488) !important;
                color: #FFFFFF !important;
                border-radius: 10px !important;
                border: none !important;
                font-weight: 600 !important;
                padding: 10px 24px !important;
                box-shadow: 0 4px 12px rgba(13, 148, 136, 0.15) !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            div.stButton > button:first-child:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(13, 148, 136, 0.3) !important;
                opacity: 0.95 !important;
            }
            div.stButton > button:first-child:active {
                transform: translateY(0) !important;
            }
            
            /* Sidebar customizations adapting to dark/light theme */
            [data-testid="stSidebar"] {
                background-color: var(--secondary-background-color) !important;
                border-right: 1px solid var(--border-color, rgba(128, 128, 128, 0.15)) !important;
                padding-top: 10px;
            }

            /* Premium Navigation Sidebar Tabs styling */
            div[role="radiogroup"] {
                background-color: transparent !important;
                padding: 0 !important;
                gap: 6px !important;
            }
            div[role="radiogroup"] > label {
                display: none !important; /* Hide Navigation Menu title label */
            }
            div[role="radiogroup"] label[data-baseweb="radio"] {
                background-color: rgba(128, 128, 128, 0.05) !important;
                border: 1px solid rgba(128, 128, 128, 0.1) !important;
                border-radius: 8px !important;
                padding: 12px 16px !important;
                margin-bottom: 4px !important;
                font-weight: 500 !important;
                font-size: 0.95rem !important;
                transition: all 0.25s ease !important;
                cursor: pointer !important;
                color: var(--text-color) !important;
                display: flex !important;
                align-items: center !important;
                width: 100% !important;
            }
            div[role="radiogroup"] label[data-baseweb="radio"]:hover {
                background-color: rgba(128, 128, 128, 0.1) !important;
                transform: translateX(4px);
                border-color: rgba(13, 148, 136, 0.3) !important;
            }
            div[role="radiogroup"] label[data-baseweb="radio"][data-checked="true"] {
                background: linear-gradient(135deg, #1e3a8a, #0d9488) !important;
                color: #FFFFFF !important;
                border-color: transparent !important;
                box-shadow: 0 4px 14px rgba(13, 148, 136, 0.25) !important;
                font-weight: 600 !important;
            }
            div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
                display: none !important; /* Hide standard radio circle icon */
            }
            
            /* Glassmorphism Cards */
            .glass-card {
                background-color: var(--secondary-background-color);
                border: 1px solid var(--border-color, rgba(128, 128, 128, 0.15));
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 20px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
                transition: all 0.3s ease;
            }
            .glass-card:hover {
                box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.08);
                transform: translateY(-2px);
            }
            .glass-card h4 {
                margin-top: 0;
                font-family: 'Outfit', sans-serif;
                color: var(--text-color);
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            /* Custom KPI Metrics */
            .kpi-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 16px;
                margin-bottom: 25px;
            }
            .kpi-card {
                background: var(--secondary-background-color);
                border: 1px solid var(--border-color, rgba(128, 128, 128, 0.15));
                border-radius: 12px;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 16px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
                transition: all 0.3s ease;
            }
            .kpi-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
                border-color: rgba(13, 148, 136, 0.3);
            }
            .kpi-icon {
                font-size: 2.2rem;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 54px;
                height: 54px;
                border-radius: 10px;
                background: rgba(13, 148, 136, 0.1);
            }
            .kpi-details {
                flex-grow: 1;
            }
            .kpi-label {
                font-size: 0.8rem;
                color: #64748B;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 600;
                margin-bottom: 4px;
            }
            .kpi-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--text-color);
                font-family: 'Outfit', sans-serif;
            }
            
            /* Flow stepper style */
            .stepper-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                margin: 20px 0;
                gap: 10px;
            }
            .step-item {
                display: flex;
                align-items: center;
                gap: 8px;
                background: rgba(128, 128, 128, 0.05);
                border: 1px solid rgba(128, 128, 128, 0.1);
                padding: 10px 18px;
                border-radius: 30px;
                font-weight: 500;
                font-size: 0.9rem;
            }
            .step-arrow {
                color: #0d9488;
                font-weight: bold;
                font-size: 1.2rem;
            }

            /* Custom Table Style */
            .custom-table-container {
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid var(--border-color, rgba(128, 128, 128, 0.15));
                margin-top: 15px;
            }
            table.custom-table {
                width: 100%;
                border-collapse: collapse;
                text-align: left;
                font-size: 0.95rem;
            }
            table.custom-table th {
                background-color: rgba(128, 128, 128, 0.08);
                color: var(--text-color);
                font-weight: 600;
                padding: 14px 18px;
                border-bottom: 2px solid var(--border-color, rgba(128, 128, 128, 0.15));
            }
            table.custom-table td {
                padding: 14px 18px;
                border-bottom: 1px solid var(--border-color, rgba(128, 128, 128, 0.15));
                color: var(--text-color);
            }
            table.custom-table tr:hover {
                background-color: rgba(128, 128, 128, 0.03);
            }

            /* Evidence Explorer card overrides */
            .evidence-card {
                background-color: var(--secondary-background-color);
                border: 1px solid var(--border-color, rgba(128, 128, 128, 0.15));
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.01);
                transition: all 0.25s ease;
            }
            .evidence-card:hover {
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.04);
                border-color: rgba(13, 148, 136, 0.25);
            }
            .evidence-title {
                margin: 12px 0 10px 0;
                font-size: 1.2rem;
                font-weight: 600;
                font-family: 'Outfit', sans-serif;
                color: var(--text-color);
            }
            .evidence-abstract {
                font-size: 0.95rem;
                line-height: 1.6;
                color: var(--text-color);
                opacity: 0.85;
                margin-top: 12px;
                font-style: normal;
                padding-left: 14px;
                border-left: 3px solid rgba(13, 148, 136, 0.3);
            }
            .evidence-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
                flex-wrap: wrap;
                gap: 8px;
            }
            .badge {
                font-size: 0.8rem;
                font-weight: 600;
                padding: 5px 12px;
                border-radius: 30px;
                letter-spacing: 0.3px;
            }
            .badge-id {
                font-weight: 700;
                color: #ffffff !important;
                background: linear-gradient(135deg, #1e3a8a, #3b82f6);
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
            }
            .badge-source {
                color: var(--text-color);
                background-color: rgba(128, 128, 128, 0.1);
            }
            .badge-relevance {
                font-weight: 700;
                color: #0d9488;
                background-color: rgba(13, 148, 136, 0.12);
            }
            
            /* Custom progress bar for relevance */
            .relevance-bar-container {
                width: 100%;
                background-color: rgba(128, 128, 128, 0.1);
                border-radius: 4px;
                height: 6px;
                margin-top: 6px;
                overflow: hidden;
            }
            .relevance-bar-fill {
                background: linear-gradient(90deg, #1e3a8a, #0d9488);
                height: 100%;
                border-radius: 4px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 3. Sidebar management
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 15px 0 25px 0; border-bottom: 1px solid rgba(128, 128, 128, 0.15); margin-bottom: 20px;">
            <div style="font-size: 2.2rem; font-weight: 800; font-family: 'Outfit', sans-serif; background: linear-gradient(135deg, #3B82F6, #10B981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1.5px; display: inline-block;">
                BioReason<span style="font-weight: 300;">-X</span>
            </div>
            <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; margin-top: 4px;">
                Clinical Decision Engine
            </div>
            <span style="display: inline-block; font-size: 0.7rem; color: #0D9488; background-color: rgba(13, 148, 136, 0.1); padding: 2px 10px; border-radius: 30px; font-weight: 700; margin-top: 8px;">v1.0 Enterprise</span>
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
        index=nav_options.index(st.session_state["active_page"]),
        key="navigation_menu_radio"
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

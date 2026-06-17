import streamlit as st
import textwrap
from backend.agents.workflow import run_bioreason_pipeline, stream_bioreason_pipeline
from backend.utils.config import logger

def render_home():
    # Hero Title with premium glowing gradient and background panel
    st.markdown(
        textwrap.dedent("""
        <div style="background: linear-gradient(135deg, rgba(30, 58, 138, 0.95), rgba(13, 148, 136, 0.95)); border-radius: 16px; padding: 40px 20px; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05); color: #ffffff;">
            <div style="font-size: 3.5rem; font-weight: 800; font-family: 'Outfit', sans-serif; letter-spacing: -1.5px; margin: 0; line-height: 1;">
                BioReason<span style="font-weight: 300;">-X</span>
            </div>
            <p style="font-size: 1.25rem; font-weight: 400; opacity: 0.9; margin-top: 15px; margin-bottom: 0; font-family: 'Inter', sans-serif; letter-spacing: 0.5px;">
                Mutation &rarr; Mechanism &rarr; Therapy Decision Intelligence
            </p>
        </div>
        
        <style>
            /* Custom Search Box & Inputs styling */
            div[data-testid="stTextInput"] input {
                background-color: var(--secondary-background-color) !important;
                border: 2px solid var(--border-color, rgba(128, 128, 128, 0.2)) !important;
                border-radius: 12px !important;
                padding: 14px 18px !important;
                font-size: 1.1rem !important;
                color: var(--text-color) !important;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.01) !important;
                transition: all 0.25s ease !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: #0d9488 !important;
                box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
            }
            
            /* Styled template buttons as tags/chips */
            div[data-testid="column"] button {
                background-color: rgba(128, 128, 128, 0.05) !important;
                color: var(--text-color) !important;
                border: 1px solid rgba(128, 128, 128, 0.15) !important;
                border-radius: 30px !important;
                padding: 6px 12px !important;
                font-size: 0.85rem !important;
                font-weight: 600 !important;
                transition: all 0.25s ease !important;
            }
            div[data-testid="column"] button:hover {
                background-color: rgba(13, 148, 136, 0.1) !important;
                color: #0d9488 !important;
                border-color: rgba(13, 148, 136, 0.3) !important;
                transform: translateY(-1px) !important;
            }
            
            /* Custom step cards */
            .step-card {
                background: var(--secondary-background-color);
                border: 1px solid var(--border-color, rgba(128, 128, 128, 0.15));
                border-radius: 10px;
                padding: 14px 18px;
                margin-bottom: 12px;
                display: flex;
                align-items: flex-start;
                gap: 14px;
                transition: all 0.25s ease;
            }
            .step-card:hover {
                border-color: rgba(13, 148, 136, 0.25);
                transform: translateX(4px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
            }
            .step-num {
                background: linear-gradient(135deg, #1e3a8a, #0d9488);
                color: #ffffff;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 0.85rem;
                flex-shrink: 0;
            }
            .step-title {
                font-weight: 600;
                color: var(--text-color);
                margin-bottom: 2px;
            }
            .step-desc {
                font-size: 0.88rem;
                color: var(--text-color);
                opacity: 0.8;
            }
        </style>
        """),
        unsafe_allow_html=True
    )

    # Grid columns
    col1, col2 = st.columns([2, 3], gap="large")

    with col1:
        # Form box styled with glassmorphism border
        st.markdown(
            textwrap.dedent("""
            <div class="glass-card">
                <h4>🧬 Analyze Genomic Variant</h4>
                <p style="font-size: 0.9rem; opacity: 0.8; margin-top: -5px; margin-bottom: 15px;">
                    Input a target mutation or pick a clinical case study template below to run the multi-agent reasoning graph.
                </p>
            </div>
            """), 
            unsafe_allow_html=True
        )

        # Main Input
        mutation_input = st.text_input(
            "Enter genomic mutation query (e.g. HGVS or amino acid variant):",
            value=st.session_state.get("mutation_query", ""),
            placeholder="e.g. BRCA1 c.5266dupC",
            key="main_input",
            label_visibility="collapsed"
        )
        
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        
        # Placeholder for the status view
        status_placeholder = st.empty()
        
        # Action button
        run_analysis = st.button("🚀 Analyze Mutation", use_container_width=True)

        st.markdown("<hr style='margin: 25px 0 20px 0; opacity: 0.15;'/>", unsafe_allow_html=True)
        
        # Predefined examples
        st.write("📋 **Select a clinical template:**")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("BRCA1", use_container_width=True, help="BRCA1 c.5266dupC"):
                st.session_state["mutation_query"] = "BRCA1 c.5266dupC"
                st.rerun()
        with c2:
            if st.button("EGFR", use_container_width=True, help="EGFR L858R"):
                st.session_state["mutation_query"] = "EGFR L858R"
                st.rerun()
        with c3:
            if st.button("BRAF", use_container_width=True, help="BRAF V600E"):
                st.session_state["mutation_query"] = "BRAF V600E"
                st.rerun()

    with col2:
        st.markdown("### 🧬 Platform Overview")
        st.markdown(
            """
            BioReason-X is an enterprise-grade multi-agent clinical decision support engine. 
            Unlike traditional keyword searches or standard RAG retrievers, BioReason-X utilizes a 
            **LangGraph Multi-Agent Orchestrator** to analyze genomic variations, trace biological pathway cascades, 
            retrieve validated literature, target potential therapies, and produce consolidated reports.
            """
        )

        st.markdown("#### 🛠️ Analysis Core Steps")
        
        steps = [
            ("1", "Mutation Interpretation", "Identifies mutation structure, type, and pathogenicity classification."),
            ("2", "Gene & Protein Mapping", "Maps spatial protein domains, active binding residues, and kinase sites."),
            ("3", "Pathway Disruption Analysis", "Traces cascade consequences on cellular networks and downstream cascades."),
            ("4", "Literature RAG Matching", "Performs semantic vector searches against clinical registries & medical publications."),
            ("5", "Targeted Therapy Guidelines", "Recommends FDA approved & off-label targeted drugs and synthetic lethal options."),
            ("6", "Validation & Clinical Auditing", "Screens findings for clinical proof, logical inconsistencies, and contradictions."),
            ("7", "Consensus Clinical Brief", "Synthesizes multi-agent findings into a certified diagnostic summary.")
        ]
        
        for num, title, desc in steps:
            st.markdown(
                textwrap.dedent(f"""
                <div class="step-card">
                    <div class="step-num">{num}</div>
                    <div>
                        <div class="step-title">{title}</div>
                        <div class="step-desc">{desc}</div>
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

    # Trigger logic
    if run_analysis or (st.session_state.get("mutation_query") and "pipeline_results" not in st.session_state):
        query_to_run = mutation_input if run_analysis else st.session_state.get("mutation_query")
        
        if query_to_run:
            with status_placeholder.status("Executing Multi-Agent Clinical Analysis (LangGraph)...", expanded=True) as status_bar:
                try:
                    logger.info(f"Triggering analysis for {query_to_run} from Home view.")
                    
                    agent_names = {
                        "mutation_agent": "🧬 Interpreting Mutation Variant...",
                        "gene_agent": "🔬 Mapping Gene & Protein Impact...",
                        "pathway_agent": "🔄 Analyzing Pathway Disruption...",
                        "literature_agent": "📚 Retrieving Literature Evidence (RAG)...",
                        "therapy_agent": "💊 Formulating Targeted Therapy Guidelines...",
                        "validation_agent": "🛡️ Verifying Consensus & Fact-Checking...",
                        "consensus_agent": "📝 Synthesizing Clinical Decision Report..."
                    }
                    
                    results = None
                    for node_name, state in stream_bioreason_pipeline(query_to_run):
                        if node_name in agent_names:
                            st.write(agent_names[node_name])
                        elif node_name == "complete":
                            results = state
                            
                    if results:
                        st.session_state["pipeline_results"] = results
                        st.session_state["mutation_query"] = query_to_run
                        status_bar.update(label="Analysis complete!", state="complete", expanded=False)
                        st.success("Analysis complete!")
                        st.session_state["active_page"] = "📊 Analysis Dashboard"
                        st.rerun()
                except Exception as e:
                    status_bar.update(label="Analysis failed!", state="error", expanded=True)
                    st.error(f"Error executing analysis pipeline: {e}")
                    logger.exception(e)
        else:
            st.warning("Please enter a valid mutation string or select a template.")

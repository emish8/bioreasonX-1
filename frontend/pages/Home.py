import streamlit as st
from backend.agents.workflow import run_bioreason_pipeline
from backend.utils.config import logger

def render_home():
    # Hero Title with gradient style using HTML/CSS
    st.markdown(
        """
        <div style="text-align: center; padding: 20px 0px 40px 0px;">
            <h1 style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 3.2rem; margin: 0; background: linear-gradient(135deg, #1A365D, #319795); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                BioReason-X
            </h1>
            <p style="font-size: 1.25rem; font-weight: 400; color: #4A5568; margin-top: 10px;">
                Mutation &rarr; Mechanism &rarr; Therapy Intelligence Platform
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Grid columns
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
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
            "**1. Mutation Interpretation**: Identifies mutation structure & pathogenicity.",
            "**2. Gene & Protein Mapping**: Maps spatial domain disruptions & active kinase sites.",
            "**3. Pathway Disruption Analysis**: Traces cellular signal cascade consequences.",
            "**4. Literature RAG Matching**: Performs deep search against clinical registries & abstracts.",
            "**5. Targeted Therapy Prescriptions**: Recommends FDA approved & off-label targeted drugs.",
            "**6. Evidence Validation & Auditing**: Screens conclusions for inconsistencies & clinical proof.",
            "**7. Consensus Synthesis**: Blends findings into a unified clinical brief."
        ]
        for step in steps:
            st.markdown(step)

    with col2:
        # Form box styled with glassmorphism border
        st.markdown(
            """
            <div style="background-color: #F7FAFC; border: 1.5px solid #E2E8F0; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <h4 style="margin-top: 0; font-family: 'Montserrat', sans-serif; color: #1A365D;">Analyze Genomic Variant</h4>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Main Input
        mutation_input = st.text_input(
            "Enter genomic mutation query (e.g. HGVS or amino acid variant):",
            value=st.session_state.get("mutation_query", ""),
            placeholder="e.g. BRCA1 c.5266dupC",
            key="main_input"
        )
        
        # Action button
        run_analysis = st.button("🚀 Analyze Mutation", use_container_width=True)

        st.markdown("---")
        
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

    # Trigger logic
    if run_analysis or (st.session_state.get("mutation_query") and "pipeline_results" not in st.session_state):
        query_to_run = mutation_input if run_analysis else st.session_state.get("mutation_query")
        
        if query_to_run:
            with st.spinner("Executing Multi-Agent Clinical Analysis (LangGraph)..."):
                try:
                    logger.info(f"Triggering analysis for {query_to_run} from Home view.")
                    results = run_bioreason_pipeline(query_to_run)
                    st.session_state["pipeline_results"] = results
                    st.session_state["mutation_query"] = query_to_run
                    st.success("Analysis complete!")
                    st.session_state["active_page"] = "📊 Analysis Dashboard"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error executing analysis pipeline: {e}")
                    logger.exception(e)
        else:
            st.warning("Please enter a valid mutation string or select a template.")

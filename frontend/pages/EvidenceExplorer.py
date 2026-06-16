import streamlit as st

def render_evidence_explorer():
    st.markdown("## 🔍 Evidence Explorer")
    st.markdown(
        """
        Browse and critique scientific evidence gathered by the **Literature Intelligence Agent** 
        via RAG matching. Papers, clinical trials, and path structures are ranked by semantic similarity index.
        """
    )

    if "pipeline_results" not in st.session_state:
        st.info("No active analysis. Please submit a mutation query on the Home page.")
        return

    results = st.session_state["pipeline_results"]
    evidence = results.get("literature_evidence", [])

    if not evidence:
        st.write("No matching scientific evidence was retrieved for the current mutation variant.")
        return

    # Render each publication
    for i, doc in enumerate(evidence, start=1):
        doc_id = doc.get("id", f"REF-{i}")
        title = doc.get("title", "Untitled Publication")
        abstract = doc.get("abstract", "")
        source = doc.get("source", "Unknown Database")
        category = doc.get("category", "General Bio-Medical")
        score = doc.get("relevance_score", 0.0)

        # Style box matching clinical aesthetics
        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-weight: 700; font-size: 0.95rem; color: #2B6CB0; background-color: #EBF8FF; padding: 4px 10px; border-radius: 6px;">
                        {doc_id}
                    </span>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #2D3748; background-color: #EDF2F7; padding: 4px 10px; border-radius: 6px;">
                        Source: {source} ({category})
                    </span>
                    <span style="font-size: 0.85rem; font-weight: 700; color: #319795; background-color: #E6FFFA; padding: 4px 10px; border-radius: 6px;">
                        Relevance: {score:.2f}
                    </span>
                </div>
                <h4 style="margin: 10px 0; font-size: 1.15rem; font-family: 'Montserrat', sans-serif; color: #1A365D;">
                    {title}
                </h4>
                <p style="font-size: 0.95rem; line-height: 1.5; color: #4A5568; margin-top: 10px; font-style: italic;">
                    "{abstract}"
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

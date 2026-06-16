import streamlit as st
import re

def get_reference_link(doc_id: str) -> str:
    """Resolves publication/database IDs into clickable direct URLs."""
    doc_id = doc_id.strip()
    if doc_id.startswith("PMID-"):
        pmid = doc_id.replace("PMID-", "")
        return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    elif doc_id.startswith("CLINVAR-"):
        clinvar_id = doc_id.replace("CLINVAR-", "")
        match = re.search(r'\d+', clinvar_id)
        if match:
            var_id = int(match.group(0))
            return f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{var_id}/"
        return f"https://www.ncbi.nlm.nih.gov/clinvar/?term={clinvar_id}"
    elif doc_id.startswith("REACTOME-"):
        reactome_id = doc_id.replace("REACTOME-", "")
        return f"https://reactome.org/content/detail/{reactome_id}"
    elif doc_id.startswith("DRUGBANK-"):
        drugbank_id = doc_id.replace("DRUGBANK-", "")
        return f"https://go.drugbank.com/drugs/{drugbank_id}"
    return None

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

        link = get_reference_link(doc_id)
        if link:
            id_html = f'<a href="{link}" target="_blank" class="badge badge-id" style="text-decoration: none;">{doc_id} 🔗</a>'
        else:
            id_html = f'<span class="badge badge-id">{doc_id}</span>'

        # Style box matching clinical aesthetics
        st.markdown(
            f"""
            <div class="evidence-card">
                <div class="evidence-meta">
                    {id_html}
                    <span class="badge badge-source">
                        Source: {source} ({category})
                    </span>
                    <span class="badge badge-relevance">
                        Relevance: {score:.2f}
                    </span>
                </div>
                <h4 class="evidence-title">
                    {title}
                </h4>
                <p class="evidence-abstract">
                    "{abstract}"
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


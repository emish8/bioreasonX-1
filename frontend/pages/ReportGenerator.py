import streamlit as st
from backend.utils.pdf_generator import generate_biomedical_pdf
from backend.utils.doc_generator import generate_biomedical_docx, HAS_DOCX
from backend.utils.config import logger

def render_report_generator():
    st.markdown("## 📄 Medical Report Generator")
    st.markdown(
        """
        Download structured, clinical-grade medical reports compiling all mutations, 
        mechanism descriptions, pathway associations, literature citations, and therapy guides.
        """
    )

    if "pipeline_results" not in st.session_state:
        st.info("No active analysis. Please submit a mutation query on the Home page.")
        return

    results = st.session_state["pipeline_results"]
    mutation_query = results.get("mutation_input", "unknown_variant")
    safe_filename = "".join([c if c.isalnum() else "_" for c in mutation_query])

    # Left and right layouts for generation trigger buttons
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔴 PDF clinical dossier")
        st.write("Generates styled PDF containing custom header titles, tabular mappings, and full citations.")
        
        try:
            pdf_bytes = generate_biomedical_pdf(results)
            st.download_button(
                label="📥 Download Clinical PDF Report",
                data=pdf_bytes,
                file_name=f"BioReasonX_Report_{safe_filename}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error compiling PDF file: {e}")
            logger.exception(e)

    with col2:
        st.markdown("### 🔵 Microsoft Word (DOCX)")
        st.write("Generates customizable Word document using standard medical templates and table styles.")
        
        if HAS_DOCX:
            try:
                docx_bytes = generate_biomedical_docx(results)
                st.download_button(
                    label="📥 Download Word DOCX Report",
                    data=docx_bytes,
                    file_name=f"BioReasonX_Report_{safe_filename}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error compiling DOCX file: {e}")
                logger.exception(e)
        else:
            st.warning("Microsoft Word report generation is disabled because `python-docx` is not installed.")

    st.markdown("---")

    # Document Preview section
    st.markdown("### 🔎 Executive Report Live Preview")
    
    consensus = results.get("consensus", {})
    mutation_details = results.get("mutation_details", {})
    
    st.markdown(
        f"""
        **TARGET VARIANT:** `{mutation_query}`  
        **GENE:** `{mutation_details.get("gene", "N/A")}`  
        **MUTATION TYPE:** {mutation_details.get("mutation_type", "N/A")}  
        **CLINICAL SIGNIFICANCE:** {mutation_details.get("clinical_significance", "N/A")}  
        **CONSENSUS CONFIDENCE INDEX:** {consensus.get("confidence_score", "N/A")}%  
        
        ---
        
        #### Executive Summary:
        {consensus.get("final_findings", "N/A")}
        
        #### Protein Disruption Summary:
        {results.get("protein_impact", "N/A")}
        
        #### Pathways Affected:
        {results.get("pathway_reasoning", {}).get("pathway_reasoning", "N/A")}
        
        #### Final Clinical Recommendation:
        {consensus.get("final_recommendation", "N/A")}
        """
    )

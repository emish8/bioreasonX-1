import streamlit as st
import pandas as pd
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

    # Page-specific preview styles
    st.markdown(
        """
        <style>
            .doc-preview-sheet {
                background-color: #FFFFFF !important;
                color: #0F172A !important;
                border: 1.5px solid #E2E8F0 !important;
                border-radius: 8px !important;
                padding: 40px 35px !important;
                box-shadow: 0 8px 30px rgba(0,0,0,0.06) !important;
                max-width: 850px;
                margin: 20px auto;
                font-family: 'Inter', sans-serif;
            }
            .doc-preview-sheet h1, .doc-preview-sheet h2, .doc-preview-sheet h3, .doc-preview-sheet h4 {
                color: #0F172A !important;
                font-family: 'Outfit', sans-serif !important;
            }
            .doc-preview-header {
                border-bottom: 3px double #0F172A;
                padding-bottom: 15px;
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
            }
            .doc-section-title {
                border-bottom: 1px solid #E2E8F0;
                padding-bottom: 4px;
                margin-top: 25px;
                margin-bottom: 10px;
                font-weight: 700;
                color: #1E3A8A !important;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.9rem;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    results = st.session_state["pipeline_results"]
    mutation_query = results.get("mutation_input", "unknown_variant")
    safe_filename = "".join([c if c.isalnum() else "_" for c in mutation_query])

    # Left and right layouts for generation trigger buttons
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            <div class="glass-card" style="margin-bottom: 10px; min-height: 230px;">
                <div style="font-size: 1.3rem; font-weight: 700; color: #DC2626; display: flex; align-items: center; gap: 8px;">
                    🔴 PDF Clinical Dossier
                </div>
                <p style="font-size: 0.92rem; opacity: 0.85; margin-top: 8px; line-height: 1.5;">
                    Generate and download a beautifully styled PDF clinical dossier. Features official letterheads, custom page dividers, formatted targeted therapy matrices, and verified RAG literature citations.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
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
        st.markdown(
            """
            <div class="glass-card" style="margin-bottom: 10px; min-height: 230px;">
                <div style="font-size: 1.3rem; font-weight: 700; color: #2563EB; display: flex; align-items: center; gap: 8px;">
                    🔵 Microsoft Word (DOCX)
                </div>
                <p style="font-size: 0.92rem; opacity: 0.85; margin-top: 8px; line-height: 1.5;">
                    Generate and export an editable Microsoft Word (DOCX) dossier. Formatted with professional paragraph alignments, standard clinical template structures, and border-accented data tables.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
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

    st.markdown("<hr style='margin: 30px 0; opacity: 0.15;'/>", unsafe_allow_html=True)

    # Document Preview section
    st.markdown("### 🔎 Executive Report Live Preview")
    
    consensus = results.get("consensus", {})
    mutation_details = results.get("mutation_details", {})
    
    st.markdown(
        f"""
        <div class="doc-preview-sheet">
            <div class="doc-preview-header">
                <div>
                    <div style="font-size: 1.6rem; font-weight: 800; letter-spacing:-1px;">BIOREASON<span style="font-weight:300;">-X</span></div>
                    <div style="font-size: 0.7rem; color: #64748B; letter-spacing: 1.5px; text-transform: uppercase; font-weight:700; margin-top:2px;">Clinical Intelligence Report</div>
                </div>
                <div style="text-align: right; font-size: 0.8rem; color: #64748B; line-height: 1.4;">
                    <strong>Dossier ID:</strong> BRX-{safe_filename[:8].upper()}<br/>
                    <strong>Date:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d')}
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; background: #F8FAFC; padding: 15px; border-radius: 6px; border: 1px solid #E2E8F0; font-size: 0.88rem;">
                <div>
                    <strong>Target Variant:</strong> <code>{mutation_query}</code><br/>
                    <strong>Gene Association:</strong> <code>{mutation_details.get("gene", "N/A")}</code>
                </div>
                <div>
                    <strong>Mutation Type:</strong> {mutation_details.get("mutation_type", "N/A")}<br/>
                    <strong>Clinical Significance:</strong> {mutation_details.get("clinical_significance", "N/A")}
                </div>
            </div>

            <div class="doc-section-title">Consensus Confidence Index</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #0D9488; margin-bottom: 15px;">
                {consensus.get("confidence_score", "N/A")}% Match Credibility Score
            </div>
            
            <div class="doc-section-title">Executive Summary</div>
            <p style="font-size: 0.9rem; line-height: 1.6; margin: 0;">
                {consensus.get("final_findings", "N/A")}
            </p>
            
            <div class="doc-section-title">Protein Disruption Summary</div>
            <p style="font-size: 0.9rem; line-height: 1.6; margin: 0;">
                {results.get("protein_impact", "N/A")}
            </p>
            
            <div class="doc-section-title">Pathways Affected</div>
            <p style="font-size: 0.9rem; line-height: 1.6; margin: 0;">
                {results.get("pathway_reasoning", {}).get("pathway_reasoning", "N/A")}
            </p>
            
            <div class="doc-section-title">Final Clinical Recommendation</div>
            <p style="font-size: 0.9rem; line-height: 1.6; margin: 0; font-weight: 600; color: #1E3A8A;">
                {consensus.get("final_recommendation", "N/A")}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

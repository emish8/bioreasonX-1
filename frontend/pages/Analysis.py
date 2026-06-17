import streamlit as st
import pandas as pd
import textwrap

def render_analysis():
    st.markdown("## 📊 Clinical Analysis Dashboard")

    if "pipeline_results" not in st.session_state:
        st.info("No active analysis. Please submit a mutation query on the Home page.")
        return

    st.info("💡 **Looking for the Reasoning Graph?** Navigate to the **🧠 Explainable AI** tab in the sidebar for a visual step-by-step trace and an interactive guide designed for non-experts!")

    results = st.session_state["pipeline_results"]
    
    mutation_query = results.get("mutation_input", "N/A")
    mutation_details = results.get("mutation_details", {})
    protein_impact = results.get("protein_impact", "N/A")
    pathway_reasoning = results.get("pathway_reasoning", {})
    consensus = results.get("consensus", {})
    therapies = results.get("therapies", [])
    validation = results.get("validation", {})
    
    gene = mutation_details.get("gene", "N/A")
    mutation_type = mutation_details.get("mutation_type", "N/A")
    clin_sig = mutation_details.get("clinical_significance", "N/A")
    conf_score = consensus.get("confidence_score", 0.0)

    # 1. Custom HTML KPI Grid
    kpi_html = textwrap.dedent(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-icon">🧬</div>
            <div class="kpi-details">
                <div class="kpi-label">Target Gene</div>
                <div class="kpi-value">{gene}</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🔬</div>
            <div class="kpi-details">
                <div class="kpi-label">Variant Query</div>
                <div class="kpi-value">{mutation_query}</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">⚕️</div>
            <div class="kpi-details">
                <div class="kpi-label">Clinical Class</div>
                <div class="kpi-value" style="font-size: 1.15rem; font-weight:600;">{clin_sig}</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-details">
                <div class="kpi-label">Confidence Index</div>
                <div class="kpi-value">{conf_score}%</div>
            </div>
        </div>
    </div>
    """)
    st.markdown(kpi_html, unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="medium")

    with col_left:
        # Card 1: Mutation Summary
        st.markdown(
            textwrap.dedent(f"""
            <div class="glass-card">
                <h4>🧬 Variant Characterization</h4>
                <div style="line-height: 1.8; font-size: 0.95rem;">
                    <strong>Target String:</strong> <code style="color: #0d9488; font-size: 0.95rem; background: rgba(13, 148, 136, 0.06); padding: 2px 6px; border-radius: 4px;">{mutation_query}</code><br/>
                    <strong>Gene Association:</strong> <code style="color: #1e3a8a; font-size: 0.95rem; background: rgba(30, 58, 138, 0.06); padding: 2px 6px; border-radius: 4px;">{gene}</code><br/>
                    <strong>Structural Variant Type:</strong> {mutation_type}<br/>
                    <strong>Significance Tag:</strong> <span style="background: rgba(13, 148, 136, 0.1); color: #0d9488; padding: 2px 8px; border-radius: 30px; font-weight: 600; font-size: 0.85rem;">{clin_sig}</span><br/>
                    <strong>Pathogenicity Confidence:</strong> {mutation_details.get('confidence_score', 'N/A')}%
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        # Card 2: Protein Disruption
        st.markdown(
            textwrap.dedent(f"""
            <div class="glass-card">
                <h4>🔬 Protein Disruption Mapping</h4>
                <p style="font-size: 0.95rem; line-height: 1.6; margin: 0; opacity: 0.95;">
                    {protein_impact}
                </p>
            </div>
            """),
            unsafe_allow_html=True
        )

        # Card 3: Pathway Reasoning with visual stepper flowchart
        p_text = pathway_reasoning.get("pathway_reasoning", "N/A")
        p_list = pathway_reasoning.get("affected_pathways", [])
        
        stepper_html = ""
        if p_list:
            stepper_html = '<div class="stepper-container">'
            for idx, p in enumerate(p_list):
                stepper_html += f'<div class="step-item"><span style="color: #0d9488; font-weight: 700;">{idx+1}.</span> {p}</div>'
                if idx < len(p_list) - 1:
                    stepper_html += '<div class="step-arrow">&rarr;</div>'
            stepper_html += '</div>'
            
        st.markdown(
            textwrap.dedent(f"""
            <div class="glass-card">
                <h4>🔄 Pathway Cascade Disruption</h4>
                <p style="font-size: 0.95rem; line-height: 1.6; opacity: 0.95;">{p_text}</p>
                {f'<div style="margin-top: 15px; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; color: #64748B; letter-spacing: 0.5px;">Affected Pathway Steps:</div>' if p_list else ''}
                {stepper_html}
                <div style="margin-top: 15px; border-top: 1px solid rgba(128, 128, 128, 0.1); padding-top: 12px; font-size: 0.95rem;">
                    <strong>Primary Downstream Effect:</strong> <span style="font-weight: 500;">{pathway_reasoning.get('downstream_effects', 'N/A')}</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

    with col_right:
        # Card 4: Disease Associations
        diseases = consensus.get("disease_associations", [])
        disease_html = ""
        if diseases:
            for dis in diseases:
                disease_html += f'<div style="background: rgba(229, 62, 62, 0.05); color: #E53E3E; border: 1px solid rgba(229, 62, 62, 0.12); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; font-weight: 600; font-size: 0.9rem; display: inline-block; margin-right: 8px;">🏥 {dis}</div>'
        else:
            disease_html = '<p style="color: #64748B; font-style: italic; margin: 0;">No direct disease connections registered.</p>'

        st.markdown(
            textwrap.dedent(f"""
            <div class="glass-card">
                <h4>🏥 Associated Malignancies</h4>
                <div style="margin-top: 10px;">
                    {disease_html}
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        # Card 5: Validation Audit Summary
        v_score = validation.get("validation_score", 0.0)
        is_valid = validation.get("is_valid", False)
        status_label = 'Passed ✅' if is_valid else 'Flagged ⚠️'
        status_color = '#0d9488' if is_valid else '#ED8936'
        status_bg = 'rgba(13, 148, 136, 0.1)' if is_valid else 'rgba(237, 137, 54, 0.1)'
        
        st.markdown(
            textwrap.dedent(f"""
            <div class="glass-card">
                <h4>🛡️ Clinical Evidence Verification</h4>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; background: rgba(128, 128, 128, 0.03); padding: 12px 18px; border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.1);">
                    <div>
                        <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Audit Score</div>
                        <div style="font-size: 1.6rem; font-weight: 700; color: #1e3a8a;">{v_score}%</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Audited Status</div>
                        <span style="display: inline-block; font-size: 0.9rem; font-weight: 700; color: {status_color}; background-color: {status_bg}; padding: 4px 12px; border-radius: 20px; margin-top: 4px;">{status_label}</span>
                    </div>
                </div>
                <div style="font-size: 0.95rem; line-height: 1.7; opacity: 0.95;">
                    <strong>Contradiction Detected:</strong> <span style="font-weight: 600; color: {'#E53E3E' if validation.get('contradiction_detected', False) else '#0d9488'};">{'Yes ⚠️' if validation.get('contradiction_detected', False) else 'No'}</span><br/>
                    <strong style="display: block; margin-top: 8px;">Audit Notes:</strong>
                    <em style="color: var(--text-color); opacity: 0.85;">{validation.get('verification_details', 'N/A')}</em>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        # Card 6: Executive Findings Summary
        st.markdown(
            textwrap.dedent(f"""
            <div class="glass-card">
                <h4>📝 Executive Clinical Findings</h4>
                <p style="font-size: 0.95rem; line-height: 1.6; opacity: 0.95; margin: 0;">
                    {consensus.get("final_findings", "N/A")}
                </p>
            </div>
            """),
            unsafe_allow_html=True
        )

    st.markdown("<hr style='margin: 30px 0; opacity: 0.15;'/>", unsafe_allow_html=True)

    # 3. Custom Styled Therapy Suggestions Table at the bottom
    st.markdown("### 💊 Targeted Therapy Guidance")
    if therapies:
        table_rows = ""
        for therapy in therapies:
            drug = therapy.get("drug", "N/A")
            drug_class = therapy.get("drug_class", "N/A")
            rationale = therapy.get("rationale", "N/A")
            ev_level = therapy.get("evidence_level", "N/A")
            
            # Color levels coding
            badge_color = "#3b82f6"
            bg_color = "rgba(59, 130, 246, 0.1)"
            ev_str = str(ev_level).upper()
            if any(x in ev_str for x in ["1", "A"]):
                badge_color = "#0d9488"
                bg_color = "rgba(13, 148, 136, 0.1)"
            elif any(x in ev_str for x in ["2", "B"]):
                badge_color = "#3b82f6"
                bg_color = "rgba(59, 130, 246, 0.1)"
            else:
                badge_color = "#d97706"
                bg_color = "rgba(217, 119, 6, 0.1)"
                
            # Append as a single flat string to avoid markdown code block parsing issues
            table_rows += f'<tr><td style="font-weight: 700; color: #1e3a8a;">💊 {drug}</td><td><span style="font-size: 0.9rem; font-weight: 500;">{drug_class}</span></td><td style="font-size: 0.9rem; opacity: 0.95; line-height: 1.5;">{rationale}</td><td style="text-align: center;"><span style="color: {badge_color}; background-color: {bg_color}; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.3px;">{ev_level}</span></td></tr>'
        
        table_html = f'<div class="custom-table-container"><table class="custom-table"><thead><tr><th style="width: 20%;">Therapy Target</th><th style="width: 20%;">Drug Class</th><th style="width: 50%;">Clinical Rationale</th><th style="text-align: center; width: 10%;">Evidence</th></tr></thead><tbody>{table_rows}</tbody></table></div>'
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No specific targeted therapy recommendations generated.")

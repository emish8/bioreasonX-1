import streamlit as st
import pandas as pd

def render_analysis():
    st.markdown("## 📊 Clinical Analysis Dashboard")

    if "pipeline_results" not in st.session_state:
        st.info("No active analysis. Please submit a mutation query on the Home page.")
        return

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

    # Top stats
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Target Gene", gene)
    with c2:
        st.metric("Variant", mutation_query)
    with c3:
        st.metric("Clinical Class", clin_sig)
    with c4:
        st.metric("Consensus Confidence", f"{conf_score}%")

    st.markdown("---")

    col_left, col_right = st.columns(2, gap="medium")

    with col_left:
        # Card 1: Mutation Summary
        with st.container(border=True):
            st.markdown("#### 🧬 Variant Characterization")
            st.markdown(f"**Target String:** `{mutation_query}`")
            st.markdown(f"**Gene Association:** `{gene}`")
            st.markdown(f"**Structural Variant Type:** {mutation_type}")
            st.markdown(f"**Significance Tag:** {clin_sig}")
            st.markdown(f"**Pathogenicity Confidence:** {mutation_details.get('confidence_score', 'N/A')}%")

        # Card 2: Protein Disruption
        with st.container(border=True):
            st.markdown("#### 🔬 Protein Disruption Mapping")
            st.write(protein_impact)

        # Card 3: Pathway Reasoning
        with st.container(border=True):
            st.markdown("#### 🔄 Pathway Cascade Disruption")
            p_text = pathway_reasoning.get("pathway_reasoning", "N/A")
            st.write(p_text)
            
            p_list = pathway_reasoning.get("affected_pathways", [])
            if p_list:
                st.markdown("**Affected Pathway Steps:**")
                st.markdown(" &rarr; ".join([f"`{p}`" for p in p_list]), unsafe_allow_html=True)
                
            st.markdown(f"**Primary Downstream Effect:** {pathway_reasoning.get('downstream_effects', 'N/A')}")

    with col_right:
        # Card 4: Disease Associations
        with st.container(border=True):
            st.markdown("#### 🏥 Associated Malignancies")
            diseases = consensus.get("disease_associations", [])
            if diseases:
                for dis in diseases:
                    st.markdown(f"• **{dis}**")
            else:
                st.write("No direct disease connections registered.")

        # Card 5: Validation Audit Summary
        with st.container(border=True):
            st.markdown("#### 🛡️ Clinical Evidence Verification")
            v_score = validation.get("validation_score", 0.0)
            is_valid = validation.get("is_valid", False)
            
            val_col1, val_col2 = st.columns([1, 2])
            with val_col1:
                st.metric("Audit Score", f"{v_score}%")
            with val_col2:
                st.markdown(f"**Audited Status:** {'Passed ✅' if is_valid else 'Flagged ⚠️'}")
                st.markdown(f"**Contradiction Detected:** {validation.get('contradiction_detected', False)}")
                
            st.markdown(f"**Audit Notes:** *{validation.get('verification_details', 'N/A')}*")

        # Card 6: Executive Findings Summary
        with st.container(border=True):
            st.markdown("#### 📝 Executive Clinical Findings")
            st.write(consensus.get("final_findings", "N/A"))

    st.markdown("---")

    # Therapy Suggestions Table at the bottom
    st.markdown("### 💊 Targeted Therapy Guidance")
    if therapies:
        df_therapies = pd.DataFrame(therapies)
        # Rename columns for presentation
        df_therapies.rename(columns={
            "drug": "Therapy Target",
            "drug_class": "Drug Class",
            "rationale": "Clinical Rationale",
            "evidence_level": "Evidence Level"
        }, inplace=True, errors='ignore')
        
        st.table(df_therapies)
    else:
        st.write("No specific targeted therapy recommendations generated.")

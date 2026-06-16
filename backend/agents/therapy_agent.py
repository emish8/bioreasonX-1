import json
from backend.agents.state import AgentState
from backend.utils.gemini_client import query_gemini_agent
from backend.utils.config import logger

def run_therapy_agent(state: AgentState) -> AgentState:
    """Agent 5: Prescribes precision medicine therapy recommendations based on biological disruption."""
    mutation_input = state.get("mutation_input", "")
    mutation_details = state.get("mutation_details", {})
    protein_impact = state.get("protein_impact", "")
    pathway_reasoning = state.get("pathway_reasoning", {})
    evidence_docs = state.get("literature_evidence", [])
    
    gene = mutation_details.get("gene", "Unknown")

    logger.info(f"Running Therapy Recommendation Agent for: '{gene}'")

    # Construct literature text to guide clinical guidance
    literature_summary = "\n".join([
        f"- ID: {doc['id']}, Source: {doc['source']}, Abstract: {doc['abstract'][:150]}..." 
        for doc in evidence_docs
    ])

    system_prompt = (
        "You are an expert precision oncology clinician. Recommend targeted therapies and drugs based on "
        "the biological and pathway disruption of a genomic variant. Detail approved drugs, therapeutic class, "
        "mechanism-based clinical rationale, and clinical evidence grade (e.g. FDA Approved (High), Off-label (Moderate), Clinical Trial (Low)). "
        "Return a JSON array containing elements with keys: 'drug' (string), 'drug_class' (string), 'rationale' (string), and 'evidence_level' (string)."
    )
    user_prompt = (
        f"Recommend therapies for gene '{gene}' variant '{mutation_input}'.\n"
        f"Protein Impact: {protein_impact}\n"
        f"Pathway Impact: {pathway_reasoning}\n"
        f"Literature evidence: \n{literature_summary}\n"
        "Provide precision medicine guidance. Respond ONLY with valid JSON."
    )

    try:
        response_text = query_gemini_agent(
            agent_name="Therapy Recommendation Agent",
            mutation_input=mutation_input,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True
        )
        therapies_list = json.loads(response_text)
    except Exception as e:
        logger.error(f"Error parsing Therapy Agent output: {e}. Raw response: {repr(response_text) if 'response_text' in locals() else 'N/A'}")
        therapies_list = [
            {
                "drug": "Broad Spectrum Tyrosine Kinase Inhibitor",
                "drug_class": "TKI",
                "rationale": "General signal transduction targeting as clinical validation is pending.",
                "evidence_level": "Off-label (Low)"
            }
        ]

    # Format trace
    drugs_str = ", ".join([tx.get("drug", "Drug") for tx in therapies_list])
    trace = {
        "step": "Precision Therapy Mapping",
        "detail": f"Recommended therapies: {drugs_str}. Primary class: {therapies_list[0].get('drug_class', 'N/A')}."
    }

    state["therapies"] = therapies_list
    state["reasoning_trace"].append(trace)

    return state

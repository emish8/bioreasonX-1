import json
from backend.agents.state import AgentState
from backend.utils.gemini_client import query_gemini_agent
from backend.utils.config import logger

def run_pathway_agent(state: AgentState) -> AgentState:
    """Agent 3: Identifies pathway disruption, downstream effects, and biological cascades."""
    mutation_input = state.get("mutation_input", "")
    mutation_details = state.get("mutation_details", {})
    protein_impact = state.get("protein_impact", "")
    gene = mutation_details.get("gene", "Unknown")

    logger.info(f"Running Pathway Analysis Agent for: '{gene}'")

    system_prompt = (
        "You are an expert pathway and systems biology researcher. Analyze the downstream pathway impacts "
        "of a gene/protein disruption. Identify specific pathways affected and details of downstream consequences. "
        "Return a JSON object containing keys: 'pathway_reasoning' (string explaining how the pathway is disrupted), "
        "'affected_pathways' (list of strings representing the main pathways), and 'downstream_effects' (string detailing biological outcomes)."
    )
    user_prompt = (
        f"Analyze pathway impacts for '{gene}' disruption. Protein impact summary: {protein_impact}. "
        "Provide a downstream pathway cascade. Respond ONLY with valid JSON."
    )

    try:
        response_text = query_gemini_agent(
            agent_name="Pathway Analysis Agent",
            mutation_input=mutation_input,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True
        )
        pathway_data = json.loads(response_text)
    except Exception as e:
        logger.error(f"Error parsing Pathway Agent output: {e}. Raw response: {repr(response_text) if 'response_text' in locals() else 'N/A'}")
        pathway_data = {
            "pathway_reasoning": "Downstream biological pathway transduction altered due to mutated gene activity.",
            "affected_pathways": ["Cellular growth pathways"],
            "downstream_effects": "Impaired regulatory controls"
        }

    # Format trace
    pathways_str = " -> ".join(pathway_data.get("affected_pathways", ["Pathway"]))
    trace = {
        "step": "Pathway Disruption Analysis",
        "detail": f"Identified cascade: {gene} -> {pathways_str}. Outcome: {pathway_data.get('downstream_effects', 'N/A')}"
    }

    state["pathway_reasoning"] = pathway_data
    state["reasoning_trace"].append(trace)

    return state

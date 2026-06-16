import json
from backend.agents.state import AgentState
from backend.utils.gemini_client import query_gemini_agent
from backend.utils.config import logger

def run_mutation_agent(state: AgentState) -> AgentState:
    """Agent 1: Interprets mutation string, identifies genes and classifications."""
    mutation_input = state.get("mutation_input", "").strip()
    logger.info(f"Running Mutation Analysis Agent for: '{mutation_input}'")

    system_prompt = (
        "You are an expert bioinformatics variant interpreter. Analyze the provided clinical mutation string "
        "and return a JSON object with keys: 'gene' (string), 'mutation_type' (string, e.g., frameshift, missense, duplication), "
        "'clinical_significance' (string, e.g., Pathogenic, Benign, VUS), and 'confidence_score' (float, 0-100)."
    )
    user_prompt = f"Analyze the mutation variant: '{mutation_input}'. Respond ONLY with valid JSON."

    try:
        response_text = query_gemini_agent(
            agent_name="Mutation Analysis Agent",
            mutation_input=mutation_input,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True
        )
        # Parse output
        details = json.loads(response_text)
    except Exception as e:
        logger.error(f"Error parsing Mutation Agent output: {e}. Raw response: {repr(response_text) if 'response_text' in locals() else 'N/A'}")
        details = {
            "gene": "Unknown",
            "mutation_type": "Unknown",
            "clinical_significance": "VUS",
            "confidence_score": 50.0
        }

    # Format trace
    trace = {
        "step": "Mutation Analysis",
        "detail": f"Detected gene: {details.get('gene', 'N/A')}, Type: {details.get('mutation_type', 'N/A')}, Clinical Significance: {details.get('clinical_significance', 'N/A')}."
    }
    
    state["mutation_details"] = details
    if "reasoning_trace" not in state or not state["reasoning_trace"]:
        state["reasoning_trace"] = []
    state["reasoning_trace"].append(trace)
    
    return state

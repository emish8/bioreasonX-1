from backend.agents.state import AgentState
from backend.utils.gemini_client import query_gemini_agent
from backend.utils.config import logger

def run_gene_agent(state: AgentState) -> AgentState:
    """Agent 2: Analyzes gene biological role and how the mutation disrupts protein structure/function."""
    mutation_input = state.get("mutation_input", "")
    mutation_details = state.get("mutation_details", {})
    gene = mutation_details.get("gene", "Unknown")
    mut_type = mutation_details.get("mutation_type", "Unknown")
    
    logger.info(f"Running Gene & Protein Agent for: '{gene}' ({mut_type})")

    system_prompt = (
        "You are an expert cancer molecular biologist. Describe how a specific mutation disrupts the "
        "corresponding gene and protein product. Outline the normal function of the protein and explain "
        "the structural/functional impact of the variant (e.g. ligand-independent activation, truncation, loss of binding domains)."
    )
    user_prompt = (
        f"Analyze the gene impact for variant '{mutation_input}' in gene '{gene}'. "
        f"The mutation type is identified as '{mut_type}'. "
        f"Provide a clear paragraph summary of the protein level disruption."
    )

    response_text = query_gemini_agent(
        agent_name="Gene & Protein Agent",
        mutation_input=mutation_input,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_mode=False
    )

    trace = {
        "step": "Gene & Protein Disruption Analysis",
        "detail": f"Analyzed molecular disruption for {gene} protein. Identified functional consequence: {response_text[:120]}..."
    }
    
    state["protein_impact"] = response_text
    state["reasoning_trace"].append(trace)
    
    return state

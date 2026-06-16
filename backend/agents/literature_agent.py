from backend.agents.state import AgentState
from backend.rag.retriever import BiomedicalRetriever
from backend.utils.config import logger

# Initialize a global retriever to share cache
_retriever = None

def get_retriever():
    global _retriever
    if _retriever is None:
        logger.info("Initializing Literature Agent BiomedicalRetriever instance.")
        _retriever = BiomedicalRetriever()
    return _retriever

def run_literature_agent(state: AgentState) -> AgentState:
    """Agent 4: Literature Intelligence Agent - queries the local RAG vector DB for publications."""
    mutation_input = state.get("mutation_input", "")
    mutation_details = state.get("mutation_details", {})
    gene = mutation_details.get("gene", "Unknown")

    logger.info(f"Running Literature Intelligence Agent for query: '{mutation_input}'")

    retriever = get_retriever()
    
    # Run multiple RAG queries for robustness (e.g. mutation input and gene name separately)
    rag_results_query = retriever.retrieve(mutation_input, top_k=3)
    rag_results_gene = retriever.retrieve(f"{gene} mutation clinical significance", top_k=2)

    # Deduplicate results by document 'id'
    seen_ids = set()
    evidence_docs = []
    
    for doc in (rag_results_query + rag_results_gene):
        if doc["id"] not in seen_ids:
            seen_ids.add(doc["id"])
            evidence_docs.append(doc)

    logger.info(f"Retrieved {len(evidence_docs)} unique literature references via RAG.")

    # Format trace
    sources_str = ", ".join([f"{doc['id']} ({doc['source']})" for doc in evidence_docs])
    trace = {
        "step": "Literature Evidence Retrieval",
        "detail": f"Queried RAG database. Found {len(evidence_docs)} supporting articles: {sources_str}."
    }

    state["literature_evidence"] = evidence_docs
    state["reasoning_trace"].append(trace)

    return state

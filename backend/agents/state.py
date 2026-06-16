from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    # User-supplied variant query
    mutation_input: str
    
    # AGENT 1: Mutation Analysis Agent
    mutation_details: Dict[str, Any]
    
    # AGENT 2: Gene & Protein Agent
    protein_impact: str
    
    # AGENT 3: Pathway Analysis Agent
    pathway_reasoning: Dict[str, Any]
    
    # AGENT 4: Literature Intelligence Agent
    literature_evidence: List[Dict[str, Any]]
    
    # AGENT 5: Therapy Recommendation Agent
    therapies: List[Dict[str, Any]]
    
    # AGENT 6: Evidence Validation Agent
    validation: Dict[str, Any]
    
    # AGENT 7: Consensus Agent
    consensus: Dict[str, Any]
    
    # Explanatory Chain-of-Thought (CoT) timeline trace
    reasoning_trace: List[Dict[str, str]]

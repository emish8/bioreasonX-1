from langgraph.graph import StateGraph, END
from typing import Dict, Any

from backend.agents.state import AgentState
from backend.agents.mutation_agent import run_mutation_agent
from backend.agents.gene_agent import run_gene_agent
from backend.agents.pathway_agent import run_pathway_agent
from backend.agents.literature_agent import run_literature_agent
from backend.agents.therapy_agent import run_therapy_agent
from backend.agents.validation_agent import run_validation_agent
from backend.agents.consensus_agent import run_consensus_agent

from backend.knowledge_graph.graph_builder import BiomedicalGraph
from backend.utils.config import logger

def update_knowledge_graph_with_results(state: AgentState):
    """Post-processing hook to dynamically add new reasoning elements into the Knowledge Graph."""
    try:
        logger.info("Injecting agentic reasoning outputs into the Biomedical Knowledge Graph.")
        graph = BiomedicalGraph()
        
        mutation = state.get("mutation_input")
        details = state.get("mutation_details", {})
        gene = details.get("gene", "Unknown Gene")
        mut_type = details.get("mutation_type", "Unknown Variant")
        clin_sig = details.get("clinical_significance", "VUS")
        
        protein_impact = state.get("protein_impact", "")
        
        pathway_data = state.get("pathway_reasoning", {})
        primary_pathway = "Unknown Pathway"
        if isinstance(pathway_data, dict):
            affected = pathway_data.get("affected_pathways", [])
            if affected:
                primary_pathway = affected[0]
                
        consensus_data = state.get("consensus", {})
        primary_disease = "Associated Disease"
        diseases = consensus_data.get("disease_associations", [])
        if diseases:
            primary_disease = diseases[0]
            
        therapies = state.get("therapies", [])
        primary_drug = "Standard Therapy"
        if therapies:
            primary_drug = therapies[0].get("drug", "Targeted Drug")
            
        evidence = state.get("literature_evidence", [])
        primary_pub = "PMID-Unknown"
        if evidence:
            primary_pub = evidence[0].get("id", "Literature Reference")

        protein_node = f"{gene} Protein"

        # 1. Inject Nodes
        graph.add_node(mutation, "Mutation", {"type": mut_type, "clinical_significance": clin_sig})
        graph.add_node(gene, "Gene", {"function": f"Biological role related to {gene}"})
        graph.add_node(protein_node, "Protein", {"function": protein_impact[:120]})
        graph.add_node(primary_pathway, "Pathway", {"description": f"Pathway cascade involving {gene}"})
        graph.add_node(primary_disease, "Disease", {"phenotype": f"Malignancy linked to {gene}"})
        graph.add_node(primary_drug, "Drug", {"class": "Targeted Inhibitor"})
        graph.add_node(primary_pub, "Publication", {"title": "Clinical trials reference paper"})

        # 2. Inject Relationships
        graph.add_edge(mutation, gene, "affects")
        graph.add_edge(gene, protein_node, "encodes")
        graph.add_edge(protein_node, primary_pathway, "participates_in")
        graph.add_edge(primary_pathway, primary_disease, "associated_with")
        graph.add_edge(primary_drug, protein_node, "targets")
        graph.add_edge(primary_pub, primary_drug, "supports")

        # Save updates (specifically for NetworkX)
        if not graph.use_neo4j:
            graph.save_networkx_graph()
            
        graph.close()
        logger.info("Knowledge Graph injection completed.")
    except Exception as e:
        logger.error(f"Error injecting results into knowledge graph: {e}")


def build_bioreason_workflow() -> StateGraph:
    """Builds and compiles the multi-agent StateGraph flow using LangGraph."""
    logger.info("Assembling LangGraph Multi-Agent state workflow.")
    
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("mutation_agent", run_mutation_agent)
    builder.add_node("gene_agent", run_gene_agent)
    builder.add_node("pathway_agent", run_pathway_agent)
    builder.add_node("literature_agent", run_literature_agent)
    builder.add_node("therapy_agent", run_therapy_agent)
    builder.add_node("validation_agent", run_validation_agent)
    builder.add_node("consensus_agent", run_consensus_agent)
    
    # Establish entry point
    builder.set_entry_point("mutation_agent")
    
    # Formulate sequential edges
    builder.add_edge("mutation_agent", "gene_agent")
    builder.add_edge("gene_agent", "pathway_agent")
    builder.add_edge("pathway_agent", "literature_agent")
    builder.add_edge("literature_agent", "therapy_agent")
    builder.add_edge("therapy_agent", "validation_agent")
    builder.add_edge("validation_agent", "consensus_agent")
    
    # End node transition
    builder.add_edge("consensus_agent", END)
    
    return builder.compile()


def run_bioreason_pipeline(mutation_query: str) -> Dict[str, Any]:
    """Runs the compiled LangGraph workflow pipeline with a target mutation query."""
    logger.info(f"Triggering BioReason-X pipeline for mutation: '{mutation_query}'")
    
    workflow = build_bioreason_workflow()
    
    initial_state = {
        "mutation_input": mutation_query,
        "mutation_details": {},
        "protein_impact": "",
        "pathway_reasoning": {},
        "literature_evidence": [],
        "therapies": [],
        "validation": {},
        "consensus": {},
        "reasoning_trace": []
    }
    
    final_state = workflow.invoke(initial_state)
    
    # Inject compiled nodes into graph database
    update_knowledge_graph_with_results(final_state)
    
    return final_state


def stream_bioreason_pipeline(mutation_query: str):
    """Streams the compiled LangGraph workflow pipeline, yielding (node_name, state)."""
    logger.info(f"Streaming BioReason-X pipeline for mutation: '{mutation_query}'")
    
    workflow = build_bioreason_workflow()
    
    state = {
        "mutation_input": mutation_query,
        "mutation_details": {},
        "protein_impact": "",
        "pathway_reasoning": {},
        "literature_evidence": [],
        "therapies": [],
        "validation": {},
        "consensus": {},
        "reasoning_trace": []
    }
    
    for event in workflow.stream(state):
        for node_name, updated_state in event.items():
            yield node_name, updated_state
            state = updated_state
            
    # Inject compiled nodes into graph database
    update_knowledge_graph_with_results(state)
    yield "complete", state


import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple
import networkx as nx

from backend.utils.config import (
    NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD,
    GRAPH_DB_PATH, has_neo4j_credentials, logger
)

class BiomedicalGraph:
    def __init__(self):
        self.use_neo4j = has_neo4j_credentials()
        self.nx_graph = nx.DiGraph()
        self.driver = None

        if self.use_neo4j:
            try:
                from neo4j import GraphDatabase
                self.driver = GraphDatabase.driver(
                    NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
                )
                self.driver.verify_connectivity()
                logger.info("Connected successfully to Neo4j database.")
            except Exception as e:
                logger.warning(f"Neo4j connection failed: {e}. Falling back to NetworkX.")
                self.use_neo4j = False

        if not self.use_neo4j:
            logger.info("Using NetworkX in-memory graph engine.")
            self.load_networkx_graph()

    def load_networkx_graph(self):
        """Loads a cached NetworkX graph or creates a default one if empty."""
        if GRAPH_DB_PATH.exists():
            try:
                with open(GRAPH_DB_PATH, "rb") as f:
                    self.nx_graph = pickle.load(f)
                logger.info(f"Loaded cached NetworkX graph with {self.nx_graph.number_of_nodes()} nodes.")
                return
            except Exception as e:
                logger.error(f"Error loading cached graph: {e}. Building a new one.")

        # If cache doesn't exist, build standard database
        self.build_default_graph()

    def build_default_graph(self):
        """Builds a rich biomedical graph for our target mutations."""
        logger.info("Building default biomedical graph...")
        self.nx_graph = nx.DiGraph()

        # --------------------- BRCA1 c.5266dupC Path ---------------------
        self.add_node("BRCA1 c.5266dupC", "Mutation", {"type": "Frameshift", "clinical_significance": "Pathogenic"})
        self.add_node("BRCA1", "Gene", {"function": "Tumor Suppressor / DNA Repair Scaffold"})
        self.add_node("BRCA1 Protein", "Protein", {"function": "Homologous recombination initiator & cell cycle checkpoint control"})
        self.add_node("Homologous Recombination", "Pathway", {"description": "High-fidelity double-strand DNA break repair pathway"})
        self.add_node("Breast and Ovarian Cancer", "Disease", {"phenotype": "Malignant transformation of epithelial tissue"})
        self.add_node("Olaparib", "Drug", {"class": "PARP Inhibitor", "action": "Induces synthetic lethality"})
        self.add_node("PMID-29402511", "Publication", {"title": "Synthetic Lethality in BRCA1 carriers using Olaparib"})

        self.add_edge("BRCA1 c.5266dupC", "BRCA1", "affects", {"disruption": "High"})
        self.add_edge("BRCA1", "BRCA1 Protein", "encodes")
        self.add_edge("BRCA1 Protein", "Homologous Recombination", "participates_in")
        self.add_edge("Homologous Recombination", "Breast and Ovarian Cancer", "associated_with")
        self.add_edge("Olaparib", "BRCA1 Protein", "targets")
        self.add_edge("PMID-29402511", "Olaparib", "supports")

        # --------------------- EGFR L858R Path ---------------------
        self.add_node("EGFR L858R", "Mutation", {"type": "Missense / Exon 21", "clinical_significance": "Pathogenic (Somatic)"})
        self.add_node("EGFR", "Gene", {"function": "Epidermal Growth Factor Receptor"})
        self.add_node("EGFR kinase", "Protein", {"function": "Receptor tyrosine kinase signaling cell survival"})
        self.add_node("MAPK Signaling", "Pathway", {"description": "RAF-MEK-ERK cellular proliferation cascade"})
        self.add_node("Lung Adenocarcinoma", "Disease", {"phenotype": "Non-small cell lung cancer subtype"})
        self.add_node("Osimertinib", "Drug", {"class": "3rd-gen EGFR TKI", "action": "Covalent inhibitor"})
        self.add_node("PMID-26458312", "Publication", {"title": "EGFR L858R Mutation and TKI Sensitivity"})

        self.add_edge("EGFR L858R", "EGFR", "affects", {"disruption": "Activating"})
        self.add_edge("EGFR", "EGFR kinase", "encodes")
        self.add_edge("EGFR kinase", "MAPK Signaling", "participates_in")
        self.add_edge("MAPK Signaling", "Lung Adenocarcinoma", "associated_with")
        self.add_edge("Osimertinib", "EGFR kinase", "targets")
        self.add_edge("PMID-26458312", "Osimertinib", "supports")

        # --------------------- BRAF V600E Path ---------------------
        self.add_node("BRAF V600E", "Mutation", {"type": "Missense / Codon 600", "clinical_significance": "Pathogenic (Somatic)"})
        self.add_node("BRAF", "Gene", {"function": "Serine/threonine-protein kinase"})
        self.add_node("BRAF V600E Kinase", "Protein", {"function": "Constitutively active monomer phosphorylating MEK"})
        self.add_node("Metastatic Melanoma", "Disease", {"phenotype": "Aggressive cutaneous melanocytic tumor"})
        self.add_node("Vemurafenib", "Drug", {"class": "BRAF inhibitor", "action": "Selective monomer inhibitor"})
        self.add_node("PMID-21876543", "Publication", {"title": "Targeted Inhibition of BRAF V600E in Melanoma"})

        self.add_edge("BRAF V600E", "BRAF", "affects", {"disruption": "Hyperactivation"})
        self.add_edge("BRAF", "BRAF V600E Kinase", "encodes")
        self.add_edge("BRAF V600E Kinase", "MAPK Signaling", "participates_in")
        self.add_edge("MAPK Signaling", "Metastatic Melanoma", "associated_with")
        self.add_edge("Vemurafenib", "BRAF V600E Kinase", "targets")
        self.add_edge("PMID-21876543", "Vemurafenib", "supports")

        self.save_networkx_graph()

    def save_networkx_graph(self):
        """Saves current NetworkX graph state to cache."""
        try:
            with open(GRAPH_DB_PATH, "wb") as f:
                pickle.dump(self.nx_graph, f)
            logger.info("Saved NetworkX graph to cache.")
        except Exception as e:
            logger.error(f"Error saving NetworkX graph: {e}")

    def add_node(self, node_id: str, label: str, properties: Dict[str, Any] = None):
        """Adds a node to either Neo4j or NetworkX."""
        properties = properties or {}
        properties["label"] = label # Add node type

        if self.use_neo4j:
            query = (
                f"MERGE (n:{label} {{id: $node_id}}) "
                f"SET n += $properties"
            )
            try:
                with self.driver.session() as session:
                    session.run(query, node_id=node_id, properties=properties)
            except Exception as e:
                logger.error(f"Neo4j add_node error: {e}")
        else:
            try:
                self.nx_graph.add_node(node_id, **properties)
            except TypeError as e:
                import inspect
                logger.error(f"add_node failed: node_id={node_id}, properties={properties}")
                logger.error(f"nx_graph type: {type(self.nx_graph)}")
                logger.error(f"add_node signature: {inspect.signature(self.nx_graph.add_node)}")
                raise e

    def add_edge(self, source_id: str, target_id: str, relationship: str, properties: Dict[str, Any] = None):
        """Adds a directed relationship/edge between two nodes."""
        properties = properties or {}
        
        if self.use_neo4j:
            # We assume node types are stored/indexed already.
            # Using generic match and merge relationship
            query = (
                "MATCH (a {id: $source_id}), (b {id: $target_id}) "
                f"MERGE (a)-[r:{relationship}]->(b) "
                "SET r += $properties"
            )
            try:
                with self.driver.session() as session:
                    session.run(query, source_id=source_id, target_id=target_id, properties=properties)
            except Exception as e:
                logger.error(f"Neo4j add_edge error: {e}")
        else:
            self.nx_graph.add_edge(source_id, target_id, relation=relationship, **properties)

    def get_pyvis_elements(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Formats graph elements for pyvis visualization."""
        nodes = []
        edges = []

        if self.use_neo4j:
            # Fetch from Neo4j
            query = "MATCH (n) RETURN n.id as id, labels(n)[0] as label, properties(n) as props"
            edge_query = "MATCH (a)-[r]->(b) RETURN a.id as source, b.id as target, type(r) as relation"
            try:
                with self.driver.session() as session:
                    n_records = session.run(query)
                    for rec in n_records:
                        nodes.append({
                            "id": rec["id"],
                            "label": rec["id"],
                            "category": rec["label"],
                            "properties": rec["props"]
                        })
                    
                    e_records = session.run(edge_query)
                    for rec in e_records:
                        edges.append({
                            "from": rec["source"],
                            "to": rec["target"],
                            "label": rec["relation"]
                        })
            except Exception as e:
                logger.error(f"Neo4j visualization query failed: {e}")
        else:
            # Read from NetworkX
            for node, attrs in self.nx_graph.nodes(data=True):
                nodes.append({
                    "id": node,
                    "label": node,
                    "category": attrs.get("label", "Unknown"),
                    "properties": {k: v for k, v in attrs.items() if k != "label"}
                })
            for u, v, attrs in self.nx_graph.edges(data=True):
                edges.append({
                    "from": u,
                    "to": v,
                    "label": attrs.get("relation", "linked_to")
                })

        return nodes, edges

    def query_graph_relations(self, entity_id: str) -> List[Dict[str, Any]]:
        """Queries immediate relationships for a given entity."""
        results = []
        if self.use_neo4j:
            query = (
                "MATCH (n {id: $entity_id})-[r]->(m) "
                "RETURN labels(m)[0] as target_label, m.id as target_id, type(r) as rel"
            )
            try:
                with self.driver.session() as session:
                    records = session.run(query, entity_id=entity_id)
                    for rec in records:
                        results.append({
                            "source": entity_id,
                            "relation": rec["rel"],
                            "target": rec["target_id"],
                            "target_category": rec["target_label"]
                        })
            except Exception as e:
                logger.error(f"Neo4j query failed: {e}")
        else:
            # Query NetworkX
            if self.nx_graph.has_node(entity_id):
                for target in self.nx_graph.successors(entity_id):
                    edge_data = self.nx_graph.get_edge_data(entity_id, target)
                    target_data = self.nx_graph.nodes[target]
                    results.append({
                        "source": entity_id,
                        "relation": edge_data.get("relation", "linked_to"),
                        "target": target,
                        "target_category": target_data.get("label", "Unknown")
                    })
        return results

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver connection closed.")

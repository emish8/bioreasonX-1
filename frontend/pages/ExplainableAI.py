import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path

from backend.knowledge_graph.graph_builder import BiomedicalGraph
from backend.utils.config import DATA_DIR, logger

# Try importing pyvis, fallback if needed
try:
    from pyvis.network import Network
    HAS_PYVIS = True
except ImportError:
    logger.warning("pyvis not installed. Falling back to static graph elements representation.")
    HAS_PYVIS = False

# Node color styling map
CATEGORY_COLORS = {
    "Mutation": "#ED8936",    # Orange
    "Gene": "#4299E1",        # Blue
    "Protein": "#9F7AEA",     # Purple
    "Pathway": "#319795",     # Teal
    "Disease": "#E53E3E",     # Deep Red
    "Drug": "#48BB78",        # Green
    "Publication": "#ECC94B"  # Gold
}

def render_explainable_ai():
    st.markdown("## 🧠 Explainable AI & Reasoning Graph")
    st.markdown(
        """
        Explore the step-by-step biomedical reasoning relationships dynamically generated 
        from agent outputs and RAG ingestion in the visual knowledge graph below.
        """
    )
    # Guided Tour Expander for non-experts
    is_expanded = True
    with st.expander("📖 Guide: How to Read the Reasoning Graph", expanded=is_expanded):
        st.write(
            "The reasoning graph acts like a **detective map**. It connects a genomic mutation "
            "all the way to its downstream cellular disruption, clinical disease, and the targeted drug that can treat it."
        )
        
        st.markdown("### 1. Core Biological Flow")
        # Visual representation using emojis
        st.info(
            "🧬 **Mutation** &nbsp;➡️&nbsp; 🧬 **Gene** &nbsp;➡️&nbsp; 🔬 **Protein** &nbsp;➡️&nbsp; 🔄 **Pathway** &nbsp;➡️&nbsp; 🏥 **Disease**"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("**🧬 Mutation &rarr; Gene &rarr; Protein**")
                st.markdown(
                    "- **Mutation**: The specific genomic change query (e.g. *EGFR L858R*).\n"
                    "- **Gene**: The gene structure containing the mutation (e.g. *EGFR*).\n"
                    "- **Protein**: The active molecule whose shape/function is altered by the mutation."
                )
        with col2:
            with st.container(border=True):
                st.markdown("**🔄 Pathway &rarr; 🏥 Disease**")
                st.markdown(
                    "- **Pathway**: The cell signaling cascade triggered to abnormal levels (e.g. *PI3K-Akt signaling*).\n"
                    "- **Disease**: The cancer or clinical condition linked to this pathway disruption."
                )

        st.markdown("### 2. Therapeutic Strategy & Support")
        col3, col4 = st.columns(2)
        with col3:
            with st.container(border=True):
                st.markdown("#### 💊 Drug")
                st.markdown(
                    "**Targets the Protein**: A targeted inhibitor (e.g. *Osimertinib*) designed to "
                    "bind to and block the overactive mutated protein."
                )
        with col4:
            with st.container(border=True):
                st.markdown("#### 📄 Publication")
                st.markdown(
                    "**Supports the Drug**: Scientific references (e.g. *PMID-26565053*) "
                    "validating the clinical efficacy of this drug."
                )

        st.markdown("### 3. Relationship Link Mechanisms")
        with st.container(border=True):
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.markdown("- **affects**: Mutation alters normal behavior of the gene.")
                st.markdown("- **encodes**: The gene acts as instruction code to build the protein.")
                st.markdown("- **participates_in**: Mutated protein alters signaling in this pathway cascade.")
            with col_l2:
                st.markdown("- **associated_with**: Signaling path deregulation is linked to this cancer/disease.")
                st.markdown("- **targets**: Drug binds directly to the protein to shut down overactivity.")
                st.markdown("- **supports**: Scientific literature validates the treatment guidelines.")
    if "pipeline_results" not in st.session_state:
        st.info("No active analysis. Please submit a mutation query on the Home page.")
        return

    # Key Legend
    st.markdown(
        """
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 25px; padding: 12px 16px; background: rgba(128, 128, 128, 0.03); border: 1px solid rgba(128, 128, 128, 0.08); border-radius: 10px;">
            <div style="font-size: 0.8rem; font-weight: 600; color: #64748B; align-self: center; margin-right: 5px; text-transform: uppercase; letter-spacing: 0.5px;">Reasoning Entities:</div>
            <div style="display: flex; align-items: center; background: rgba(237, 137, 54, 0.08); color: #ED8936; border: 1px solid rgba(237, 137, 54, 0.15); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#ED8936; margin-right:6px;"></span>Mutation
            </div>
            <div style="display: flex; align-items: center; background: rgba(66, 153, 225, 0.08); color: #4299E1; border: 1px solid rgba(66, 153, 225, 0.15); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#4299E1; margin-right:6px;"></span>Gene
            </div>
            <div style="display: flex; align-items: center; background: rgba(159, 122, 234, 0.08); color: #9F7AEA; border: 1px solid rgba(159, 122, 234, 0.15); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#9F7AEA; margin-right:6px;"></span>Protein
            </div>
            <div style="display: flex; align-items: center; background: rgba(49, 151, 149, 0.08); color: #319795; border: 1px solid rgba(49, 151, 149, 0.15); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#319795; margin-right:6px;"></span>Pathway
            </div>
            <div style="display: flex; align-items: center; background: rgba(229, 62, 62, 0.08); color: #E53E3E; border: 1px solid rgba(229, 62, 62, 0.15); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#E53E3E; margin-right:6px;"></span>Disease
            </div>
            <div style="display: flex; align-items: center; background: rgba(72, 187, 120, 0.08); color: #48BB78; border: 1px solid rgba(72, 187, 120, 0.15); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#48BB78; margin-right:6px;"></span>Drug
            </div>
            <div style="display: flex; align-items: center; background: rgba(236, 201, 75, 0.08); color: #B7791F; border: 1px solid rgba(236, 201, 75, 0.15); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#ECC94B; margin-right:6px;"></span>Publication
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Initialize graph backend
    graph_engine = BiomedicalGraph()
    nodes, edges = graph_engine.get_pyvis_elements()
    graph_engine.close()

    if not nodes:
        st.info("The reasoning graph is currently empty. Run an analysis first to populate it.")
        return

    # Check for pyvis availability
    if HAS_PYVIS:
        try:
            # Create Network graph
            net = Network(
                height="550px", 
                width="100%", 
                bgcolor="#ffffff", 
                font_color="#2D3748", 
                directed=True
            )
            
            # Physics Configuration
            net.barnes_hut(
                gravity=-3000, 
                central_gravity=0.3, 
                spring_length=120, 
                spring_strength=0.04, 
                damping=0.85
            )

            # Add nodes
            for node in nodes:
                node_id = node["id"]
                label = node["label"]
                category = node["category"]
                properties = node.get("properties", {})
                
                # Make a tooltip listing node details
                tooltip_parts = [f"<b>{label}</b> ({category})"]
                for k, v in properties.items():
                    tooltip_parts.append(f"{k}: {v}")
                tooltip = "<br>".join(tooltip_parts)
                
                color = CATEGORY_COLORS.get(category, "#A0AEC0") # Gray fallback
                
                net.add_node(
                    node_id, 
                    label=label, 
                    title=tooltip, 
                    color=color, 
                    size=22 if category in ["Mutation", "Gene"] else 18
                )

            # Add edges
            for edge in edges:
                net.add_edge(
                    edge["from"], 
                    edge["to"], 
                    title=edge["label"], 
                    label=edge["label"], 
                    color="#CBD5E0", 
                    width=1.5
                )

            # Save file to generate html string
            temp_html_path = DATA_DIR / "temp_graph.html"
            net.write_html(str(temp_html_path))

            # Read file contents
            with open(temp_html_path, "r", encoding="utf-8") as f:
                html_code = f.read()

            # Remove temporary file
            if temp_html_path.exists():
                os.remove(temp_html_path)

            # Apply transparency overrides
            html_code = html_code.replace('background-color: #ffffff;', 'background-color: transparent;')
            html_code = html_code.replace('border: 1px solid lightgray;', 'border: none;')
            
            style_override = "<style>body { background-color: transparent !important; }</style>"
            html_code = html_code.replace("</head>", f"{style_override}</head>")
            
            # Inject client-side theme detection script
            dark_mode_script = """
            <script>
            window.addEventListener('DOMContentLoaded', (event) => {
                setTimeout(() => {
                    const bgColor = window.getComputedStyle(document.body).backgroundColor;
                    const rgb = bgColor.match(/\\d+/g);
                    if (rgb) {
                        const r = parseInt(rgb[0]);
                        const g = parseInt(rgb[1]);
                        const b = parseInt(rgb[2]);
                        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
                        if (brightness < 128) {
                            // Dark mode detected! Update vis.js options for visibility
                            network.setOptions({
                                nodes: {
                                    font: {
                                        color: '#E2E8F0'
                                    }
                                },
                                edges: {
                                    font: {
                                        color: '#CBD5E0'
                                    },
                                    color: {
                                        color: '#4A5568',
                                        highlight: '#319795',
                                        hover: '#4A5568',
                                        inherit: false
                                    }
                                }
                            });
                        }
                    }
                }, 100);
            });
            </script>
            """
            html_code = html_code.replace("</body>", f"{dark_mode_script}</body>")

            # Render HTML inside Streamlit
            components.html(html_code, height=580, scrolling=True)
            
        except Exception as e:
            st.error(f"Failed to render Pyvis visualization: {e}")
            logger.exception(e)
            render_fallback_lists(nodes, edges)
    else:
        st.warning("Pyvis is not installed in the current environment. Displaying graph relationships in list format below.")
        render_fallback_lists(nodes, edges)


def render_fallback_lists(nodes, edges):
    """Fallback representation for when Pyvis visual library is missing or fails."""
    st.markdown("### 🧬 Nodes (Biological Entities)")
    if nodes:
        node_cards = ""
        for node in nodes:
            label = node.get("label", "N/A")
            cat = node.get("category", "N/A")
            color = CATEGORY_COLORS.get(cat, "#A0AEC0")
            node_cards += f"""
            <div style="background: rgba(128, 128, 128, 0.04); border: 1px solid rgba(128, 128, 128, 0.1); border-left: 4px solid {color}; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: inline-block; margin-right: 8px; min-width: 150px;">
                <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; font-weight: 600;">{cat}</div>
                <div style="font-weight: 700; color: var(--text-color); margin-top: 2px; font-size: 0.95rem;">{label}</div>
            </div>
            """
        st.markdown(f"<div style='margin-bottom: 25px;'>{node_cards}</div>", unsafe_allow_html=True)
    else:
        st.write("No nodes in the reasoning graph.")

    st.markdown("### 🔗 Directed Edges (Mechanisms)")
    if edges:
        edge_items = ""
        for edge in edges:
            frm = edge.get("from", "N/A")
            to = edge.get("to", "N/A")
            label = edge.get("label", "N/A")
            edge_items += f"""
            <div style="background: rgba(128, 128, 128, 0.02); border: 1px solid rgba(128, 128, 128, 0.08); border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; gap: 10px; max-width: 600px;">
                <span style="font-weight: 600; color: #1e3a8a;">{frm}</span>
                <span style="color: #0d9488; font-weight: 700; font-size: 0.85rem; background: rgba(13, 148, 136, 0.08); padding: 4px 12px; border-radius: 20px;">{label} &rarr;</span>
                <span style="font-weight: 600; color: #1e3a8a;">{to}</span>
            </div>
            """
        st.markdown(edge_items, unsafe_allow_html=True)
    else:
        st.write("No edges in the reasoning graph.")

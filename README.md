# BioReason-X

**Mutation &rarr; Mechanism &rarr; Therapy Intelligence Platform**

BioReason-X is an enterprise-grade precision medicine platform designed for genomic researchers, clinical tumor boards, and oncologists. The system automates clinical reasoning, tracing genetic mutations to their downstream cellular disruptions and suggesting targeted therapeutic solutions using a multi-agent framework, localized retrieval-augmented generation (RAG), and a unified knowledge graph.

---

## 🧬 System Architecture

BioReason-X is built on a modular design:

```
BioReason-X/
├── app.py                     # Main Streamlit entrance & page router
├── requirements.txt           # Python package dependencies
├── README.md                  # System manual
├── data/
│   ├── literature_db.json     # Pre-seeded RAG abstracts corpus
│   └── faiss_index/           # Cached vector database indexes
├── backend/
│   ├── agents/
│   │   ├── state.py           # LangGraph session state representation
│   │   ├── mutation_agent.py  # Agent 1: HGVS variant interpreter
│   │   ├── gene_agent.py      # Agent 2: Molecular protein disruption mapping
│   │   ├── pathway_agent.py   # Agent 3: Pathway cascade disruption tracer
│   │   ├── literature_agent.py# Agent 4: Semantic RAG retrieval
│   │   ├── therapy_agent.py   # Agent 5: Precision drug prescription
│   │   ├── validation_agent.py# Agent 6: Logical fact-check auditor
│   │   ├── consensus_agent.py # Agent 7: Consensus report synthesizer
│   │   └── workflow.py        # LangGraph StateGraph assembler & KG updater
│   ├── knowledge_graph/
│   │   └── graph_builder.py   # Neo4j and NetworkX graph controller
│   ├── rag/
│   │   ├── embedder.py        # SentenceTransformers/TF-IDF manager
│   │   └── retriever.py       # FAISS database/NumPy Cosine similarity engine
│   └── utils/
│       ├── config.py          # Environment settings, logger, path config
│       ├── gemini_client.py   # Gemini API connector with templates backup
│       ├── pdf_generator.py   # ReportLab PDF clinical generator
│       └── doc_generator.py   # Word (docx) report exporter
```

### 🤖 Multi-Agent LangGraph Workflow
The analysis follows a sequential clinical path assembled in a LangGraph StateGraph:
1. **Mutation Agent** parses the raw variant and identifies type (insertion/missense) and gene.
2. **Gene Agent** analyzes structural disruptions to the target protein.
3. **Pathway Agent** maps the downstream cellular cascade (e.g., Homologous Recombination or MAPK pathways).
4. **Literature Agent** retrieves reference documents from the local RAG store.
5. **Therapy Agent** identifies targeted therapeutics (e.g., PARP or tyrosine kinase inhibitors).
6. **Validation Agent** critiques the compiled findings to find inconsistencies.
7. **Consensus Agent** compiles the final synthesis, calculating validation and confidence indicators.

### 🕸️ Dual-Engine Knowledge Graph
- **NetworkX (Default Fallback)**: Runs locally as a memory-based directed graph, saved in `data/networkx_graph.gpickle`.
- **Neo4j (Production)**: When configured, nodes and edges are dynamically written to an external Neo4j database using cypher queries.
- Elements are formatted and visualised interactively in the app using **Pyvis**.

---

## 🛠️ Setup Instructions

### 0. Prerequisites
- Python 3.9, 3.10, or 3.11 installed.

### 1. Run models
```bash
# run ollama
nohup ollama serve > ollama.log 2>&1 &

# verfify it running
cat ollama.log 

# run model
ollama run deepseek-r1:32b

#vll
nohup python -m vllm.entrypoints.openai.api_server \
  --model casperhansen/deepseek-r1-distill-qwen-32b-awq \
  --quantization awq \
  --port 8000 \
  --host 127.0.0.1 \
  --max-model-len 8192 \
  --trust-remote-code > vllm.log 2>&1 &
```

### 2. Installation
Clone or navigate to the workspace directory and install requirements:
```bash
python -m venv .venv
source .venv/bin/activate 
pip install -r requirements.txt
```

*(Note: If compilation issues occur installing `faiss-cpu` or `sentence-transformers` on your OS, the codebase will dynamically activate fallbacks: TF-IDF vector embeddings and NumPy-based cosine similarity matrix searches, ensuring the application remains fully operational.)*

### 3. API Key & DB Settings (Optional)
Create a `.env` file in the root directory to activate live services:

```env
# Gemini API Key (Enables live AI reasoning instead of local simulated profiles)
GEMINI_API_KEY=AIzaSy...

# Neo4j Credentials (Enables saving nodes to a live Neo4j cluster)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=myPassword
```

*Note: If no API key is specified, the application launches in **Clinical Simulation Mode** (Demo Mode). This uses detailed mock templates matching our demo profiles (BRCA1, EGFR, BRAF) or synthesizes reasonable predictions dynamically, allowing a full review of the UI, reports, and timeline components without any active API keys.*

---

## 🚀 Running the App

Start the Streamlit application:
```bash
streamlit run app.py --server.port 8501 --server.headless true  --server.enableCORS false --server.enableXsrfProtection false --server.fileWatcherType poll

streamlit run app.py
```
This opens the browser automatically at `http://localhost:8501`.

---

## 📝 Example Executions
Try submitting one of the pre-loaded templates on the Home page:
- **`BRCA1 c.5266dupC`**: Traces the frameshift mutation to Homologous Recombination Deficiency and targets PARP Inhibitors (Olaparib) via synthetic lethality.
- **`EGFR L858R`**: Traces the Exon 21 missense mutation to kinase hyperactivation and targets Osimertinib.
- **`BRAF V600E`**: Traces the V600E active monomer to downstream MEK/ERK activation and targets Vemurafenib or combined RAF/MEK drugs.

---

## ⚙️ Production Deployment Guidance

1. **Host Configuration**: Deploy using standard Streamlit sharing portals, AWS EC2, or docker containers. Set `layout="wide"` in the application profile.
2. **Neo4j Integration**: For shared production setups, replace the local NetworkX file cache with a managed AuraDB cloud instance by setting the standard `NEO4J_URI` env vars.
3. **API Rate Limits**: The live mode uses `gemini-2.5-flash`. To scale, implement user session limits or transition to key-rotation configurations.
4. **Data Security**: In compliance with HIPAA/GDPR clinical standards, this prototype operates locally and does not transmit PHI (Protected Health Information).

import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, List
from backend.utils.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL_FLASH,
    logger,
    USE_LOCAL_LLM,
    LOCAL_LLM_API_BASE,
    LOCAL_LLM_MODEL
)

# Configure google-generativeai if API key is present
HAS_GEMINI = False
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        HAS_GEMINI = True
        logger.info("Gemini API configured successfully.")
    except Exception as e:
        logger.error(f"Error configuring Gemini API: {e}. Falling back to Simulation Mode.")

# Detailed mock profiles for demo mutations
MOCK_PROFILES = {
    "BRCA1 c.5266dupC": {
        "mutation_details": {
            "gene": "BRCA1",
            "mutation_type": "Frameshift Insertion (c.5266dupC)",
            "clinical_significance": "Pathogenic",
            "confidence_score": 98.0
        },
        "protein_impact": (
            "The c.5266dupC duplication mutation in BRCA1 creates a frameshift starting "
            "at codon Gln1756, introducing a premature stop codon 74 amino acids downstream (p.Gln1756Profs). "
            "This truncates the C-terminal BRCT domain, which is essential for interacting with BARD1, "
            "preventing checkpoint control and leaving cells deficient in Homologous Recombination (HR) repair."
        ),
        "pathway_reasoning": {
            "pathway_reasoning": (
                "BRCA1 truncation leads to Homologous Recombination Deficiency (HRD). "
                "The cell loses its primary pathway for repairing double-strand DNA breaks. "
                "Consequently, double-strand breaks must be repaired by highly error-prone pathways like "
                "Non-Homologous End Joining (NHEJ), which induces genome-wide mutation accumulation, "
                "translocations, and genomic instability, highly predisposing cell lines to malignant transformation."
            ),
            "affected_pathways": ["Homologous Recombination DNA Repair", "G2/M DNA Damage Checkpoint"],
            "downstream_effects": "Genomic instability, error-prone NHEJ activation"
        },
        "therapies": [
            {
                "drug": "Olaparib",
                "drug_class": "PARP Inhibitor",
                "rationale": "Induces synthetic lethality by trapping PARP1/2 on single-strand breaks in homologous recombination-deficient cells.",
                "evidence_level": "FDA Approved (High)"
            },
            {
                "drug": "Rucaparib",
                "drug_class": "PARP Inhibitor",
                "rationale": "Traps PARP and blocks base excision repair, selectively killing homologous recombination-deficient tumor lines.",
                "evidence_level": "FDA Approved (High)"
            },
            {
                "drug": "Talazoparib",
                "drug_class": "PARP Inhibitor",
                "rationale": "Highly potent PARP trapper causing synthetic lethality in germline BRCA1-mutated breast cancers.",
                "evidence_level": "FDA Approved (High)"
            }
        ],
        "validation": {
            "is_valid": True,
            "validation_score": 96.0,
            "verification_details": "Consistent with literature (ClinVar VCV000003767, Reactome R-HSA-5693532, and DrugBank DB00947).",
            "contradiction_detected": False
        },
        "consensus": {
            "final_findings": (
                "BRCA1 c.5266dupC is a high-penetrance pathogenic germline founder variant. "
                "It causes a complete loss of BRCA1-mediated homologous recombination DNA repair capability."
            ),
            "disease_associations": ["Hereditary Breast Cancer", "Hereditary Ovarian Cancer", "Prostate Cancer"],
            "final_recommendation": (
                "Genetic counseling is strongly recommended. The therapeutic pipeline should prioritize "
                "PARP inhibitors (e.g., Olaparib, Talazoparib) to leverage synthetic lethality. Platinum-based "
                "chemotherapies (Carboplatin) represent secondary options due to cross-linking repair deficits."
            ),
            "confidence_score": 97.0
        },
        "reasoning_trace": [
            {"step": "Step 1: Variant Parsing", "detail": "Identified BRCA1 nucleotide duplication c.5266dupC."},
            {"step": "Step 2: Protein Disruption Map", "detail": "Detected frameshift truncation of BRCA1 BRCT C-terminal complex site."},
            {"step": "Step 3: Pathway Breakdown", "detail": "Homologous recombination DNA double-strand break repair path disabled."},
            {"step": "Step 4: Literature Retrieval", "detail": "Matched 4 documents linking c.5266dupC to HRD and PARP activity."},
            {"step": "Step 5: Therapy Targeting", "detail": "Identified PARP trapping compounds (Olaparib) for synthetic lethality targeting."},
            {"step": "Step 6: Clinical Validation", "detail": "Verified pathogenicity and therapeutic level of evidence across databases."}
        ]
    },
    "EGFR L858R": {
        "mutation_details": {
            "gene": "EGFR",
            "mutation_type": "Missense Substitution (c.2573T>G, p.Leu858Arg)",
            "clinical_significance": "Pathogenic (Somatic Activation)",
            "confidence_score": 99.0
        },
        "protein_impact": (
            "The EGFR L858R missense mutation substitutes a leucine at codon 858 with an arginine in the active kinase domain. "
            "This substitution introduces a positive charge that disrupts hydrophobic interactions, destabilizing "
            "the autoinhibited inactive conformation. This locks the EGFR kinase domain into a constitutively active state "
            "independent of epidermal growth factor binding."
        ),
        "pathway_reasoning": {
            "pathway_reasoning": (
                "Somatic activation of the EGFR kinase domain triggers ligand-independent autophosphorylation. "
                "This constantly recruits key adaptor proteins, hyperactivating downstream cascades: "
                "the Ras-Raf-MEK-ERK (MAPK) signaling pathway (driving cell division and survival) and "
                "the PI3K-Akt-mTOR pathway (blocking apoptosis). This sustained signaling drives oncogenesis."
            ),
            "affected_pathways": ["EGFR Autophosphorylation", "MAPK Signaling Cascade", "PI3K-Akt Signaling"],
            "downstream_effects": "Constitutive cell proliferation, survival signaling, evasion of apoptosis"
        },
        "therapies": [
            {
                "drug": "Osimertinib",
                "drug_class": "3rd-Gen EGFR TKI",
                "rationale": "Irreversibly binds to the ATP-binding pocket of mutated EGFR (including L858R and T790M resistance mutations), blocking autophosphorylation.",
                "evidence_level": "FDA Approved (High)"
            },
            {
                "drug": "Erlotinib",
                "drug_class": "1st-Gen EGFR TKI",
                "rationale": "Reversibly inhibits EGFR tyrosine kinase, effective for L858R but prone to secondary resistance mutations.",
                "evidence_level": "FDA Approved (Moderate)"
            },
            {
                "drug": "Dacomitinib",
                "drug_class": "2nd-Gen EGFR TKI",
                "rationale": "Irreversible pan-HER inhibitor showing clinical benefit in EGFR-mutated lung cancers.",
                "evidence_level": "FDA Approved (Moderate)"
            }
        ],
        "validation": {
            "is_valid": True,
            "validation_score": 98.0,
            "verification_details": "Corroborated by FDA approval guidelines and ClinVar somatic cancer databases.",
            "contradiction_detected": False
        },
        "consensus": {
            "final_findings": (
                "EGFR L858R is a classic somatic activating mutation representing a major target in lung adenocarcinoma. "
                "It induces hyperactivation of downstream proliferative pathways."
            ),
            "disease_associations": ["Lung Adenocarcinoma", "Non-Small Cell Lung Cancer"],
            "final_recommendation": (
                "Prioritize treatment with third-generation EGFR TKIs, specifically Osimertinib. "
                "Monitor for the emergence of secondary resistance variants, such as EGFR C797S or MET amplification."
            ),
            "confidence_score": 99.0
        },
        "reasoning_trace": [
            {"step": "Step 1: Variant Parsing", "detail": "Identified missense variant EGFR p.Leu858Arg (L858R)."},
            {"step": "Step 2: Protein Disruption Map", "detail": "Determined active kinase domain destabilization, leading to ligand-independent activity."},
            {"step": "Step 3: Pathway Breakdown", "detail": "Identified hyperactivation of receptor tyrosine kinase, downstream MAPK and PI3K pathways."},
            {"step": "Step 4: Literature Retrieval", "detail": "Matched references connecting Exon 21 activating mutations with TKI drug profiles."},
            {"step": "Step 5: Therapy Targeting", "detail": "Recommended covalent 3rd-generation TKIs (Osimertinib) as primary clinical option."},
            {"step": "Step 6: Clinical Validation", "detail": "Confirmed therapeutic validation against FDA oncology indications."}
        ]
    },
    "BRAF V600E": {
        "mutation_details": {
            "gene": "BRAF",
            "mutation_type": "Missense Substitution (c.1799T>A, p.Val600Glu)",
            "clinical_significance": "Pathogenic (Somatic Activation)",
            "confidence_score": 99.0
        },
        "protein_impact": (
            "The BRAF V600E mutation substitutes valine (a hydrophobic residue) with glutamic acid (a negatively charged residue) "
            "at codon 600. The negative charge mimics activation-loop phosphorylation, forcing the kinase domain into a constitutively active state. "
            "This active monomer bypasses the need for upstream RAS activation or dimerization."
        ),
        "pathway_reasoning": {
            "pathway_reasoning": (
                "Somatic activation of the BRAF V600E kinase monomer drives continuous phosphorylation of MEK1/2. "
                "Active MEK subsequently phosphorylates ERK1/2, which translocates to the nucleus to trigger transcription "
                "of G1-S cell cycle proteins. This bypasses the typical ligand-activated MAPK controls, forcing uncontrolled cell growth."
            ),
            "affected_pathways": ["RAF-MEK-ERK Kinase Cascade", "MAPK Signaling Pathway"],
            "downstream_effects": "Constitutive ERK activation, transcription of proliferative transcription factors"
        },
        "therapies": [
            {
                "drug": "Vemurafenib",
                "drug_class": "BRAF Inhibitor",
                "rationale": "Selectively binds the ATP-binding site of mutated active V600E monomers, halting downstream MEK/ERK activation.",
                "evidence_level": "FDA Approved (High)"
            },
            {
                "drug": "Dabrafenib + Trametinib",
                "drug_class": "BRAF + MEK Inhibitor Combination",
                "rationale": "Combining BRAF and MEK inhibitors delays resistance pathways and reduces paradoxically activated skin lesions.",
                "evidence_level": "FDA Approved (High)"
            },
            {
                "drug": "Encorafenib + Cetuximab",
                "drug_class": "BRAF + EGFR Inhibitor Combination",
                "rationale": "Synergistically treats V600E colorectal cancer by blocking EGFR feedback loops.",
                "evidence_level": "FDA Approved (High)"
            }
        ],
        "validation": {
            "is_valid": True,
            "validation_score": 97.0,
            "verification_details": "Validated by ClinVar and DrugBank indications for BRAF V600E positive melanoma/colorectal oncology.",
            "contradiction_detected": False
        },
        "consensus": {
            "final_findings": (
                "BRAF V600E is a highly pathogenic somatic driver mutation leading to a constitutively active monomer "
                "and MAPK cascade hyperactivation."
            ),
            "disease_associations": ["Melanoma", "Colorectal Cancer", "Papillary Thyroid Carcinoma"],
            "final_recommendation": (
                "Prioritize combined BRAF/MEK inhibition therapy (e.g., Dabrafenib + Trametinib) for melanoma. "
                "For colorectal cancer, consider Encorafenib in combination with an anti-EGFR antibody (Cetuximab) to counter EGFR feedback reactivation."
            ),
            "confidence_score": 98.0
        },
        "reasoning_trace": [
            {"step": "Step 1: Variant Parsing", "detail": "Parsed somatic missense variant BRAF p.Val600Glu (V600E)."},
            {"step": "Step 2: Protein Disruption Map", "detail": "Determined activation loop phosphorylation mimicry, giving rise to active monomers."},
            {"step": "Step 3: Pathway Breakdown", "detail": "Identified direct RAF-MEK-ERK signal propagation bypassing upstream RAS controls."},
            {"step": "Step 4: Literature Retrieval", "detail": "Retrieved trials detailing targeted small-molecule inhibitors in BRAF mutated malignancies."},
            {"step": "Step 5: Therapy Targeting", "detail": "Recommended dual target BRAF + MEK combo pathways to suppress reactivation loops."},
            {"step": "Step 6: Clinical Validation", "detail": "Confirmed alignment with NCCN guidelines for melanoma and metastatic colorectal cancers."}
        ]
    }
}

def generate_local_llm_content(prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
    """Queries the local OpenAI-compatible API endpoint (like vLLM or Ollama)."""
    url = f"{LOCAL_LLM_API_BASE.rstrip('/')}/chat/completions"
    
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": messages,
        "temperature": 0.1,
    }
    
    if json_mode:
        # Reasoning models (like DeepSeek-R1) generate <think>...</think> tags first.
        # Forcing response_format={"type": "json_object"} causes local LLMs (like Ollama)
        # to fail, block thinking tokens, or return empty/whitespace responses.
        is_reasoning = any(term in LOCAL_LLM_MODEL.lower() for term in ["r1", "reasoning", "thinking", "qwq"])
        if is_reasoning:
            logger.info(f"Reasoning model detected ({LOCAL_LLM_MODEL}). Disabling API-level response_format constraints to allow `<think>` blocks.")
        else:
            payload["response_format"] = {"type": "json_object"}
        
    headers = {
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            res_data = response.read().decode("utf-8")
            res_json = json.loads(res_data)
            content = res_json["choices"][0]["message"]["content"]
            if json_mode:
                # Remove DeepSeek-R1 <think>...</think> blocks
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                # Remove markdown code blocks if present
                match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, flags=re.DOTALL)
                if match:
                    content = match.group(1).strip()
            return content
    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to local LLM at {url}: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error querying local LLM: {e}")
        raise e

def generate_gemini_content(prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
    """Wrapper calling the Gemini model or returning a message if error occurs."""
    if not HAS_GEMINI:
        raise RuntimeError("Gemini API key is missing. Simulation mode is active.")
        
    try:
        model_name = GEMINI_MODEL_FLASH
        
        # Structure model params
        generation_config = {}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"
            
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config=generation_config
        )
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API generation failed: {e}")
        raise e

def query_gemini_agent(agent_name: str, mutation_input: str, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """Invokes the local LLM first, falling back to Gemini API, and finally to simulation templates if both fail."""
    # Normalized search key for simulation profiles (used as final fallback)
    lookup_key = None
    for key in MOCK_PROFILES.keys():
        if key.lower() in mutation_input.lower():
            lookup_key = key
            break

    # If key is not found but mutation matches gene substrings, map them
    if not lookup_key:
        if "brca" in mutation_input.lower():
            lookup_key = "BRCA1 c.5266dupC"
        elif "egfr" in mutation_input.lower():
            lookup_key = "EGFR L858R"
        elif "braf" in mutation_input.lower():
            lookup_key = "BRAF V600E"

    # 1. Attempt Local LLM First (if configured)
    if USE_LOCAL_LLM:
        try:
            logger.info(f"[LOCAL LLM MODE] Querying local model for agent '{agent_name}' with: {mutation_input}")
            return generate_local_llm_content(user_prompt, system_instruction=system_prompt, json_mode=json_mode)
        except Exception as e:
            logger.warning(f"Local LLM query failed for '{agent_name}'. Falling back to Gemini: {e}")
            # Fall through to Gemini

    # 2. Attempt Live Gemini API (if available)
    if HAS_GEMINI:
        try:
            logger.info(f"[LIVE API MODE] Querying Gemini model for agent '{agent_name}' with: {mutation_input}")
            return generate_gemini_content(user_prompt, system_instruction=system_prompt, json_mode=json_mode)
        except Exception as e:
            logger.warning(f"Live Gemini API failed for '{agent_name}'. Falling back to simulation profile: {e}")
            # Fall through to simulation mode

    # 3. Final Fallback: Clinical Simulation Mode
    logger.info(f"[SIMULATION MODE] Agent '{agent_name}' resolving profile for target: {mutation_input}")
    return fetch_simulated_result(agent_name, lookup_key, mutation_input, json_mode)

def fetch_simulated_result(agent_name: str, lookup_key: str, raw_input: str, json_mode: bool) -> str:
    """Returns simulated response contents based on pre-defined clinical profiles."""
    profile = MOCK_PROFILES.get(lookup_key or "BRCA1 c.5266dupC")
    
    # Custom fallback logic if user enters a totally new mutation in demo mode
    is_custom = lookup_key is None
    
    if agent_name == "Mutation Analysis Agent":
        if is_custom:
            # Generate generic fallback analysis
            gene_match = re.match(r'^([A-Z0-9a-z\-]+)', raw_input.strip())
            gene = gene_match.group(1).upper() if gene_match else "UNKNOWN"
            res = {
                "gene": gene,
                "mutation_type": "Missense Variant (p.Xxx123Yyy)" if "c." not in raw_input else "Insertion/Deletion Variant",
                "clinical_significance": "Uncertain Significance (VUS)",
                "confidence_score": 75.0
            }
        else:
            res = profile["mutation_details"]
        return json.dumps(res) if json_mode else str(res)

    elif agent_name == "Gene & Protein Agent":
        if is_custom:
            return f"The entry represents a variant in the {raw_input} sequence. Analysis suggests disruption of protein transcription, yielding potential functional loss or aberrant kinase signal activity."
        return profile["protein_impact"]

    elif agent_name == "Pathway Analysis Agent":
        if is_custom:
            res = {
                "pathway_reasoning": "Disruption of normal gene pathways. Cascades linked to cell growth and survival regulation may be impaired, forcing cell lines to rely on accessory cellular checkpoints.",
                "affected_pathways": ["Cellular Signalling", "Signal Transduction Cascades"],
                "downstream_effects": "Altered gene transcription and cellular replication rates."
            }
        else:
            res = profile["pathway_reasoning"]
        return json.dumps(res) if json_mode else res["pathway_reasoning"]

    elif agent_name == "Therapy Recommendation Agent":
        if is_custom:
            res = [
                {
                    "drug": "Genomic-guided clinical trials",
                    "drug_class": "Experimental targeted therapy",
                    "rationale": "Uncertain clinical significance (VUS) warrants screening against active oncology phase trials.",
                    "evidence_level": "Preclinical (Low)"
                }
            ]
        else:
            res = profile["therapies"]
        return json.dumps(res) if json_mode else str(res)

    elif agent_name == "Evidence Validation Agent":
        if is_custom:
            res = {
                "is_valid": True,
                "validation_score": 60.0,
                "verification_details": "Variant lacks high-confidence database correlation. Preliminary predictions are modeled using computational tools.",
                "contradiction_detected": True
            }
        else:
            res = profile["validation"]
        return json.dumps(res) if json_mode else str(res)

    elif agent_name == "Consensus Agent":
        if is_custom:
            res = {
                "final_findings": f"Preliminary analysis compiled for target mutation {raw_input}. Variant is classified as a VUS.",
                "disease_associations": ["Associated Malignancies"],
                "final_recommendation": "Perform full gene sequencing and consult tumor board panels to evaluate clinical significance.",
                "confidence_score": 65.0
            }
        else:
            res = profile["consensus"]
        return json.dumps(res) if json_mode else str(res)

    return "No matching agent simulation profile."

# Healthcare AI Policy & Governance Corpus

## 1. Overview

This directory contains the curated document corpus used as the authoritative knowledge base for the **Enterprise Multi-Agent Copilot (Healthcare)** system.

The documents consist of regulatory, governance, policy, and industry reports related to Artificial Intelligence in healthcare. This corpus supports citation-grounded Retrieval-Augmented Generation (RAG) and multi-agent verification workflows in a regulated healthcare environment.

---

## 2. Document Inventory

The dataset includes the following documents:

- `Deloitte_AI_Digital_Health.pdf`
- `FDA_AI_Enabled_Device_Software_2025.pdf`
- `FDA_AI_ML_SaMD_Framework.pdf`
- `HIMSS_AI_Adoption_Hospitals.pdf`
- `IHI_AI_Implications_for_Safety.pdf`
- `McKinsey_AI_Healthcare_Value.pdf`
- `OECD_AI_in_Health_Risks.pdf`
- `OECD_Trustworthy_AI_in_Health.pdf`
- `WEF_AI_Healthcare_Report.pdf`
- `WHO_AI_Ethics_Governance.pdf`
- `WHO_AI_for_Health_2024.pdf`
- `WHO_AI_Reshaping_Health_Systems.pdf`

These documents represent perspectives from:

- Global regulatory authorities (FDA)
- International health governance organizations (WHO, OECD)
- Industry and consulting analyses (McKinsey, Deloitte)
- Healthcare IT organizations (HIMSS)
- Global policy forums (WEF)
- Patient safety institutions (IHI)

---

## 3. Selection Criteria

The corpus was selected based on the following principles:

- Institutional credibility  
- Regulatory relevance  
- Global healthcare governance representation  
- Coverage of ethics, risk, adoption, safety, and value dimensions  
- Suitability for evaluating citation-grounded AI systems  

The dataset intentionally focuses on governance and policy-level content rather than structured clinical datasets. This enables controlled experimentation in policy-aware reasoning and regulatory-constrained AI responses.

---

## 4. Integration in the RAG Pipeline

The documents in this directory are integrated into the system through the following process:

1. PDF loading and parsing  
2. Semantic chunking  
3. Embedding generation  
4. Storage of embeddings in the **ChromaDB vector database**

During query execution:

- The **Researcher Agent** retrieves Top-K relevant document chunks using semantic similarity search.
- The **Writer Agent** generates responses strictly grounded in retrieved evidence.
- The **Verifier Agent** validates citation presence and formatting.
- Regeneration is triggered if grounding or citation requirements are not satisfied.

---

## 5. Citation Enforcement Policy

All system-generated responses must:

- Be derived exclusively from retrieved document chunks  
- Include explicit source references  
- Avoid unsupported or speculative claims  

If sufficient evidence is not found within this corpus, the system must return:

> "Insufficient information in the knowledge base."

This policy is central to hallucination mitigation and evaluation integrity.

---

## 6. Experimental Purpose

This dataset enables controlled experimentation in:

- Citation-grounded LLM response generation  
- Multi-agent orchestration reliability  
- Verification loop effectiveness  
- Policy-aware reasoning in regulated domains  
- Hallucination control mechanisms  

---

## 7. Limitations

- The corpus does not include structured clinical or patient-level data.  
- Regulatory updates beyond publication dates are not dynamically tracked.  
- Domain scope is limited to governance, ethics, adoption, risk, and system-level analysis.  

# Advanced Resume Analyzer CLI


A command‑line tool that compares a résumé (PDF or DOCX) against a job description and generates:

-
 
**Similarity score**
 (TF‑IDF + cosine similarity)  
-
 
**NER‑based name extraction**
 (spaCy)  
-
 
**Section parsing**
 (Experience, Skills)  
-
 
**Contact extraction**
 (email & international phone)  
-
 
**Keyword gap analysis**
 (missing skills)  
-
 
**Actionable recommendations**
  
-
 
**Rich console tables**
 and colorized output  
-
 
**TXT and optional JSON reports**
  
-
 
**Batch mode**
, YAML config, logging, progress bars  

---

## Quick Start


1.
 
**Clone or download**
 this repo  
2.
 
**Install dependencies**
  
   
```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm


---

## Web UI (optional)


```bash
pip install streamlit
streamlit run app.py
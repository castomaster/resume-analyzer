# AI Resume Analyzer – CLI + Streamlit GUI

AI‑powered tool that compares a résumé (PDF / DOCX) with a job description and generates:

* **Similarity score** (TF‑IDF + cosine)
* **NER‑based name extraction** (spaCy)
* **Section parsing** (Experience, Skills)
* **Email & phone finder**
* **Keyword gap analysis**
* **Actionable recommendations**
* Batch‑mode CLI **and** drag‑and‑drop **web UI**

<p align="center">
  <a href="YOUR-DEMO-URL" target="_blank">
    <img src="docs/demo_screenshot.png" width="80%">
  </a>
</p>

---

## 🌐 Try it online

▶ **Live demo:** 
https://resume-analyzer-eensuzogku6mh96kz9at2h.streamlit.app/

---

## ⚡ Quick Start (CLI)

Open the document Installation & Usage.docx in the root folder

```bash
git clone https://github.com/castomaster/resume-analyzer.git
cd resume-analyzer
pip install -r requirements.txt
python -m spacy download en_core_web_sm

---



# single résumé
python src/resume_analyzer.py sample/resume.pdf --job_file sample/jd.txt

# batch mode
python src/resume_analyzer.py sample/ --batch --job_file sample/jd.txt

## 📦 Tech stack

| Part              | Library                            |
|-------------------|------------------------------------|
| **NLP / NER**     | spaCy 3                            |
| **Similarity**    | scikit‑learn TF‑IDF + cosine       |
| **PDF / DOCX**    | pdfplumber / python‑docx           |
| **UI**            | Streamlit 1                        |
| **Styling**       | rich tables, tqdm bars             |

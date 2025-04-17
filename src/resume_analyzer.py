"""
Advanced Resume Analyzer CLI Tool
=================================

This script compares a résumé (PDF or DOCX) against a job description,
producing similarity metrics and actionable recommendations.

Features:
 - PDF/DOCX parsing (pdfplumber, python-docx) with progress bars
 - NER-based name extraction via spaCy
 - Email & international phone extraction via regex
 - Flexible section parsing (Experience, Skills)
 - Semantic similarity: TF-IDF + cosine similarity (scikit-learn)
 - Keyword gap analysis (spaCy + TF-IDF)
 - Configurable thresholds and sections via YAML config
 - Colored, structured console output (rich)
 - Logging (file and console) with verbosity control
 - Batch mode for multiple résumés

Quick start:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python resume_analyzer.py path/to/resume.pdf \
    --job_file path/to/jd.txt --config config.yaml --batch resumes/ --json --verbose
```

requirements.txt:
```
pdfplumber
python-docx
spacy
scikit-learn
PyYAML
rich
tqdm
```

config.yaml (example):
```yaml
experience_min_words: 100
resume_max_words: 1500
top_keywords: 20
sections:
  experience:
    headers: ["Experience", "Work History", "Professional Experience"]
    stops: ["Skills", "Education", "Projects"]
  skills:
    headers: ["Skills", "Technical Skills"]
    stops: ["Experience", "Education", "Projects"]
``` 

"""
import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import pdfplumber
import spacy
import yaml
from docx import Document
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
console = Console()
logging.basicConfig(
    filename="analyzer.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    console.print("[red]spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm[/red]")
    sys.exit(1)

# Default config
DEFAULT_CONFIG = {
    'experience_min_words': 100,
    'resume_max_words': 1500,
    'top_keywords': 20,
    'sections': {
        'experience': {
            'headers': ["Experience", "Work History", "Professional Experience"],
            'stops': ["Skills", "Education", "Projects"]
        },
        'skills': {
            'headers': ["Skills", "Technical Skills"],
            'stops': ["Experience", "Education", "Projects"]
        }
    }
}

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------
def load_config(path: Path):
    if path and path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
            DEFAULT_CONFIG.update(cfg)
    return DEFAULT_CONFIG


def extract_text_resume(path: Path) -> str:
    ext = path.suffix.lower()
    text = []
    if ext == ".pdf":
        with pdfplumber.open(path) as pdf:
            for page in tqdm(pdf.pages, desc=f"Extracting PDF {path.name}"):
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
    elif ext == ".docx":
        doc = Document(path)
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
    else:
        console.print(f"[red]Unsupported format: {ext}[/red]")
        sys.exit(1)
    return "\n".join(text)


def extract_full_name(text: str) -> str:
    doc = nlp(text[:1000])
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            return ent.text
    # Fallback first line
    for line in text.splitlines():
        tokens = [w for w in line.split() if w.istitle()]
        if len(tokens) >= 2:
            return line.strip()
    return "Name Not Found"


def regex_contacts(text: str) -> list:
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"(?:\+?\d{1,3}[\s.-])?(?:\(?\d{3}\)?[\s.-])?\d{3}[\s.-]?\d{4}", text)
    contacts = []
    if emails:
        contacts.append("Emails: " + ", ".join(sorted(set(emails))))
    if phones:
        contacts.append("Phones: " + ", ".join(sorted(set(phones))))
    return contacts


def find_section(text: str, hdrs: list, stops: list) -> str:
    pattern = rf"(?i)({'|'.join(hdrs)})[:\n]?(.*?)(?=(?:{'|'.join(stops)})|$)"
    m = re.search(pattern, text, re.DOTALL)
    return m.group(2).strip() if m else ""


def tfidf_similarity(a: str, b: str) -> float:
    vec = TfidfVectorizer(stop_words='english')
    tfidf = vec.fit_transform([a, b])
    return round(float(cosine_similarity(tfidf[0], tfidf[1])[0][0] * 100), 2)


def top_keywords(text: str, n: int) -> set:
    doc = nlp(text.lower())
    kws = [tok.lemma_ for tok in doc if tok.pos_ in ("NOUN","PROPN") and not tok.is_stop]
    return set(kws[:n])

# ---------------------------------------------------------------------------
# Analysis and Reporting
# ---------------------------------------------------------------------------
def analyze_resume(resume_path: Path, jd_text: str, cfg: dict) -> dict:
    text = extract_text_resume(resume_path)
    words_count = len(text.split())

    result = {
        'candidate': extract_full_name(text),
        'contacts': regex_contacts(text),
        'experience': find_section(text, cfg['sections']['experience']['headers'], cfg['sections']['experience']['stops']),
        'skills': find_section(text, cfg['sections']['skills']['headers'], cfg['sections']['skills']['stops']),
        'match_pct': tfidf_similarity(text, jd_text),
        'recommendations': []
    }

    # Recommendations
    missing = top_keywords(jd_text, cfg['top_keywords']) - top_keywords(result['skills'], cfg['top_keywords'])
    if missing:
        result['recommendations'].append(f"Add missing skills: {', '.join(sorted(missing))}")
    if len(result['experience'].split()) < cfg['experience_min_words']:
        result['recommendations'].append("Provide more detail in your experience section.")
    if not result['contacts']:
        result['recommendations'].append("Add contact information (email/phone).")
    if words_count > cfg['resume_max_words']:
        result['recommendations'].append("Résumé is lengthy; consider shortening.")

    return result


def print_report(report: dict, to_json: bool = False):
    table = Table(title="Resume Analysis", box=box.SIMPLE)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Candidate", report['candidate'])
    for c in report['contacts'] or ["No contact info found"]:
        table.add_row("Contact", c)
    table.add_row("Match %", f"{report['match_pct']} %")
    console.print(table)

    console.print("[bold]Recommendations:[/bold]")
    if report['recommendations']:
        for rec in report['recommendations']:
            console.print(f" - {rec}")
    else:
        console.print(" - None 🎉")

    # Save text
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt = f"analysis_{timestamp}.txt"
    Path(txt).write_text(json.dumps(report, indent=2), encoding='utf-8')
    console.print(f"[green]Saved report to {txt}[/green]")

    # JSON
    if to_json:
        jfile = txt.replace('.txt', '.json')
        Path(jfile).write_text(json.dumps(report, indent=2), encoding='utf-8')
        console.print(f"[green]Saved JSON to {jfile}[/green]")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Advanced Resume Analyzer CLI")
    parser.add_argument('resume', type=Path, help="Path to résumé (.pdf/.docx) or directory for batch")
    parser.add_argument('--job_file', type=Path, help="Optional JD .txt file")
    parser.add_argument('--config', type=Path, help="YAML config file")
    parser.add_argument('--json', action='store_true', help="Save JSON output")
    parser.add_argument('--batch', action='store_true', help="Process all résumés in a folder")
    parser.add_argument('--verbose', action='store_true', help="Verbose logging to console")
    args = parser.parse_args()

    if  args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    cfg = load_config(args.config)

    # Load job description
    if args.job_file:
        jd_text = args.job_file.read_text(encoding='utf-8')
    else:
        console.print("Paste job description; end with blank line:")
        lines = []
        while True:
            line = input()
            if not line.strip(): break
            lines.append(line)
        jd_text = "\n".join(lines)

    paths = []
    if args.batch and args.resume.is_dir():
        for f in args.resume.iterdir():
            if f.suffix.lower() in ['.pdf', '.docx']:
                paths.append(f)
    else:
        paths = [args.resume]

    for p in paths:
        logger.info(f"Starting analysis for {p.name}")
        report = analyze_resume(p, jd_text, cfg)
        print_report(report, args.json)

if __name__ == '__main__':
    main()

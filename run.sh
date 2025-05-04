#!/usr/bin/env bash
# --- AI Resume Analyzer launcher (Unix) -----------------------------------

# 1. Create venv if missing
if [ ! -d ".venv" ]; then
  echo "[INFO] Creating virtual environment…"
  python3 -m venv .venv
fi

# 2. Activate venv
source .venv/bin/activate

# 3. Install deps (idempotent)
pip install --disable-pip-version-check -q -r requirements.txt

# 4. Download spaCy model if absent
python - <<'PY'
import importlib.util, subprocess, sys
spec = importlib.util.find_spec("en_core_web_sm")
sys.exit(0 if spec else 1)
PY
if [ $? -ne 0 ]; then
  echo "[INFO] Downloading spaCy model…"
  python -m spacy download en_core_web_sm
fi

# 5. Launch Streamlit
echo "[INFO] Starting AI Resume Analyzer…"
streamlit run App.py

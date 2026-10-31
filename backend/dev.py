"""Same-origin local demo: python -m uvicorn backend.dev:app --host 127.0.0.1 --port 4173.
Serves the static platform and the actual API from one process. No front-end proxy needed.
Production GitHub Pages still serves dist only; deploy app.py separately over HTTPS.
"""
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from .app import app

DIST=Path(__file__).resolve().parents[1]/'dist'
app.mount('/',StaticFiles(directory=DIST,html=True),name='geotwin_frontend')

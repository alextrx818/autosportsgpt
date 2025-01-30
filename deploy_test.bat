@echo off
cd /d "%~dp0"
git add app.yaml
git commit -m "Update configuration to use app-level environment variables"
git push
python fetch_all_logs.py

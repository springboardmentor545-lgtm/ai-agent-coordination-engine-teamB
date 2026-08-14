# Enterprise Workflow Platform - Module 2

A clean Module 2 implementation focused on enterprise tool integration, intelligent tool selection, action execution, validation, and error handling.

## Structure

enterprise_workflow_module2/
- agents/
- api/
- config/
- memory/
- prompts/
- tools/
- tests/
- .env.example
- .gitignore
- requirements.txt
- run.py

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:8000/docs

Example request:
POST /workflow/execute
```json
{"request":"calculate 25 * 4","session_id":"demo-01"}
```

The ZIP intentionally excludes virtual environments, Python caches, secrets, and other generated files.

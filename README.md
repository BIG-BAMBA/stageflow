# StageFlow API

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Variables d'environnement

- DATABASE_URL=sqlite:///./stageflow.db
- SECRET_KEY=dev-secret-key
- ALGORITHM=HS256
- ACCESS_TOKEN_EXPIRE_MINUTES=60

## Lancement local

```bash
uvicorn app.main:app --reload
```

## Tests

```bash
pytest
```

## Rôles

- student: view published offers, create applications, withdraw pending applications
- company: create draft offers, submit them, view applications for own offers
- program_manager: review offers, decide applications, view global statistics
- admin: manage users and roles

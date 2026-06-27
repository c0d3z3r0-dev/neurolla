# Deployment Guide

---

# Local Development

Install:

```bash
pip install -r requirements.txt
```

Run API:

```bash
uvicorn server.main:app --reload
```

Run bot:

```bash
python run_commander.py
```

---

# Production

Recommended:

- Docker
- Nginx
- PostgreSQL
- Redis
- Supervisor

---

# Hosting

Recommended:

- AWS
- DigitalOcean
- Railway
- Render

---

# Scaling

Use:

```text
Gunicorn + Uvicorn workers
```

For API scaling.

---

# Bot Persistence

Use:

```text
Supervisor
```

Or:

```text
PM2
```

To keep bot processes alive.
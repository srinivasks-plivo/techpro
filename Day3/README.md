# IVR System - Plivo Voice Integration

Production-ready Interactive Voice Response (IVR) system built with Flask, PostgreSQL, and Plivo.

## Architecture

```
Flask API ← Plivo Webhooks → Voice Call
    ↓
Redis (Sessions) + PostgreSQL (Persistent Storage)
```

**Stack:** Python 3.14 | Flask | SQLAlchemy | PostgreSQL | Redis | Plivo API

## Quick Start

### Prerequisites
- Python 3.14+
- PostgreSQL 15+
- Redis
- Plivo account with phone number

### Setup

```bash
# 1. Clone and enter directory
cd Day3

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials:
#   - PLIVO_AUTH_ID
#   - PLIVO_AUTH_TOKEN
#   - PLIVO_PHONE_NUMBER
#   - SALES_TRANSFER_NUMBER
#   - SUPPORT_TRANSFER_NUMBER
#   - WEBHOOK_BASE_URL (ngrok URL)

# 5. Initialize database
createdb ivr_db
python scripts/init_db.py
python scripts/seed_menus.py

# 6. Run application
python app.py  # Runs on port 5001

# 7. Expose to internet (for Plivo webhooks)
ngrok http 5001
```

### Plivo Configuration

Set these webhook URLs in your Plivo console:

- **Answer URL:** `https://your-ngrok-url.ngrok.dev/voice/incoming`
- **Hangup URL:** `https://your-ngrok-url.ngrok.dev/voice/hangup`
- **Method:** POST

## IVR Flow

```
Incoming Call
    ↓
"Welcome. Press 1 for Sales, or Press 2 for Support."
    ├─ Press 1 → Transfer to SALES_TRANSFER_NUMBER
    ├─ Press 2 → Transfer to SUPPORT_TRANSFER_NUMBER
    └─ Other   → "Invalid input. Press 1 or 2."
```

## Project Structure

```
Day3/
├── app.py                 # Flask app & webhook endpoints
├── config.py              # Environment configuration
├── models/                # SQLAlchemy models
│   ├── call_log.py        # Call records
│   ├── caller_history.py  # Caller aggregates
│   └── menu_config.py     # IVR menu definitions
├── services/              # Business logic
│   ├── ivr_service.py     # Call flow orchestration
│   ├── plivo_service.py   # XML generation
│   └── redis_service.py   # Session management
└── scripts/               # Database utilities
    ├── init_db.py         # Create tables
    └── seed_menus.py      # Load IVR menus
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/voice/incoming` | POST | Handle incoming calls |
| `/voice/input` | POST | Process DTMF digit input |
| `/voice/hangup` | POST | Handle call completion |
| `/health` | GET | Health check |

## Database Schema

**call_logs:** Individual call records (duration, status, user inputs)
**caller_history:** Aggregated caller stats (total calls, avg duration)
**menu_configurations:** IVR menu structure and routing

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://localhost/ivr_db` |
| `REDIS_HOST` | Redis host | `localhost` |
| `PLIVO_AUTH_ID` | Plivo auth ID | From Plivo console |
| `PLIVO_AUTH_TOKEN` | Plivo auth token | From Plivo console |
| `PLIVO_PHONE_NUMBER` | Plivo phone number | `+16172386217` |
| `SALES_TRANSFER_NUMBER` | Sales transfer destination | `+1234567890` |
| `SUPPORT_TRANSFER_NUMBER` | Support transfer destination | `+919019841867` |
| `WEBHOOK_BASE_URL` | Public webhook URL | `https://xxx.ngrok.dev` |

## Development

```bash
# Verify setup
python scripts/verify_setup.py

# Re-seed menus
python scripts/seed_menus.py

# Check logs
tail -f logs/app.log

# Database access
psql -d ivr_db
```

## Production Deployment

1. Replace ngrok with production domain
2. Set `FLASK_ENV=production` and `FLASK_DEBUG=False`
3. Use production WSGI server (gunicorn/uWSGI)
4. Configure SSL/TLS certificates
5. Set up database connection pooling
6. Enable Redis persistence
7. Configure log aggregation

## Testing

Call your Plivo number:
1. Listen to menu prompt
2. Press 1 or 2
3. Verify call transfers correctly
4. Check database for call logs

## Troubleshooting

**"Invalid Action URL" error:** Update `WEBHOOK_BASE_URL` in `.env` to your ngrok URL

**Call not answered:** Verify Plivo webhook URLs are correct and accessible

**Database connection failed:** Ensure PostgreSQL is running: `brew services list`

**Redis connection failed:** Start Redis: `redis-server`

## License

Proprietary

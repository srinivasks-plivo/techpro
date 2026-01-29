# IVR System - Interactive Voice Response

A production-ready IVR (Interactive Voice Response) system built with Flask, PostgreSQL, Redis, and Plivo Voice API.

## Overview

This project demonstrates a complete voice IVR system that:
- ✓ Handles incoming phone calls via Plivo
- ✓ Presents interactive multi-level menus
- ✓ Records caller inputs and call history
- ✓ Manages session state with Redis
- ✓ Persists all data to PostgreSQL
- ✓ Supports menu configuration without code changes

**Perfect for:** Learning voice APIs, understanding service architecture, building real-time systems.

---

## Prerequisites

Before you start, ensure you have:

### System Requirements
- **Python 3.8+** - Download from python.org
- **PostgreSQL 13+** - `brew install postgresql@15` (macOS)
- **Redis** - `brew install redis` (macOS)
- **Git** - For cloning the repository

### Accounts
- **Plivo Account** - Sign up at plivo.com for voice API credentials

### Tools (Optional but recommended)
- **TablePlus** - Database viewer for seeing PostgreSQL data
- **ngrok** - For exposing local Flask server to internet

---

## Quick Start (5 minutes)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Day3
```

### Step 2: Create Virtual Environment

```bash
# Create venv inside the project directory
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify (you should see (venv) in your terminal)
which python
```

### Step 3: Install Requirements

```bash
pip install -r requirements.txt

# Verify installation
pip list | grep -E "Flask|SQLAlchemy|redis|plivo"
```

### Step 4: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or use your favorite editor

# Required settings in .env:
# - DATABASE_URL=postgresql://user:password@localhost/ivr_db
# - REDIS_HOST=localhost
# - PLIVO_AUTH_ID=your_auth_id
# - PLIVO_AUTH_TOKEN=your_auth_token
# - PLIVO_PHONE_NUMBER=+15551234567
```

---

## Complete Setup Guide

### Step 1: Verify Prerequisites

```bash
# Check Python version
python --version

# Check PostgreSQL is installed
psql --version

# Check Redis is installed
redis-cli --version
```

### Step 2: Start Services

**Terminal 1 - Start Redis:**
```bash
redis-cli ping
# Should return: PONG

brew services start redis
```

**Terminal 2 - Start PostgreSQL:**
```bash
brew services start postgresql@15

# Verify it's running
psql -l
```

### Step 3: Create Database

```bash
# Create database for IVR
createdb ivr_db

# Verify
psql -l | grep ivr_db
```

### Step 4: Initialize Database Tables

```bash
python scripts/init_db.py

# Output should show:
# ✓ Database connection established
# ✓ Tables created successfully
# ✓ All 3 tables created successfully
```

### Step 5: Seed Default Menus

```bash
python scripts/seed_menus.py

# Output should show:
# ✓ main_menu created
# ✓ sales_menu created
# ✓ support_menu created
# ... (14 total menus)
# ✓ Created 14 menus successfully
```

### Step 6: Verify Setup

```bash
python scripts/verify_setup.py

# Should show:
# ✓ PostgreSQL connection successful
# ✓ Redis connection successful
# ✓ Configuration loaded
# ✓ Plivo credentials configured
# ✓ Menus loaded
# 🎉 All checks passed! System is ready.
```

---

## Running the Application

### Local Development (No Real Calls)

**Terminal 1 - Start Flask App:**
```bash
python app.py

# Output:
# * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

**Terminal 2 - Test with Local Webhook Simulation:**
```bash
python scripts/test_webhook.py

# Simulates a complete call flow without needing a real phone
# Output shows XML responses at each step
```

### With Real Plivo Calls

**Step 1: Expose Flask to Internet**
```bash
# Install ngrok if you haven't already
brew install ngrok

# In a new terminal, expose Flask
ngrok http 5000

# Copy the forwarding URL (e.g., https://abc123.ngrok.io)
```

**Step 2: Configure Plivo Webhooks**
1. Go to Plivo Console → Applications → Create New Application
2. Set:
   - **Answer URL:** `https://YOUR_NGROK_URL/webhooks/answer`
   - **Hangup URL:** `https://YOUR_NGROK_URL/webhooks/hangup`
3. Buy a phone number and assign it to the application

**Step 3: Test the IVR**
```bash
# Call your Plivo phone number and follow the menu prompts
# Your call data will be saved to PostgreSQL
```

---

## File Structure

```
Day3/
├── README.md                       # This file
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .env                           # Your actual credentials (git-ignored)
├── app.py                         # Flask web application
│
├── models/
│   ├── __init__.py
│   ├── database.py                # Database connection
│   ├── call_log.py                # CallLog model
│   ├── caller_history.py          # CallerHistory model
│   └── menu_config.py             # MenuConfiguration model
│
├── services/
│   ├── __init__.py
│   ├── redis_service.py           # Session management
│   ├── plivo_service.py           # XML generation
│   └── ivr_service.py             # IVR logic
│
├── scripts/
│   ├── init_db.py                 # Create database tables
│   ├── seed_menus.py              # Add default menus
│   ├── verify_setup.py            # Verify all connections
│   └── test_webhook.py            # Local testing
│
└── documentation/
    ├── FINAL_SUMMARY.txt          # Project completion summary
    ├── MODELS_EXPLANATION.md      # Database models guide
    ├── SERVICES_EXPLANATION.md    # Services architecture
    └── ... (more docs)
```

---

## Understanding the System

### Architecture Diagram

```
User's Phone → Plivo Voice Network
                     ↓
        HTTP POST /webhooks/answer
        HTTP POST /webhooks/input
        HTTP POST /webhooks/hangup
                     ↓
            Flask Application
                     ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
    IVR Service  Redis Service  PostgreSQL
    (Orchestrate) (Session)     (Permanent Data)
```

### How a Call Works

1. **User calls your Plivo number**
2. **Plivo → Flask** POST `/webhooks/answer`
   - Flask creates Redis session for the call
   - Loads main menu from PostgreSQL
   - Returns XML with main menu message
3. **Plivo plays menu** and waits for digit input
4. **User presses digit (e.g., 1)**
5. **Plivo → Flask** POST `/webhooks/input` with digit
   - Flask retrieves session from Redis
   - Validates the digit
   - Determines next menu or action
   - Returns XML for next step
6. **Steps 3-5 repeat** until call ends
7. **User hangs up or transfers**
8. **Plivo → Flask** POST `/webhooks/hangup`
   - Flask saves complete call data to PostgreSQL
   - Updates caller history
   - Deletes Redis session
   - Call complete ✓

---

## Common Tasks

### View Call Logs

```bash
# Using psql (PostgreSQL command line)
psql -U your_user -d ivr_db

# Inside psql:
SELECT * FROM call_logs;
SELECT * FROM caller_history;
SELECT * FROM menu_configurations;
```

Or use **TablePlus** for a GUI:
1. Connect to PostgreSQL
2. Browse call_logs, caller_history, menu_configurations tables

### Change Menu Messages

```bash
# Edit directly in database using TablePlus
# Or use SQL:
UPDATE menu_configurations
SET message = 'New message here'
WHERE menu_id = 'main_menu';
```

### Clear Session Data

```bash
# Clear all active call sessions from Redis
redis-cli FLUSHDB

# Warning: This will end all active calls!
```

### Check Active Sessions

```bash
redis-cli
> KEYS ivr:session:*
> GET ivr:session:abc-123
> QUIT
```

---

## Troubleshooting

### Connection Errors

**PostgreSQL connection failed:**
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL
brew services start postgresql@15

# Verify connection
psql -l
```

**Redis connection failed:**
```bash
# Check if Redis is running
brew services list | grep redis

# Start Redis
brew services start redis

# Test connection
redis-cli ping  # Should return PONG
```

### Database Errors

**Tables don't exist:**
```bash
# Recreate tables
python scripts/init_db.py
```

**Menus are empty:**
```bash
# Seed default menus
python scripts/seed_menus.py
```

**Environment variables not loading:**
```bash
# Check .env file exists in project root
ls -la .env

# Verify format
cat .env | grep PLIVO_AUTH_ID
```

### Plivo Webhook Issues

**"Connection refused" from Plivo:**
- Flask app not running: `python app.py`
- Wrong ngrok URL in Plivo console
- ngrok expired (expires after 8 hours): run `ngrok http 5000` again

**"Invalid authentication":**
- Wrong Plivo credentials in .env
- Verify in Plivo console your auth ID and token

---

## Project Documentation

For detailed information, see:

- **FINAL_SUMMARY.txt** - Complete project overview and setup guide
- **MODELS_EXPLANATION.md** - Deep dive into database schema
- **SERVICES_EXPLANATION.md** - Service layer architecture
- **FLASK_EXPLANATION.md** - Flask application integration
- **QUICK_REFERENCE.txt** - Quick lookup guide

---

## What You'll Learn

✓ How voice APIs work (Plivo webhooks)
✓ Session management with Redis
✓ Database design (PostgreSQL + SQLAlchemy)
✓ Service-oriented architecture
✓ Flask webhook integration
✓ Configuration-driven applications
✓ Error handling and logging
✓ Call orchestration and state machines

---

## Next Steps

### To Run Real Calls
1. Get Plivo API credentials
2. Buy a Plivo phone number
3. Set up ngrok
4. Configure webhook URLs in Plivo console
5. Start Flask and make a call!

### To Extend the System
- Add more menu branches
- Implement call recording
- Add SMS notifications
- Build admin dashboard
- Implement speech recognition
- Add multi-language support

---

## Support

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Run verification script:** `python scripts/verify_setup.py`
3. **Check Flask logs** for error messages
4. **Review FINAL_SUMMARY.txt** for detailed setup info

---

## License

This is an educational project built as part of the TECHPRO internship program.

---

## Environment Variables Reference

```bash
# .env file settings

# Database
DATABASE_URL=postgresql://username:password@localhost/ivr_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Plivo Voice API
PLIVO_AUTH_ID=your_auth_id_here
PLIVO_AUTH_TOKEN=your_auth_token_here
PLIVO_PHONE_NUMBER=+15551234567

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# IVR Settings
DEFAULT_TIMEOUT=5
MAX_RETRIES=3
SESSION_TTL=1800
```

---

**Happy coding! 🚀**

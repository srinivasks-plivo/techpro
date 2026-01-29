# Flask Application - Webhook Integration

## Overview

The Flask application is the web server that connects Plivo to your IVR services. It receives webhook calls from Plivo and routes them to the appropriate service handlers.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   PLIVO (Voice Network)              │
└────────────────────┬─────────────────────────────────┘
                     │
                     │ HTTP POST (webhook)
                     │
         ┌───────────▼──────────────┐
         │  Flask Web Server        │
         │  (app.py)                │
         ├────────────────────────┤
         │ /webhooks/answer       │ ← Incoming call
         │ /webhooks/input        │ ← Digit pressed
         │ /webhooks/hangup       │ ← Call ended
         │ /health                │ ← Health check
         └───────────┬──────────────┘
                     │
         ┌───────────▼──────────────┐
         │  IVR Service            │
         │  (Orchestrator)         │
         │                         │
         │ handle_incoming_call()  │
         │ handle_digit_input()    │
         │ handle_hangup()         │
         └───────────┬──────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌──────────┐  ┌─────────┐
    │ Redis  │  │  Plivo   │  │ Models  │
    │Service │  │ Service  │  │(Database)
    └────────┘  └──────────┘  └─────────┘
```

## Request/Response Cycle

### Incoming Call Flow

```
1. USER CALLS PLIVO NUMBER
   ↓
   Plivo detects incoming call

2. PLIVO MAKES WEBHOOK CALL
   POST /webhooks/answer
   {
       "CallUUID": "4f3a4e5c-b2d8-4a7f-9c1e-3b8f6a9d2e1c",
       "From": "+15551234567",
       "To": "+15559876543",
       "Direction": "inbound",
       "CallStatus": "ringing"
   }

3. FLASK RECEIVES REQUEST
   app.route('/webhooks/answer') triggers

4. FLASK CALLS IVR SERVICE
   ivr_service.handle_incoming_call(call_uuid, from, to)

5. IVR SERVICE:
   - Creates Redis session
   - Loads main_menu from database
   - Calls Plivo Service to generate XML

6. PLIVO SERVICE RETURNS
   <Response>
       <GetDigits action="/webhooks/input" timeout="5">
           <Speak>Press 1 for Sales...</Speak>
       </GetDigits>
   </Response>

7. FLASK RETURNS XML TO PLIVO
   Plivo receives XML

8. PLIVO EXECUTES XML
   - Speaks message to caller
   - Waits for digit input

9. USER PRESSES DIGIT
   ↓
   Plivo detects digit press

10. PLIVO MAKES WEBHOOK CALL
    POST /webhooks/input
    {
        "CallUUID": "4f3a4e5c-b2d8-4a7f-9c1e-3b8f6a9d2e1c",
        "Digits": "1",
        "Duration": "5"
    }

11. (Cycle repeats from step 3 for each digit)

12. CALL ENDS
    Plivo calls /webhooks/hangup
    {
        "CallUUID": "4f3a4e5c-b2d8-4a7f-9c1e-3b8f6a9d2e1c",
        "HangupCause": "NORMAL_CLEARING",
        "Duration": "330",
        "CallStatus": "completed"
    }

13. FLASK CALLS IVR SERVICE
    ivr_service.handle_hangup(call_uuid, cause, duration)

14. IVR SERVICE:
    - Gets session from Redis
    - Saves to CallLog table
    - Updates CallerHistory table
    - Deletes Redis session

15. FLASK RETURNS 200 OK
    (No XML needed for hangup)

16. CALL COMPLETE
    Data is now permanently stored in database
```

## Flask Endpoints

### 1. POST /webhooks/answer

**Purpose:** Handle incoming call

**Called by:** Plivo when someone dials your phone number

**Receives:**
- `CallUUID` - Unique call identifier
- `From` - Caller's phone number
- `To` - Your Plivo phone number
- `Direction` - 'inbound' or 'outbound'
- `CallStatus` - Call state

**Returns:** XML string (Plivo will execute it)

**What it does:**
```python
def webhook_answer():
    1. Extract parameters from request
    2. Validate parameters
    3. Call ivr_service.handle_incoming_call()
    4. Return XML to Plivo
    5. If error: Return error XML (graceful degradation)
```

**Example Code:**
```python
@app.route('/webhooks/answer', methods=['POST'])
def webhook_answer():
    call_uuid = request.form.get('CallUUID')
    from_number = request.form.get('From')
    to_number = request.form.get('To')

    xml_response = ivr_service.handle_incoming_call(
        call_uuid=call_uuid,
        from_number=from_number,
        to_number=to_number
    )

    return Response(xml_response, mimetype='application/xml')
```

### 2. POST /webhooks/input

**Purpose:** Handle user input (digit pressed)

**Called by:** Plivo when user presses a button

**Receives:**
- `CallUUID` - Unique call identifier
- `Digits` - What digit(s) user pressed
- `Duration` - How long into call

**Returns:** XML string (next menu, transfer, hangup, or error)

**What it does:**
```python
def webhook_input():
    1. Extract parameters from request
    2. Validate parameters
    3. Call ivr_service.handle_digit_input()
    4. Return XML to Plivo
    5. If error: Return error XML
```

**Example Code:**
```python
@app.route('/webhooks/input', methods=['POST'])
def webhook_input():
    call_uuid = request.form.get('CallUUID')
    digits = request.form.get('Digits')

    xml_response = ivr_service.handle_digit_input(
        call_uuid=call_uuid,
        digit=digits
    )

    return Response(xml_response, mimetype='application/xml')
```

### 3. POST /webhooks/hangup

**Purpose:** Handle call end

**Called by:** Plivo when the call ends

**Receives:**
- `CallUUID` - Unique call identifier
- `HangupCause` - Why call ended (NORMAL_CLEARING, BUSY, etc.)
- `Duration` - Call length in seconds
- `CallStatus` - Final call status

**Returns:** Empty 200 OK response (no XML needed)

**What it does:**
```python
def webhook_hangup():
    1. Extract parameters from request
    2. Validate parameters
    3. Call ivr_service.handle_hangup()
       - Saves session to CallLog (permanent)
       - Updates CallerHistory (permanent)
       - Deletes Redis session (cleanup)
    4. Return 200 OK
    5. If error: Still return 200 OK (to prevent retry)
```

**Example Code:**
```python
@app.route('/webhooks/hangup', methods=['POST'])
def webhook_hangup():
    call_uuid = request.form.get('CallUUID')
    hangup_cause = request.form.get('HangupCause')
    duration = int(request.form.get('Duration', 0))

    ivr_service.handle_hangup(
        call_uuid=call_uuid,
        hangup_cause=hangup_cause,
        duration=duration
    )

    return Response('', status=200)
```

### 4. GET /health

**Purpose:** Health check endpoint

**Called by:** Monitoring systems or manual testing

**Returns:** JSON with service status

**Example Response:**
```json
{
    "status": "healthy",
    "timestamp": "2026-01-29T10:00:00Z",
    "redis": "healthy",
    "database": "healthy"
}
```

### 5. GET /

**Purpose:** Basic info page

**Returns:** HTML page with endpoint information

## Error Handling

### Strategy

The Flask app handles errors gracefully:

**For /webhooks/answer and /webhooks/input:**
- If error: Return XML that speaks error message and hangs up
- This ensures caller hears something instead of silence

**For /webhooks/hangup:**
- If error: Still return 200 OK
- Prevents Plivo from retrying the webhook
- Call data may be incomplete but won't cause cascading errors

### Common Errors

**Missing Parameters:**
```python
if not call_uuid or not from_number:
    return error_xml  # "Invalid parameters"
```

**Service Failure:**
```python
try:
    xml = ivr_service.handle_incoming_call(...)
except Exception as e:
    logger.error(f"Service failed: {e}")
    return error_xml  # "System unavailable"
```

**Redis Down:**
```python
session = redis_service.get_session(call_uuid)
if session is None:
    return error_xml  # "Session expired"
```

## Logging

The Flask app logs everything for debugging:

```python
logger.info("📞 ANSWER WEBHOOK")
logger.info(f"   CallUUID: {call_uuid}")
logger.info(f"   From: {from_number}")
logger.info(f"   To: {to_number}")
logger.debug(f"   XML: {xml_response[:100]}...")
```

**Log Levels:**
- `DEBUG` - Detailed info (request/response details)
- `INFO` - Important events (webhook calls, service calls)
- `WARNING` - Something unexpected (invalid input, service degradation)
- `ERROR` - Actual errors (exceptions, service failures)

## Running the Flask App

### Start Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your Plivo, database, Redis settings

# Make sure Redis and PostgreSQL are running
redis-cli ping
psql -l

# Run the app
python app.py
```

**Output:**
```
🚀 Starting IVR System Flask Application
   Environment: development
   Debug: True
   Database: postgresql://...
   Redis: redis://localhost:6379/0
 * Running on http://0.0.0.0:5000/
```

### Expose to Internet (For Real Plivo Webhooks)

```bash
# Install ngrok (if not already installed)
brew install ngrok

# Start ngrok in a new terminal
ngrok http 5000

# ngrok will show a URL like:
# Forwarding    https://abc123.ngrok.io -> http://localhost:5000

# Use this URL in Plivo console:
# Answer URL: https://abc123.ngrok.io/webhooks/answer
# Hangup URL: https://abc123.ngrok.io/webhooks/hangup
```

## Testing the Webhooks Locally

### Test /webhooks/answer

```bash
curl -X POST http://localhost:5000/webhooks/answer \
  -d "CallUUID=test-123" \
  -d "From=+15551234567" \
  -d "To=+15559876543" \
  -d "CallStatus=ringing"
```

**Expected Response:** XML with main menu

### Test /webhooks/input

```bash
curl -X POST http://localhost:5000/webhooks/input \
  -d "CallUUID=test-123" \
  -d "Digits=1"
```

**Expected Response:** XML with next menu or action

### Test /health

```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "redis": "healthy",
  "database": "healthy"
}
```

## Integration with Services

### How Flask Calls Services

```python
# Import services
from services.ivr_service import ivr_service
from services.redis_service import redis_service
from services.plivo_service import plivo_service

# In webhook handler
xml = ivr_service.handle_incoming_call(call_uuid, from_num, to_num)

# Inside IVR Service, it calls:
# - redis_service.create_session()
# - Models to load menu
# - plivo_service.generate_menu_xml()
# - And returns XML to Flask
# - Flask returns XML to Plivo
```

**The Flow:**
```
Flask → IVR Service → Redis Service
                    → Models (Database)
                    → Plivo Service
                    → back to Flask
                    → back to Plivo
```

## Security Considerations

### 1. Validate Plivo Signature (Optional but Recommended)

Plivo can sign requests so you know they're from Plivo:

```python
import plivo

def validate_plivo_signature(request):
    signature = request.headers.get('X-Plivo-Signature')
    uri = request.url
    params = request.form.to_dict()

    expected = plivo.utils.compute_signature(
        uri,
        params,
        PLIVO_AUTH_TOKEN
    )

    return signature == expected
```

### 2. Rate Limiting

Prevent abuse by limiting requests:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/webhooks/answer', methods=['POST'])
@limiter.limit("100/minute")
def webhook_answer():
    ...
```

### 3. HTTPS in Production

Always use HTTPS in production:

```bash
# Use reverse proxy like Nginx with SSL
# Or use production app server like Gunicorn with SSL
gunicorn --certfile=/path/to/cert --keyfile=/path/to/key app:app
```

## Performance Considerations

### 1. Async Processing for Heavy Operations

For database saves, use background tasks:

```python
from celery import Celery

@app.route('/webhooks/hangup', methods=['POST'])
def webhook_hangup():
    # Return immediately
    save_call_async.delay(call_uuid, data)
    return Response('', status=200)

@app.task
def save_call_async(call_uuid, data):
    # Save to database in background
    ivr_service.handle_hangup(...)
```

### 2. Response Time Constraints

Plivo expects response within 20 seconds:

```python
# Make sure operations are fast
# - Redis queries: milliseconds ✓
# - Database queries: milliseconds ✓
# - Plivo XML generation: microseconds ✓
# Total: < 100ms typically ✓
```

### 3. Connection Pooling

Already handled by:
- SQLAlchemy (database pool)
- Redis (connection pool)

## Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With SSL
gunicorn -w 4 -b 0.0.0.0:5000 \
  --certfile=/path/to/cert.pem \
  --keyfile=/path/to/key.pem \
  app:app
```

### Using Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /webhooks/ {
        proxy_pass http://localhost:5000;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}
```

### Environment Variables

Production uses different settings than development:

```bash
# .env (production)
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://prod_user:password@prod_db:5432/ivr
REDIS_HOST=prod_redis_host
REDIS_PORT=6379
```

## Monitoring

### Check App is Running

```bash
# Manual check
curl http://localhost:5000/health

# Automated (add to monitoring script)
curl -f http://localhost:5000/health || systemctl restart ivr-app
```

### Monitor Logs

```bash
# View logs in real-time
tail -f app.log

# Search for errors
grep ERROR app.log

# Count webhook calls
grep "WEBHOOK" app.log | wc -l
```

## Summary

The Flask application:
- ✓ Receives Plivo webhooks (3 endpoints)
- ✓ Routes calls to IVR service
- ✓ Returns XML responses
- ✓ Handles errors gracefully
- ✓ Logs everything
- ✓ Provides health checks
- ✓ Integrates all services

**Next steps:**
1. Configure .env file with credentials
2. Start Redis and PostgreSQL
3. Initialize database (scripts)
4. Seed default menus (scripts)
5. Run `python app.py`
6. Test with `curl` or ngrok
7. Configure Plivo webhooks
8. Test with real calls!

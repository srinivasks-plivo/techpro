"""
Flask Web Server - IVR System Main Application

WHAT THIS DOES:
================
This is the main web server that handles Plivo webhooks.

When someone calls your Plivo number:
1. Plivo makes HTTP POST to /webhooks/answer
2. We respond with XML (via services)
3. User presses digit → Plivo calls /webhooks/input
4. We respond with next XML
5. Call ends → Plivo calls /webhooks/hangup
6. We save to database and cleanup

WEBHOOK FLOW:
=============
                    PLIVO (External Service)
                             │
                 (1) Call arrives
                             │
                    ┌────────▼────────┐
                    │ /webhooks/answer│
                    └────────┬────────┘
                             │
                    ┌────────▼──────────┐
                    │ User presses digit│
                    └────────┬──────────┘
                             │
                    ┌────────▼────────┐
                    │ /webhooks/input │
                    └────────┬────────┘
                             │
                    (repeat until call ends)
                             │
                    ┌────────▼─────────┐
                    │ /webhooks/hangup │
                    └──────────────────┘
"""

from flask import Flask, request, Response
from datetime import datetime
import logging
import json

# Import our services and models
from config import get_config
from services.ivr_service import ivr_service
from services.redis_service import redis_service
from models import init_db

# ===== CONFIGURATION =====
config = get_config()

# ===== CREATE FLASK APP =====
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# ===== LOGGING SETUP =====
# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===== WEBHOOK ENDPOINTS =====

@app.route('/webhooks/answer', methods=['POST'])
def webhook_answer():
    """
    Handle incoming call.

    Called by Plivo when someone dials your phone number.

    Plivo sends:
        CallUUID - Unique call identifier
        From - Caller's phone number
        To - Your Plivo phone number
        Direction - 'inbound' or 'outbound'
        CallStatus - 'ringing', 'answered', etc.

    We need to:
        1. Extract parameters from request
        2. Call IVR service to handle incoming call
        3. Return XML response to Plivo

    Returns:
        XML string (Plivo will parse and execute it)

    Example Plivo Request:
        POST /webhooks/answer
        {
            "CallUUID": "4f3a4e5c-b2d8-4a7f-9c1e-3b8f6a9d2e1c",
            "From": "+15551234567",
            "To": "+15559876543",
            "Direction": "inbound",
            "CallStatus": "ringing"
        }
    """
    try:
        # Extract parameters from Plivo's request
        call_uuid = request.form.get('CallUUID')
        from_number = request.form.get('From')
        to_number = request.form.get('To')
        call_status = request.form.get('CallStatus')

        # Log for debugging
        logger.info(f"📞 ANSWER WEBHOOK")
        logger.info(f"   CallUUID: {call_uuid}")
        logger.info(f"   From: {from_number}")
        logger.info(f"   To: {to_number}")
        logger.info(f"   Status: {call_status}")

        # Validate required parameters
        if not call_uuid or not from_number or not to_number:
            logger.error("❌ Missing required parameters")
            error_xml = (
                '<Response>'
                '<Speak>Invalid call parameters</Speak>'
                '<Hangup />'
                '</Response>'
            )
            return Response(error_xml, mimetype='application/xml')

        # Call IVR service to handle incoming call
        # This will:
        # - Create Redis session
        # - Load main menu
        # - Generate XML response
        xml_response = ivr_service.handle_incoming_call(
            call_uuid=call_uuid,
            from_number=from_number,
            to_number=to_number
        )

        logger.info(f"✓ Returning XML response")
        logger.debug(f"   XML: {xml_response[:100]}...")

        # Return XML response to Plivo
        return Response(xml_response, mimetype='application/xml')

    except Exception as e:
        logger.error(f"❌ Error in answer webhook: {str(e)}", exc_info=True)
        # Return error XML to Plivo
        error_xml = (
            '<Response>'
            '<Speak>An error occurred. Please try again later.</Speak>'
            '<Hangup />'
            '</Response>'
        )
        return Response(error_xml, mimetype='application/xml')


@app.route('/webhooks/input', methods=['POST'])
def webhook_input():
    """
    Handle user input (digit pressed).

    Called by Plivo when user presses a digit.

    Plivo sends:
        CallUUID - Unique call identifier
        Digits - What digit(s) user pressed
        Duration - How long caller has been on call

    We need to:
        1. Extract parameters from request
        2. Call IVR service to handle digit input
        3. Generate response (next menu, transfer, hangup, etc.)
        4. Return XML response to Plivo

    Returns:
        XML string (Plivo will parse and execute it)

    Example Plivo Request:
        POST /webhooks/input
        {
            "CallUUID": "4f3a4e5c-b2d8-4a7f-9c1e-3b8f6a9d2e1c",
            "Digits": "1",
            "Duration": "5"
        }
    """
    try:
        # Extract parameters from Plivo's request
        call_uuid = request.form.get('CallUUID')
        digits = request.form.get('Digits')
        duration = request.form.get('Duration', 0)

        # Log for debugging
        logger.info(f"🔘 INPUT WEBHOOK")
        logger.info(f"   CallUUID: {call_uuid}")
        logger.info(f"   Digits: {digits}")
        logger.info(f"   Duration: {duration}s")

        # Validate required parameters
        if not call_uuid or not digits:
            logger.error("❌ Missing required parameters")
            error_xml = (
                '<Response>'
                '<Speak>Invalid input parameters</Speak>'
                '</Response>'
            )
            return Response(error_xml, mimetype='application/xml')

        # Call IVR service to handle digit input
        # This will:
        # - Get session from Redis
        # - Validate digit
        # - Determine next action (menu, transfer, hangup)
        # - Generate XML response
        xml_response = ivr_service.handle_digit_input(
            call_uuid=call_uuid,
            digit=digits  # User pressed this digit
        )

        logger.info(f"✓ Returning XML response")
        logger.debug(f"   XML: {xml_response[:100]}...")

        # Return XML response to Plivo
        return Response(xml_response, mimetype='application/xml')

    except Exception as e:
        logger.error(f"❌ Error in input webhook: {str(e)}", exc_info=True)
        # Return error XML to Plivo
        error_xml = (
            '<Response>'
            '<Speak>An error occurred processing your input. Please try again.</Speak>'
            '</Response>'
        )
        return Response(error_xml, mimetype='application/xml')


@app.route('/webhooks/hangup', methods=['POST'])
def webhook_hangup():
    """
    Handle call end.

    Called by Plivo when the call ends for any reason.

    Plivo sends:
        CallUUID - Unique call identifier
        HangupCause - Why did call end? ('NORMAL_CLEARING', 'BUSY', etc.)
        Duration - How long was the call in seconds
        CallStatus - Final status of call

    We need to:
        1. Extract parameters from request
        2. Call IVR service to handle call end
        3. This will:
           - Get session from Redis
           - Save to CallLog (permanent)
           - Update CallerHistory (permanent)
           - Delete session from Redis (cleanup)
        4. Return empty 200 OK response (no XML needed for hangup)

    Returns:
        Empty 200 OK response

    Example Plivo Request:
        POST /webhooks/hangup
        {
            "CallUUID": "4f3a4e5c-b2d8-4a7f-9c1e-3b8f6a9d2e1c",
            "HangupCause": "NORMAL_CLEARING",
            "Duration": "330",
            "CallStatus": "completed"
        }
    """
    try:
        # Extract parameters from Plivo's request
        call_uuid = request.form.get('CallUUID')
        hangup_cause = request.form.get('HangupCause')
        duration = request.form.get('Duration', 0)
        call_status = request.form.get('CallStatus')

        # Log for debugging
        logger.info(f"📵 HANGUP WEBHOOK")
        logger.info(f"   CallUUID: {call_uuid}")
        logger.info(f"   Cause: {hangup_cause}")
        logger.info(f"   Duration: {duration}s")
        logger.info(f"   Status: {call_status}")

        # Validate required parameters
        if not call_uuid:
            logger.error("❌ Missing CallUUID parameter")
            return Response('', status=400)

        # Convert duration to integer
        try:
            duration = int(duration)
        except (ValueError, TypeError):
            duration = 0

        # Call IVR service to handle call end
        # This will:
        # - Get session from Redis
        # - Save session data to CallLog (permanent)
        # - Update CallerHistory (permanent)
        # - Delete session from Redis (cleanup)
        ivr_service.handle_hangup(
            call_uuid=call_uuid,
            hangup_cause=hangup_cause,
            duration=duration
        )

        logger.info(f"✓ Hangup processing complete")

        # Return 200 OK (no XML needed for hangup)
        return Response('', status=200)

    except Exception as e:
        logger.error(f"❌ Error in hangup webhook: {str(e)}", exc_info=True)
        # Still return 200 OK so Plivo doesn't retry
        return Response('', status=200)


# ===== HEALTH CHECK ENDPOINT =====

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Use this to verify the app is running and services are available.

    Tests:
    - Redis connection (ping)
    - Database connection (query)
    - Basic system status

    Returns:
        JSON with status information
    """
    import json

    try:
        logger.info("🏥 HEALTH CHECK")

        # Test Redis
        redis_status = "healthy"
        try:
            if redis_service.ping():
                logger.info("   ✓ Redis: OK")
            else:
                redis_status = "unhealthy"
                logger.warning("   ⚠️  Redis: Not responding")
        except Exception as e:
            redis_status = "error"
            logger.error(f"   ❌ Redis error: {str(e)}")

        # Test Database
        db_status = "healthy"
        try:
            from models.database import SessionLocal
            from sqlalchemy import text
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("   ✓ Database: OK")
        except Exception as e:
            db_status = "error"
            logger.error(f"   ❌ Database error: {str(e)}")

        # Build response
        overall_status = "healthy" if (redis_status == "healthy" and db_status == "healthy") else "degraded"

        health_response = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "redis": redis_status,
            "database": db_status,
            "uptime": "TBD"
        }

        logger.info(f"   Overall: {overall_status}")
        return json.dumps(health_response), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        logger.error(f"❌ Error in health check: {str(e)}", exc_info=True)
        return json.dumps({"status": "error", "error": str(e)}), 500, {'Content-Type': 'application/json'}


# ===== BASIC ROUTES =====

@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint - just a basic info page.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>IVR System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .info { background: #f0f0f0; padding: 20px; border-radius: 5px; }
            code { background: #ddd; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🎯 IVR System</h1>
        <div class="info">
            <h2>Endpoints:</h2>
            <ul>
                <li><code>/webhooks/answer</code> - Incoming call handler (POST)</li>
                <li><code>/webhooks/input</code> - Digit input handler (POST)</li>
                <li><code>/webhooks/hangup</code> - Call end handler (POST)</li>
                <li><code>/health</code> - Health check (GET)</li>
            </ul>
            <h2>Status:</h2>
            <p>✓ Application is running</p>
            <p>Check <code>/health</code> for service status</p>
        </div>
    </body>
    </html>
    """
    return html


# ===== ALIAS ROUTES (for /voice/* -> /webhooks/*) =====

@app.route('/voice/incoming', methods=['POST'])
def voice_incoming():
    """Alias for /webhooks/answer"""
    return webhook_answer()

@app.route('/voice/input', methods=['POST'])
def voice_input():
    """Alias for /webhooks/input"""
    return webhook_input()

@app.route('/voice/hangup', methods=['POST'])
def voice_hangup():
    """Alias for /webhooks/hangup"""
    return webhook_hangup()


# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    logger.warning(f"404 Not Found: {request.path}")
    return json.dumps({"error": "Not found", "path": request.path}), 404, {'Content-Type': 'application/json'}


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    logger.error(f"500 Internal Server Error: {str(error)}", exc_info=True)
    return json.dumps({"error": "Internal server error"}), 500, {'Content-Type': 'application/json'}


# ===== APPLICATION STARTUP =====

@app.before_request
def log_request():
    """Log all incoming requests."""
    logger.debug(f"→ {request.method} {request.path}")


@app.after_request
def log_response(response):
    """Log all outgoing responses."""
    logger.debug(f"← {response.status_code}")
    return response


# ===== MAIN ENTRY POINT =====

if __name__ == '__main__':
    """
    Start the Flask web server.

    Usage:
        python app.py

    The server will start on http://localhost:5000

    To expose to internet (for Plivo webhooks):
        ngrok http 5000
        # Then use ngrok URL in Plivo console
    """
    logger.info("🚀 Starting IVR System Flask Application")
    logger.info(f"   Environment: {config.FLASK_ENV}")
    logger.info(f"   Debug: {config.FLASK_DEBUG}")
    logger.info(f"   Database: {config.DATABASE_URL}")
    logger.info(f"   Redis: {config.REDIS_URL}")

    # Run Flask app
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,  # Standard port
        debug=config.FLASK_DEBUG,  # Enable debug mode in development
        threaded=True  # Handle multiple requests concurrently
    )

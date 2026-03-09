# Day3 IVR System - Loom Script

**Duration:** ~8-10 minutes
**Level:** Intermediate (assumes basic Python knowledge)

---

## Opening Scene (0:00-0:30)

### Visual: Show the Day3 folder on screen
- Open VS Code or file explorer
- Show the project directory structure

### Script:
"Hey everyone! Today I'm going to walk you through an **Interactive Voice Response (IVR) system** - basically a smart phone system that handles incoming calls, presents menus, and records everything.

This is a **production-ready system** built with Flask, PostgreSQL, Redis, and the Plivo Voice API. By the end of this video, you'll understand how phone systems work behind the scenes."

---

## Section 1: What is an IVR System? (0:30-1:30)

### Visual: Draw/show the IVR concept
- Show a flowchart or diagram of a call flow
- Example: "Press 1 for Sales, Press 2 for Support"

### Script:
"An IVR system is what you experience when you call a company and hear:

'Press 1 for Sales, press 2 for Support, press 3 for Account Information...'

**Key capabilities:**
1. **Receives calls** via Plivo (a voice API provider)
2. **Presents interactive menus** with voice prompts
3. **Records caller choices** in the database
4. **Manages session state** with Redis (temporary storage)
5. **Transfers calls** or provides information
6. **Stores everything permanently** in PostgreSQL

Think of it like a digital receptionist that never gets tired!"

---

## Section 2: The Architecture (1:30-3:30)

### Visual: Show the architecture diagram
- Display the data flow: Phone → Plivo → Flask → Services → Database

### Script:
"Let me break down how all the pieces work together.

**[Point 1: The Phone Call]**
When someone calls your number, here's what happens:

1. **Plivo receives the call** (that's the voice service)
2. **Plivo sends an HTTP request** to our Flask app saying 'hey, someone's calling!'
3. **Flask responds with XML** - instructions for Plivo on what to do next

**[Point 2: The Layers]**
Our system has three main layers:

**Layer 1 - Models (Database):**
- `CallLog` - saves every call that happens
- `CallerHistory` - tracks returning callers
- `MenuConfiguration` - defines what menus exist

**Layer 2 - Services (Business Logic):**
- `RedisService` - manages active call sessions in memory (fast!)
- `PlivoService` - generates the XML responses
- `IVRService` - decides what to do next in the call flow

**Layer 3 - Flask (Web Server):**
- Three main endpoints:
  - `/webhooks/answer` - 'Someone is calling!'
  - `/webhooks/input` - 'User pressed digit 1'
  - `/webhooks/hangup` - 'Call ended'

**[Point 3: Technology Stack]**
- **Flask** - lightweight web framework
- **PostgreSQL** - permanent data storage (who called, when, what they pressed)
- **Redis** - temporary session storage (which menu is the caller on right now?)
- **Plivo** - voice API provider
- **SQLAlchemy** - ORM for database"

---

## Section 3: The Data Models (3:30-5:00)

### Visual: Show the database schema
- Display CallLog table structure
- Show CallerHistory table
- Show MenuConfiguration table

### Script:
"Let me show you the database schema - this is how we store information.

**[Point 1: MenuConfiguration Table]**
This is the blueprint of your IVR system. Each menu has:
- `menu_id` - unique identifier (like 'main_menu')
- `message` - what the caller hears ('Press 1 for Sales...')
- `digit_actions` - what happens when they press each digit
- `action_type` - is it a menu, transfer, or recording?

Example: 'main_menu' has digit 1 → go to sales_menu, digit 2 → go to support_menu

**[Point 2: CallLog Table]**
Every single call gets recorded:
- `call_uuid` - unique ID for the call
- `from_number` - who called (e.g., +1-555-1234)
- `start_time` - when the call started
- `duration` - how long they talked
- `menu_path` - which menus they visited (like breadcrumbs)
- `user_inputs` - every digit they pressed
- `status` - did they complete, hang up, transfer?

This gives you perfect audit trail of everything that happened.

**[Point 3: CallerHistory Table]**
If someone calls multiple times:
- `phone_number` - their number
- `total_calls` - how many times they've called
- `total_duration` - total time spent in the system
- `last_call_time` - when they called last
- `metadata` - custom data about this caller

So if someone calls back, you know 'Oh, this person has called 5 times before!'

**[Point 4: Redis Sessions]**
While a call is happening, we store the session in Redis:
```
Key: ivr:session:abc-123-def
Value: {
  'call_uuid': 'abc-123-def',
  'phone_number': '+1-555-1234',
  'current_menu': 'main_menu',
  'inputs_pressed': ['1', '2'],
  'menu_path': ['main_menu', 'sales_menu']
}
```

Why Redis? It's in-memory, super fast, and automatically expires when the call ends. No cleanup needed!"

---

## Section 4: How a Call Flows (5:00-7:00)

### Visual: Step through a complete call flow
- Animate or step through the sequence diagram

### Script:
"Let me walk you through what happens when someone actually makes a call.

**[Step 1: Incoming Call - t=0 seconds]**
- Customer calls your Plivo number: +1-555-1234
- Plivo receives the call
- **Plivo → Flask HTTP POST** to `/webhooks/answer`
- Request includes: `call_uuid`, `from_number`, etc.

**[Step 2: Create Session - t=1 second]**
- Flask receives the request
- Creates a **Redis session** for this call
- Loads the **main_menu** from PostgreSQL
- Returns XML with the message: 'Press 1 for Sales, 2 for Support'

**[Step 3: Menu Plays - t=2 seconds]**
- Plivo plays the voice message
- System waits for caller to press a digit
- Timeout is 5 seconds

**[Step 4: User Presses Digit - t=7 seconds]**
- Customer presses '1' (Sales)
- **Plivo → Flask HTTP POST** to `/webhooks/input`
- Request includes: `call_uuid`, `digit` (1)

**[Step 5: IVR Logic - t=8 seconds]**
- Flask retrieves the **Redis session**
- Looks up what menu to show next for digit 1
- Updates the session with: `menu_path: ['main_menu', 'sales_menu']`
- Loads the **sales_menu** from PostgreSQL
- Returns XML with: 'You've reached Sales. Press 1 to speak to someone, press 2 for hours'

**[Step 6: Loop or End - t=9+ seconds]**
- Steps 3-5 repeat for each digit pressed
- Eventually, customer presses digit for 'Transfer to Sales Agent'

**[Step 7: Call Transfers - t=120 seconds]**
- Flask generates XML to **transfer** the call
- Plivo transfers customer to actual sales agent
- Or: Customer hangs up

**[Step 8: Call Ends - t=125 seconds]**
- Call disconnects
- **Plivo → Flask HTTP POST** to `/webhooks/hangup`
- Request includes: `call_uuid`, `call_duration`, etc.

**[Step 9: Save Everything - t=126 seconds]**
- Flask saves to **CallLog**:
  - Who called: +1-555-0987
  - When: 2025-02-22 14:30:00
  - Duration: 125 seconds
  - Path: main_menu → sales_menu
  - Inputs: 1, 1 (pressed 1 twice)
  - Status: transferred
- Updates **CallerHistory** with total count
- Deletes the **Redis session** (cleanup)
- Call complete! ✓

The whole thing is automated - no human involved until transfer!"

---

## Section 5: Project Files Overview (7:00-8:30)

### Visual: Navigate through the codebase
- Show each file as you mention it

### Script:
"Let me show you what we actually built. Here's the project structure:

**[Root Level Files]**
- `config.py` - Loads environment variables (credentials, database URL, etc.)
- `requirements.txt` - Python dependencies (Flask, SQLAlchemy, redis, plivo, psycopg2)
- `.env` - Your actual credentials (kept secret, not in git)
- `app.py` - The Flask application with three webhook endpoints

**[models/ folder - The Database Layer]**
- `database.py` - SQLAlchemy setup, engine, session factory
- `call_log.py` - CallLog model (the table definition)
- `caller_history.py` - CallerHistory model
- `menu_config.py` - MenuConfiguration model

**[services/ folder - The Business Logic]**
- `redis_service.py` - Session management (get/set/delete sessions)
- `plivo_service.py` - XML generation (what to tell Plivo to do)
- `ivr_service.py` - IVR orchestration (figure out next menu based on input)

**[scripts/ folder - Utilities]**
- `init_db.py` - One-time: create all database tables
- `seed_menus.py` - One-time: populate default menus
- `verify_setup.py` - Test all connections (Postgres, Redis, Plivo)
- `test_webhook.py` - Simulate calls locally without a real phone

**[docs/ folder - Documentation]**
- Detailed explanations of each component
- Setup guides, architecture diagrams, etc.

The beauty of this structure is **separation of concerns**:
- Models know about data
- Services know about business logic
- Flask just handles HTTP and calls services
- Easy to test, easy to extend, easy to understand"

---

## Section 6: Key Takeaways (8:30-10:00)

### Visual: Summary slide or checklist

### Script:
"Here's what you learned today:

**1. What IVR Systems Do:**
- Handle incoming calls via APIs
- Present interactive menus
- Record every interaction
- Scale to handle thousands of calls

**2. Architecture Patterns:**
- Service layer (business logic separate from web layer)
- Models/ORM (database abstraction)
- Temporary storage (Redis for sessions)
- Permanent storage (PostgreSQL for records)

**3. The Call Flow:**
- Webhook-based (Plivo sends HTTP requests)
- Stateful (current menu tracked in Redis)
- Session-based (each call is independent)
- Fully logged (everything saved for audit)

**4. Technologies You Learned:**
- Flask webhooks
- SQLAlchemy ORM
- Redis sessions
- Plivo Voice API
- PostgreSQL

**5. Why This Matters:**
- Phone systems are **real-time systems** - they must respond in milliseconds
- **State management is critical** - you need to know which menu the user is on
- **Audit trails are essential** - companies need to know what customers did
- **APIs power everything** - Plivo API handles the voice, your app handles the logic

---

## Closing (10:00)

### Script:
"You just learned how to build a production-ready IVR system from scratch. This is the same architecture used by companies handling thousands of calls per day.

Key files to focus on:
- Start with `models/` to understand the data
- Then `services/` to understand the logic
- Then `app.py` to see how they work together

To get this running locally:
1. Set up PostgreSQL and Redis (brew install)
2. Copy `.env.example` to `.env` with your credentials
3. Run `python scripts/init_db.py` to create tables
4. Run `python app.py` to start the server
5. Run `python scripts/test_webhook.py` to simulate a call

This is a great foundation for learning about:
- Voice APIs
- Real-time systems
- Session management
- Database design
- Service-oriented architecture

Thanks for watching, and happy coding! 🚀"

---

## Additional Notes for Recording

### Pacing Tips:
- Pause briefly at transitions between sections
- Let code examples breathe - don't rush through file reading
- Use zoom or highlighting to focus on specific parts
- Slow down at architectural diagrams

### Visual Recommendations:
- Use different colors for different layers (Models, Services, Flask)
- Show actual database records/Redis values
- Create a simple animated call flow diagram
- Use VS Code's outline/breadcrumb to navigate quickly

### Optional Demos:
- Show the `.env` file structure
- Show a sample MenuConfiguration record
- Show a sample CallLog record
- Open a terminal and run `python scripts/verify_setup.py`

### Music/Audio:
- Upbeat background music during intro/outro
- Lower volume during technical explanations
- Highlight key terms with sound effects (optional)

---

## Script Checklist

- [ ] Intro: Hook the audience (what is an IVR system?)
- [ ] Architecture: Show how pieces fit together
- [ ] Database: Explain the three models
- [ ] Call Flow: Walk through step-by-step
- [ ] Code: Show actual files
- [ ] Takeaways: Key concepts summarized
- [ ] Outro: What to do next

---

**Total Duration: ~10 minutes (scripted timing)**

**Actual Duration: 8-12 minutes (accounting for natural pauses, demonstrations, and code exploration)**

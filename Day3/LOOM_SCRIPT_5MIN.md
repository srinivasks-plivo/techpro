# Day3 IVR System - 5 Minute Loom Script

**Duration:** 5 minutes
**Level:** Intermediate

---

## Opening (0:00-0:30)

"Hey! Today I'm showing you a production-ready **IVR System** - the smart phone system that handles incoming calls, presents menus, and records everything.

Think of the system you use when calling a bank: 'Press 1 for Sales, Press 2 for Support'. That's an IVR. Built with Flask, PostgreSQL, Redis, and Plivo Voice API. Let's dive in!"

---

## What is IVR + Architecture (0:30-2:00)

"An IVR system does 5 things:
1. **Receives calls** via Plivo (voice API)
2. **Presents interactive menus** with voice
3. **Records caller choices** in database
4. **Manages session state** with Redis
5. **Stores everything** in PostgreSQL

**The architecture has 3 layers:**

**Layer 1 - Models (Database):**
- CallLog → saves every call
- CallerHistory → tracks returning callers
- MenuConfiguration → defines menus

**Layer 2 - Services (Business Logic):**
- RedisService → session management
- PlivoService → generates XML responses
- IVRService → decides next menu based on input

**Layer 3 - Flask (Web Server):**
- /webhooks/answer → incoming call
- /webhooks/input → digit pressed
- /webhooks/hangup → call ended"

---

## How a Call Works (2:00-4:00)

"Let me walk you through a real call step-by-step:

**Step 1 (t=0 sec):** Customer calls your number → Plivo receives it → sends HTTP POST to Flask `/webhooks/answer`

**Step 2 (t=1 sec):** Flask creates a **Redis session**, loads **main_menu** from database, returns XML: 'Press 1 for Sales, 2 for Support'

**Step 3 (t=2 sec):** Plivo plays the voice message, waits 5 seconds for digit input

**Step 4 (t=7 sec):** Customer presses '1' → Plivo sends HTTP POST to `/webhooks/input` with digit=1

**Step 5 (t=8 sec):** Flask retrieves the **Redis session**, looks up next menu for digit 1, updates session, loads **sales_menu**, returns new XML

**Step 6+ (t=9+ sec):** Loop repeats until customer presses transfer digit or hangs up

**Step 9 (t=125 sec):** Call ends → Plivo sends POST to `/webhooks/hangup` with duration

**Step 10 (t=126 sec):** Flask saves to **CallLog** (who called, when, duration, menu path, inputs), updates **CallerHistory** (total calls), deletes **Redis session**. Done! ✓

The whole flow is **automated** - no human involvement until the transfer!"

---

## Project Structure (4:00-4:45)

"Here's what we built:

**Root Files:**
- config.py → loads credentials
- requirements.txt → dependencies
- .env → your secrets
- app.py → Flask webhooks

**models/folder:**
- database.py → SQLAlchemy setup
- call_log.py → CallLog table
- menu_config.py → MenuConfiguration table

**services/ folder:**
- redis_service.py → session management
- plivo_service.py → XML generation
- ivr_service.py → IVR logic

**scripts/ folder:**
- init_db.py → create tables
- test_webhook.py → simulate calls locally"

---

## Key Takeaways (4:45-5:00)

"You learned:
✓ How IVR systems work (webhooks, not direct calls)
✓ Session management with Redis
✓ Data persistence with PostgreSQL
✓ Three-layer architecture pattern
✓ Real call flow from start to finish

This is production-ready code used by companies handling thousands of calls per day!

To run it: setup PostgreSQL + Redis, configure .env, run init_db.py, start Flask app.

Thanks for watching! 🚀"

---

**Script Complete - Ready to Record!**

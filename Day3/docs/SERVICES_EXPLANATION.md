# Services Layer - Complete Explanation

## Overview

The Services Layer contains three interconnected services that handle the IVR logic:

1. **Redis Service** - Session Management (temporary, fast)
2. **Plivo Service** - XML Generation (how to respond)
3. **IVR Service** - Call Orchestration (what should happen next)

## Service #1: Redis Service

### Purpose
Manage temporary call session data while a call is active.

### What It Does
```
Call arrives
    ↓
create_session() → Create in Redis
    ↓
User presses digit
    ↓
add_user_input() → Record in Redis
    ↓
set_current_menu() → Update current menu in Redis
    ↓
Call ends
    ↓
delete_session() → Cleanup
```

### Key Methods

| Method | Purpose | When Called |
|--------|---------|-------------|
| `create_session()` | Start new session | Incoming call |
| `get_session()` | Retrieve session | Any time we need current state |
| `update_session()` | Save changes | After any state change |
| `add_user_input()` | Record digit press | User presses button |
| `set_current_menu()` | Navigate to new menu | Moving to next menu |
| `delete_session()` | Cleanup | Call ends |
| `mark_call_completed()` | Mark as successful | Call ends normally |
| `mark_call_abandoned()` | Mark as abandoned | User hung up |

### Session Data Structure

```python
{
    "call_uuid": "4f3a4e5c-b2d8-4a7f-9c1e-3b8f6a9d2e1c",
    "from_number": "+15551234567",
    "to_number": "+15559876543",
    "current_menu_id": "main_menu",
    "menu_history": ["main_menu", "sales_menu"],
    "user_inputs": [
        {
            "menu_id": "main_menu",
            "digit": "1",
            "timestamp": "2026-01-29T10:00:05Z"
        },
        {
            "menu_id": "sales_menu",
            "digit": "1",
            "timestamp": "2026-01-29T10:00:08Z"
        }
    ],
    "start_time": "2026-01-29T10:00:00Z",
    "last_activity": "2026-01-29T10:00:08Z",
    "state": "active"
}
```

### Why Redis?

- **Speed**: In-memory, microseconds vs. disk
- **TTL**: Auto-expires after 30 minutes
- **Flexibility**: JSON strings, easy to modify
- **Cleanup**: Can disappear without data loss (temporary)

---

## Service #2: Plivo Service

### Purpose
Generate XML responses that tell Plivo what to do.

### The XML Language

Plivo doesn't execute Python. Instead, it:
1. Receives our XML response
2. Executes the XML instructions
3. Reports back what happened

### Plivo XML Elements

```xml
<Response>                                    <!-- Root element -->
  <Speak>Say something via TTS</Speak>       <!-- Text-to-speech -->
  <GetDigits action="/url">                  <!-- Wait for digits -->
    <Speak>Prompt message</Speak>
  </GetDigits>
  <Dial timeout="30">                        <!-- Transfer call -->
    <Number>+15551234567</Number>
  </Dial>
  <Hangup />                                 <!-- End call -->
  <Play>https://example.com/audio.mp3</Play> <!-- Play audio file -->
  <Redirect>/new-url</Redirect>              <!-- Go to new URL -->
</Response>
```

### Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `generate_menu_xml()` | Menu with digit input | XML with <GetDigits> |
| `generate_transfer_xml()` | Transfer to phone | XML with <Dial> |
| `generate_hangup_xml()` | End call | XML with <Hangup> |
| `generate_play_xml()` | Play audio file | XML with <Play> |
| `generate_speak_only_xml()` | Just say something | XML with <Speak> |
| `generate_invalid_input_xml()` | Invalid digit error | Error XML |
| `generate_timeout_xml()` | No input error | Error XML |

### Common Response Examples

**Menu with digit input:**
```xml
<Response>
  <GetDigits action="/webhooks/input" timeout="5" numDigits="1">
    <Speak>Press 1 for Sales, 2 for Support</Speak>
  </GetDigits>
</Response>
```

**Transfer to operator:**
```xml
<Response>
  <Dial timeout="30">
    <Number>+15551234567</Number>
  </Dial>
</Response>
```

**Say goodbye and hang up:**
```xml
<Response>
  <Speak>Thank you for calling. Goodbye.</Speak>
  <Hangup />
</Response>
```

### Why XML?

- Plivo is a service external to your code
- XML is the standard protocol for voice APIs
- Each element maps to a voice action
- Easy for Plivo to parse and execute

---

## Service #3: IVR Service

### Purpose
Orchestrate the entire IVR call flow.

### The Three Main Methods

#### 1. handle_incoming_call()
```
Incoming call arrives
    ↓
Create Redis session (redis_service)
    ↓
Load main_menu from database (model)
    ↓
Generate XML (plivo_service)
    ↓
Return XML to Plivo
```

#### 2. handle_digit_input()
```
Digit arrives from Plivo
    ↓
Get session from Redis (redis_service)
    ↓
Get current menu from database (model)
    ↓
Validate digit
    ↓
Record digit in session (redis_service)
    ↓
Determine next menu
    ↓
Generate XML (plivo_service)
    ↓
Update session (redis_service)
    ↓
Return XML to Plivo
```

#### 3. handle_hangup()
```
Call ends
    ↓
Get session from Redis (redis_service)
    ↓
Save to CallLog table (model) - PERMANENT
    ↓
Update CallerHistory table (model) - PERMANENT
    ↓
Delete session from Redis (redis_service)
```

### Decision Logic

When user presses a digit, IVR Service determines the action:

```python
if menu.action_type == "menu":
    # Navigate to next menu

elif menu.action_type == "transfer":
    # Transfer to phone number

elif menu.action_type == "hangup":
    # End the call

elif digit_is_valid:
    # Go to digit_actions[digit] menu

else:
    # Invalid input - show error
```

---

## How Services Work Together

### Complete Call Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. INCOMING CALL                                                 │
│ Plivo calls: /webhooks/answer?CallUUID=abc123&From=+15551234... │
└──────────────────┬───────────────────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │ IVR Service         │
        │ .handle_incoming_   │
        │  call()             │
        └──────────┬──────────┘
                   │
         ┌─────────┼─────────┐
         │         │         │
    ┌────▼────┐ ┌─▼──────┐ ┌▼──────────┐
    │  Redis  │ │ Models │ │   Plivo   │
    │ Service │ │        │ │  Service  │
    │         │ │        │ │           │
    │create_  │ │ Load   │ │ generate_ │
    │session()│ │ main_  │ │ menu_xml()│
    │         │ │ menu   │ │           │
    └────┬────┘ └─┬──────┘ └┬──────────┘
         │        │        │
         └────────┼────────┘
                  │
            ┌─────▼──────┐
            │   Return   │
            │    XML     │
            └─────┬──────┘
                  │
                  ▼
    ┌─────────────────────────────────┐
    │ Plivo speaks: "Press 1 for..."  │
    └─────────────────────────────────┘
                  │
                  ▼ (User presses digit)
                  │
┌──────────────────────────────────────────────────────────────────┐
│ 2. DIGIT INPUT                                                   │
│ Plivo calls: /webhooks/input?CallUUID=abc123&Digits=1           │
└──────────────────┬───────────────────────────────────────────────┘
                   │
        ┌──────────▼────────────┐
        │  IVR Service          │
        │  .handle_digit_       │
        │   input()             │
        └──────────┬────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐ ┌──────▼────┐ ┌───────▼──────┐
│ Redis  │ │  Models   │ │    Plivo     │
│Service │ │           │ │   Service    │
│        │ │           │ │              │
│get_    │ │ Load menu │ │ generate_    │
│session │ │ from menu │ │ menu_xml()   │
│        │ │ ID        │ │ OR           │
│add_    │ │ Validate  │ │ generate_    │
│user_   │ │ digit     │ │ transfer_xml │
│input   │ │           │ │ OR           │
│        │ │           │ │ generate_    │
│set_    │ │           │ │ hangup_xml   │
│current │ │           │ │              │
│_menu   │ │           │ │              │
└────┬───┘ └─────┬─────┘ └───────┬──────┘
     │           │               │
     └───────────┼───────────────┘
                 │
            ┌────▼─────┐
            │  Return  │
            │   XML    │
            └────┬─────┘
                 │
                 ▼ (Repeat or)
                 │
┌──────────────────────────────────────────────────────────────────┐
│ 3. CALL ENDS (User hangs up)                                     │
│ Plivo calls: /webhooks/hangup?CallUUID=abc123&Duration=330      │
└──────────────────┬───────────────────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │  IVR Service        │
        │  .handle_hangup()   │
        └──────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐     ┌──▼───┐      ┌───▼───┐
│ Redis  │     │Models│      │ Redis │
│Service │     │      │      │Service│
│        │     │      │      │       │
│get_    │     │Save  │      │delete_│
│session │     │to    │      │session│
│        │     │Call  │      │       │
│        │     │Log   │      │       │
│        │     │      │      │       │
│        │     │Update│      │       │
│        │     │Caller│      │       │
│        │     │History│      │       │
└────────┘     └──────┘      └───────┘

            All data now PERMANENT
            in PostgreSQL database
```

---

## Data Flow Summary

### Temporary (Fast) - Redis
```
create_session()
    ↓
add_user_input()
    ↓
set_current_menu()
    ↓
Session expires or deleted
```

### Permanent (Durable) - PostgreSQL
```
When call ends:
    ↓
CallLog created (call details)
    ↓
CallerHistory updated (caller profile)
    ↓
Data stays forever
```

### The Handoff
```
Redis Session
    ↓ (call ends)
    ↓
CallLog + CallerHistory
    ↓ (via models)
    ↓
PostgreSQL Database
```

---

## Key Insights

### 1. Separation of Concerns
- **Redis Service**: "Where is this call in the system?"
- **Plivo Service**: "How do we tell Plivo what to do?"
- **IVR Service**: "What should happen next?"

### 2. Models ↔ Services Relationship
```
Models:            Services:
- MenuConfiguration → IVR Service reads for menu logic
- CallLog           ← IVR Service writes at call end
- CallerHistory     ← IVR Service updates at call end
```

### 3. Speed vs. Durability
```
Need Speed?  → Redis (temporary, fast)
Need Forever? → PostgreSQL via Models (permanent, slow)
```

### 4. Stateless Design
- IVR Service doesn't "remember" anything
- Everything is stored in Redis or database
- If server crashes, just read Redis session and continue

---

## Using the Services

### Example: Simple Menu Navigation

```python
from services import redis_service, plivo_service, ivr_service

# 1. Incoming call
xml = ivr_service.handle_incoming_call(
    call_uuid="abc123",
    from_number="+15551234567",
    to_number="+15559876543"
)
# Returns: <Response><GetDigits>...main menu...</GetDigits></Response>

# 2. User presses 1
xml = ivr_service.handle_digit_input(
    call_uuid="abc123",
    digit="1"
)
# Returns: <Response><GetDigits>...sales menu...</GetDigits></Response>

# 3. User presses 1 again
xml = ivr_service.handle_digit_input(
    call_uuid="abc123",
    digit="1"
)
# Returns: <Response><Dial>...transfer to operator...</Dial></Response>

# 4. Call ends
ivr_service.handle_hangup(
    call_uuid="abc123",
    hangup_cause="NORMAL_CLEARING",
    duration=180
)
# Saves to database, cleans up Redis session
```

---

## Error Scenarios

### Session Expired
```
User doesn't press digit for 30 minutes
    ↓
Redis session auto-expires (TTL)
    ↓
Next digit press → Session not found
    ↓
IVR Service detects missing session
    ↓
Generate error XML
```

### Invalid Menu
```
Menu references non-existent next_menu
    ↓
IVR Service can't find it in database
    ↓
Generates hangup XML
    ↓
Call ends gracefully
```

### Digit Not in Menu
```
User presses "5" but only "1,2,3" valid
    ↓
IVR Service detects invalid digit
    ↓
Loads invalid_input_menu
    ↓
Generates error message XML
```

---

## Next Steps

With Services complete, next phase is:

**Phase 3: Flask Application**
- Create Flask app (web server)
- Create webhook endpoints
- Connect to services

**Phase 4: Database & Scripts**
- Create database initialization
- Create menu seeding
- Create verification tools

---

## Summary

| Component | Purpose | Speed | Storage |
|-----------|---------|-------|---------|
| Redis Service | Session management | ⚡ Fast | Temporary |
| Plivo Service | XML generation | ⚡ Fast | N/A |
| IVR Service | Call orchestration | ⚡ Fast | Via models |
| Models | Data persistence | 🐢 Slow | Permanent |

**Together**: A complete, scalable IVR system! 🎯

# Database Models Explanation

## Overview: Three Tables, One Purpose

The IVR system uses three interconnected tables:

```
┌─────────────────────────────────────────────────────────────────┐
│                      IVR SYSTEM ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐      ┌──────────────────────┐
│  menu_configurations │      │    call_logs         │
│  (Define menus)      │      │    (Store calls)     │
├──────────────────────┤      ├──────────────────────┤
│ menu_id (unique)  ◄──┼──┐   │ call_uuid (unique)   │
│ message           │  │   ├──► from_number         │
│ digit_actions     │  │   │  │ duration             │
│ action_config     │  │   │  │ menu_path (FK)       │
│ parent_menu_id    │  │   │  │ user_inputs          │
└──────────────────────┘  │   │ created_at           │
                          │   └──────────────────────┘
                          │
                          ├──► menu_path contains menu_ids
                              from menu_configurations
                          
                          ┌──────────────────────┐
                          │  caller_history      │
                          │  (Know your caller)  │
                          ├──────────────────────┤
                          │ phone_number (FK)    │
                          │ total_calls          │
                          │ avg_duration         │
                          │ preferred_language   │
                          └──────────────────────┘
```

---

## Table 1: `menu_configurations`

### What it stores
The **blueprint** for every menu screen in your IVR.

### Key fields

| Field | Purpose | Example |
|-------|---------|---------|
| `menu_id` | Unique identifier | "sales_menu" |
| `message` | What Plivo says to caller | "Press 1 for new customers" |
| `digit_actions` | Button mapping | `{"1": "sales_new", "2": "sales_exist"}` |
| `max_digits` | How many digits to accept | 1 |
| `timeout` | Silence threshold (seconds) | 5 |
| `action_type` | Special behavior | "menu", "transfer", "hangup" |
| `action_config` | Extra config | `{"transfer_number": "+1555..."}` |

### Database Schema

```sql
CREATE TABLE menu_configurations (
    id SERIAL PRIMARY KEY,
    menu_id VARCHAR(100) UNIQUE NOT NULL,      -- "main_menu"
    message TEXT NOT NULL,                     -- "Press 1 for..."
    parent_menu_id VARCHAR(100),               -- NULL for root
    digit_actions JSON,                        -- {"1": "sales_menu"}
    action_type VARCHAR(50),                   -- "menu", "transfer"
    action_config JSON,                        -- Transfer details
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Example data

```json
{
    "menu_id": "main_menu",
    "parent_menu_id": null,
    "message": "Welcome! Press 1 for Sales, 2 for Support, 3 for Billing",
    "digit_actions": {
        "1": "sales_menu",
        "2": "support_menu",
        "3": "billing_menu",
        "0": "operator_transfer"
    },
    "action_type": "menu",
    "is_active": true
}
```

### Why this design?

**Flexibility:** Change menus without restarting the app.
- Update database → Changes immediately live
- No code redeploy needed
- Non-technical people can manage menus

**Scalability:** Supports unlimited menu trees
- Parent-child relationships build complex hierarchies
- Easy to add/remove menus

---

## Table 2: `call_logs`

### What it stores
**Detailed record** of each individual phone call.

Think of it like a phone bill - captures every call's details.

### Key fields

| Field | Purpose | Example |
|-------|---------|---------|
| `call_uuid` | Plivo's unique call ID | "4f3a-4e5c-b2d8-4a7f" |
| `from_number` | Caller's phone number | "+15551234567" |
| `start_time` | When call started | "2026-01-29T10:00:00Z" |
| `end_time` | When call ended | "2026-01-29T10:05:30Z" |
| `duration` | Call length (seconds) | 330 |
| `menu_path` | Menus visited in order | ["main_menu", "sales_menu"] |
| `user_inputs` | Digits pressed + timing | `[{"digit": "1", "menu": "main"}]` |
| `call_status` | Result of call | "completed", "abandoned" |

### Database Schema

```sql
CREATE TABLE call_logs (
    id SERIAL PRIMARY KEY,
    call_uuid VARCHAR(255) UNIQUE NOT NULL,
    from_number VARCHAR(20) NOT NULL,
    to_number VARCHAR(20) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration INTEGER,
    menu_path JSON,                      -- ["main_menu", "sales_menu"]
    user_inputs JSON,                    -- [{"digit": "1", "time": "..."}]
    call_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Example data

```json
{
    "call_uuid": "4f3a4e5c-b2d8-4a7f-9c1e-3b8f6a9d2e1c",
    "from_number": "+15551234567",
    "to_number": "+15559876543",
    "start_time": "2026-01-29T10:00:00Z",
    "end_time": "2026-01-29T10:05:30Z",
    "duration": 330,
    "call_status": "completed",
    "menu_path": ["main_menu", "sales_menu", "sales_new_customer"],
    "user_inputs": [
        {"menu_id": "main_menu", "digit": "1", "timestamp": "2026-01-29T10:00:05Z"},
        {"menu_id": "sales_menu", "digit": "1", "timestamp": "2026-01-29T10:00:08Z"}
    ]
}
```

### Why this design?

**Audit trail:** Complete history of every call
- Who called
- What menus they used
- What buttons they pressed
- How long they spent

**Analytics:** Understand caller behavior
- Popular menus
- Abandon rates
- Average duration
- Path analysis

---

## Table 3: `caller_history`

### What it stores
**Summary profile** for each phone number.

One row per unique caller, aggregating all their calls.

### Key fields

| Field | Purpose | Example |
|-------|---------|---------|
| `phone_number` | Unique caller ID | "+15551234567" |
| `total_calls` | How many times called | 5 |
| `first_call_at` | Initial call time | "2026-01-20T14:00:00Z" |
| `last_call_at` | Most recent call | "2026-01-29T10:00:00Z" |
| `total_duration` | Total time (seconds) | 1200 |
| `preferred_language` | Their language | "en", "es" |
| `metadata` | Custom data | `{"account": "ACC123", "vip": true}` |

### Database Schema

```sql
CREATE TABLE caller_history (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    first_call_at TIMESTAMP NOT NULL,
    last_call_at TIMESTAMP NOT NULL,
    total_calls INTEGER NOT NULL DEFAULT 1,
    total_duration INTEGER NOT NULL DEFAULT 0,
    preferred_language VARCHAR(10),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Example data

```json
{
    "phone_number": "+15551234567",
    "total_calls": 5,
    "first_call_at": "2026-01-20T14:00:00Z",
    "last_call_at": "2026-01-29T10:00:00Z",
    "total_duration": 1200,
    "average_duration": 240,
    "preferred_language": "en",
    "metadata": {
        "account_number": "ACC123456",
        "customer_tier": "premium",
        "vip": true,
        "notes": "VIP customer, prefers email follow-up"
    }
}
```

### Why this design?

**Quick lookup:** Recognize returning customers
- When they call back, check caller_history
- Know they've called 5 times before
- Personalize greeting or shortcuts

**Aggregation:** Calculate business metrics
- Total customers (count unique phone_numbers)
- Average calls per customer
- Average duration per customer
- Identify VIPs (total_calls > 10)

---

## How They Work Together: A Call Journey

### Step 1: User calls
```
🔔 Phone rings → Plivo webhook to /webhooks/answer
```

### Step 2: Load menu
```python
menu = MenuConfiguration.query.filter_by(menu_id="main_menu").first()
# Returns: message, digit_actions, timeout, etc.
```

### Step 3: Create session (Redis - temporary)
```python
session = {
    "call_uuid": "4f3a...",
    "from_number": "+1555...",
    "current_menu_id": "main_menu",      # ← Points to menu_configurations
    "menu_history": ["main_menu"],
}
redis.setex(f"ivr:session:{call_uuid}", 1800, json.dumps(session))
```

### Step 4: User presses digit
```
digit = "1" → User wants Sales
```

### Step 5: Update session
```python
current_menu = MenuConfiguration.query.filter_by(
    menu_id=session["current_menu_id"]
).first()
next_menu_id = current_menu.digit_actions["1"]  # "sales_menu"

session["menu_history"].append("sales_menu")
session["current_menu_id"] = "sales_menu"
session["user_inputs"].append({
    "menu_id": "main_menu",
    "digit": "1"
})
```

### Step 6: Call ends
```python
# Save to call_logs table (permanent)
call_log = CallLog(
    call_uuid=session["call_uuid"],
    from_number=session["from_number"],
    duration=calculated_duration,
    menu_path=session["menu_history"],        # ["main_menu", "sales_menu"]
    user_inputs=session["user_inputs"]        # All digits they pressed
)
db.add(call_log)
db.commit()

# Update caller_history table
caller = CallerHistory.query.filter_by(
    phone_number=session["from_number"]
).first_or_create()
caller.total_calls += 1
caller.total_duration += calculated_duration
caller.last_call_at = datetime.utcnow()
db.commit()

# Clean up session
redis.delete(f"ivr:session:{call_uuid}")
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      INCOMING CALL                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Load main_menu from  │
                    │ menu_configurations  │
                    └──────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Create session in    │
                    │ Redis (temporary)    │
                    └──────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────────┐
        │           USER PRESSES DIGIT                  │
        └───────────────────────────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Get digit_actions    │
                    │ from menu_config     │
                    └──────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼──────┐       ┌────────▼─────┐
            │ Navigate to  │       │ Execute      │
            │ next menu    │       │ action       │
            │ (loop back)  │       └────────┬─────┘
            └──────────────┘                │
                    │                       │
                    │            ┌──────────▼──────────┐
                    │            │ Transfer / Hangup   │
                    │            └──────────┬──────────┘
                    │                       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ CALL ENDS            │
                    └──────────────────────┘
                                │
                                ▼
                ┌──────────────────────────────────┐
                │ Save to call_logs table          │
                │ (menu_path + user_inputs)        │
                └──────────────────────────────────┘
                                │
                                ▼
                ┌──────────────────────────────────┐
                │ Update caller_history table      │
                │ (increment total_calls, etc.)    │
                └──────────────────────────────────┘
                                │
                                ▼
                ┌──────────────────────────────────┐
                │ Delete session from Redis        │
                └──────────────────────────────────┘
```

---

## Key Takeaways

### Model #1: MenuConfiguration
- **Purpose:** Define IVR structure
- **Flexibility:** Change menus without code changes
- **Key feature:** digit_actions for routing

### Model #2: CallLog
- **Purpose:** Permanent record of each call
- **Used for:** Audit trail, analytics
- **Key feature:** menu_path and user_inputs tracking

### Model #3: CallerHistory
- **Purpose:** Know each caller
- **Used for:** Personalization, business metrics
- **Key feature:** Aggregated stats (total_calls, avg_duration)

### Together
They create a complete system:
- **MenuConfiguration** = Blueprint
- **CallLog** = Execution history
- **CallerHistory** = Caller profile

---

## Next Steps

Now that you understand the models, the next components will be:

1. **Redis Service** - Store sessions temporarily (fast)
2. **Plivo Service** - Generate XML responses
3. **IVR Service** - Orchestrate call flow
4. **Flask App** - Handle webhooks
5. **Database initialization** - Create tables

Each component builds on the models you just learned!

<a name="_gzjc4dobdtlw"></a>Overview

**Duration:** 2 weeks, **Time needed:** ~ 6-8 hours/week
##
## <a name="_2lp5ritye2nf"></a><a name="_g6h263g5g6ar"></a>**The Core Philosophy: You Direct, Claude Code Builds**
**You are a business person. Claude Code is your engineering partner.**

This program is designed for you to learn to direct claude code. You will and should never manually write Python, JavaScript, or any programming language. Instead, you'll learn to:

1. **Describe what you want** in plain English
1. **Let Claude Code build it** for you
1. **Verify the output works** by testing and checking results
1. **Push to production** by asking claude code to do so

## <a name="_4a81p6qy7yjq"></a>**Your Role vs Claude Code's Role**

|**Your Role (Human)**|**Claude Code's Role**|
| :- | :- |
|Decide what to build|Write all the code|
|Give requirements in plain English|Create project structure and files|
|Run commands (copy/paste from instructions)|Handle dependencies and configurations|
|Test by clicking, calling, checking dashboards|Debug and fix errors|
|Verify data appears correctly|Integrate APIs and services|
|Ask clarifying questions when stuck|Explain what code does when asked|


##
##
## <a name="_xwfmtl95z0qw"></a><a name="_331u4hc7dxry"></a><a name="_a6zat25zy6k0"></a>**How to Approach Each Day**
**Step 1: Watch the short videos (5-10 min)** Get a mental model of the concept. Don't memorize—just understand "why this exists."

**Step 2: Learn concepts from Claude (browser/desktop)** Ask Claude to explain concepts. Your goal: understand enough to verify outputs, not to code.

**Step 3: Build projects with Claude Code (terminal)** Give Claude Code your requirements. Let it generate everything. Run the code. Test it.

**Step 4: Verify using checklists** Every project has a verification checklist. Your job is to confirm each item works.

## <a name="_jjcr4kbt3dux"></a>**The Golden Rules for Success**
**Rule 1: Never write code manually** If you're typing Python or JavaScript, stop. Ask Claude Code to do it.

**Rule 2: Copy-paste commands exactly** Terminal commands are provided. Copy them. Don't improvise.

**Rule 3: Verify in dashboards, not code** Check Vercel dashboard for data. Check Railway logs for activity. Check Plivo console for calls. You verify by looking at results, not reading code.

**Rule 4: When stuck, describe the problem to Claude** "I ran the command and got this error: [paste error]" — Claude will fix it.

**Rule 5: Test with real calls** The ultimate verification is: Can you call the phone number and talk to your AI?


##
##
##
## <a name="_gwviprcv5vxq"></a><a name="_qxb36x8ze27p"></a><a name="_qggdntqdn7dm"></a><a name="_xa491n8aucz7"></a>**Week-by-Week Agenda**
### <a name="_uy59t3uspr89"></a>**Week 1: Foundation & Deployment (5 Days)**

|**Day**|**Focus**|**What You'll Have Working**|
| :-: | :-: | :-: |
|1|Environment + Git|Cursor IDE, GitHub, terminal basics, first Python project running|
|2|Multi-file projects|Plivo Account Health Checker with proper structure|
|3|Web servers + Databases|Flask server, Redis sessions, PostgreSQL storage|
|4|Plivo Voice IVR|Working phone menu: "Press 1 for Sales, 2 for Support..."|
|5|Cloud Deployment|IVR running on Vercel 24/7 with cloud databases|

**End of Week 1:** A production IVR system anyone can call.


### <a name="_3yixv75ni5ev"></a>**Week 2: AI Voice Agents (7 Days)**

|**Day**|**Focus**|**What You'll Have Working**|
| :-: | :-: | :-: |
|1|LLM APIs|OpenAI calls, streaming, function calling|
|2|Speech AI|Deepgram transcription, ElevenLabs voice generation|
|3|Pipecat Framework|Local voice bot you can talk to via microphone|
|4|Pipecat + Plivo|AI agent answering real phone calls|
|5|LiveKit Alternative|Same agent using LiveKit + SIP (optional approach)|
|6|Railway Deployment|Voice AI running 24/7 in the cloud|
|7|Polish + Demo|Final features, demo video, external testing|

**End of Week 2:** A production AI receptionist that answers calls, detects intent, and logs everything.


## <a name="_g8kipckjhs4t"></a>**Tools You'll Use**

|**Tool**|**Purpose**|**You'll Use It For**|
| :-: | :-: | :-: |
|Claude code|Your tech partner|Everything|
|Cursor IDE|Code editor with AI|Where Claude Code runs|
|GitHub Desktop|Version control|Saving and sharing your work|
|ngrok|Local tunnel|Testing webhooks during development|
|Vercel|Serverless hosting|Deploying APIs and databases|
|Railway|Container hosting|Deploying voice AI (long-running)|
|Plivo|Phone infrastructure|Real phone numbers and calls|


## <a name="_qxqtoi744x73"></a>**When Things Go Wrong**
1. **Copy the full error message**
1. **Paste it to Claude Code or Claude browser**
1. **Ask: "I got this error when running [command]. How do I fix it?"**
1. **Follow the fix, test again**

You are never expected to debug code yourself. That's Claude's job.

**Remember: Your job is to direct and verify. Claude Code's job is to build and fix. Stick to your role and you'll succeed.**


### <a name="_dk2qid88s8am"></a>**Tips for Success**
- **Use AI constantly** — ask Claude to explain errors, generate boilerplate, review your code
- **Don't memorize syntax** — understand concepts, look up specifics as needed
- **Break when stuck** — if stuck for 30+ min, ask Claude or take a break
- **Document everything** — keep a running Google Doc of "things I learned" and "things that confused me"
- **Ship ugly code** — working > perfect, refine later


<a name="_rvswqsll6de2"></a>Week 1 - Foundation
### <a name="_lcjhd4z0t580"></a>**Week 1: Foundation**
#### <a name="_9b7z5oaijrel"></a>**Day 1**
**Goal: Set up your development environment, understand Git workflows, and learn to direct Claude Code while verifying its outputs.**

**Shorts to watch**

- [**Fireship - VS Code in 100 Seconds**](https://youtube.com/watch?v=KMxo3T_MTvY)** 
- [**Git Explained in 100 Seconds**](https://youtube.com/watch?v=hwP7WQkmECE)
- [**Cursor 3 minute demo - the most popular AI code editor**](https://www.youtube.com/watch?v=LR04bU_yV5k&pp=ygURY3Vyc29yIGlkZSBzaG9ydHPSBwkJhwoBhyohjO8%3D)


**Environment Setup**

- Install iterm 2, homebrew on mac (we will install claude code via homebrew not directly, else we wont be able to upgrade automatically)
- Install Cursor IDE, set up Claude Code CLI within Cursor terminal
- Install GitHub Desktop app (for visual git operations without command line)
- Create GitHub account
- Learn terminal basics: cd, ls, mkdir, touch, rm, tab completion
- Learn about brew package manage, install it (use claude desktop app for help)
- **Task:** Navigate to a folder, create a file, and delete it using terminal, change folders and navigate using tab completion

**Git Fundamentals**

- Complete[ ](https://github.com/skills/introduction-to-github)[GitHub Skills: Introduction to GitHub](https://github.com/skills/introduction-to-github) (click "Start Course" in readme)
- Complete[ ](https://github.com/skills/review-pull-requests)[GitHub Skills: Review Pull Requests](https://github.com/skills/review-pull-requests)
- Learn branching, merging, resolving conflicts (ask Claude in browser to explain with diagrams)
  - [**Learn Git Branching**](https://learngitbranching.js.org/) **(interactive visualization)**
- Practice using GitHub Desktop for: viewing changes, staging commits, switching branches, pushing/pulling
- **Task**: Can you explain to someone what a branch is? What a pull request does? When you'd use merge vs rebase?

**Python Awareness (Not Coding)**

You won't write Python, Claude Code will. But you need to recognize what you're looking at to verify outputs.

Ask Claude (browser or desktop) to explain these concepts at a high level:

- How to run a Python file (python filename.py or python3 filename.py)
- What import statements do (bringing in external tools)
- What if \_\_name\_\_ == "\_\_main\_\_": means (entry point of the program)
- Indentation matters in Python (vs brackets {} in other languages)
- What a function looks like (def function\_name():)
- What pip install does (installing packages)
- What requirements.txt is (list of packages needed)

**Task:** When Claude Code generates a Python file, can you identify: the imports, the main function, where the program starts running?
####
<a name="_rmtyd2qbwcap"></a>**Mini-Projects**

**Project 1: CLI Tool with File Operations**

Ask Claude Code to build a command-line tool that:

- Takes a folder path as input
- Scans all files in that folder
- Outputs a summary: total files, total size, largest file, file types breakdown
- Saves the report to a text file

Your job:

1. Give Claude Code the requirements above
1. Run the generated script on a test folder
1. Verify the output matches reality (manually count files in a small folder)
1. Push to GitHub using GitHub Desktop
1. Check that your repo shows the files on github.com

**Project 2: Git Workflow Practice**

Do this sequence 3 times until muscle memory:

1. Create a new branch from github desktop app
1. Ask Claude Code to add a new feature to your Project 1 (e.g., "add option to filter by file extension")
1. Commit changes with a descriptive message
1. Push branch to GitHub
1. Open a Pull Request on github.com
1. Review the changes (look at the dif)
1. Merge the PR
1. Pull latest changes to your local machine

Your job:

- Verify each step worked by checking GitHub Desktop and github.com
- On the 3rd attempt, intentionally create a merge conflict (edit same line in two branches) and resolve it

#### <a name="_9cp3q0qym7hh"></a>**Day 2**
**Project 3: Multi-File Python Project**

Ask Claude Code to build a "Plivo Account Health Checker" that:

- Reads Plivo API credentials from a .env file (not hardcoded)
- Calls Plivo API to get account balance
- Calls Plivo API to get recent message logs
- Outputs a formatted report with: current balance, messages sent today, any failed messages
- Includes proper error handling (what if API is down? what if credentials wrong?)

Your job:

1. Verify the project structure makes sense (separate files for config, API calls, main logic)
1. Verify .env file is in .gitignore (credentials should never go to GitHub, ask claude LLM on what is gitignore and why it matters)
1. Run the script with your real Plivo credentials
1. Intentionally break it (wrong API key) and verify error handling works
1. Push to GitHub, confirm .env is NOT visible in the repo

**End of Project Checklist**

- Cursor IDE installed and Claude Code working in terminal
- GitHub Desktop installed and connected to account
- Can navigate terminal comfortably
- Completed both GitHub Skills courses
- Can explain Git concepts (branch, PR, merge) verbally
- Can identify parts of a Python file (imports, main, functions)
- Project 1 running and verified☐Completed 3 full branch → PR → merge cycles
- Project 3 running with real Plivo credentials
- All projects pushed to GitHub (no secrets exposed)

#### <a name="_wlntq6v0i7yz"></a>**Day 3**
### <a name="_4iqs3drg3min"></a>**Web Servers, Databases & Plivo Voice**
**Goal:** Understand how web servers work, why they're needed for Plivo webhooks, and build a voice IVR with persistent storage.

**Shorts to watch first**

- [**Flask in 100 Seconds - Fireship**](https://youtube.com/watch?v=Z1RJmh_OqeA)
- [**Webhooks Explained - Fireship**](https://youtube.com/watch?v=41NOoEz3Tzc)
- [**ngrok in 100 Seconds**](https://youtube.com/watch?v=UaxqJUXqvro)
- [**Redis in 100 Seconds - Fireship**](https://youtube.com/watch?v=G1rOthIU-uo)
- [**PostgreSQL in 100 Seconds - Fireship**](https://youtube.com/watch?v=n2Fluyr3lbc)

**Part 1: Flask Fundamentals (Learn from Claude, Verify Understanding)**

Ask Claude (browser) to explain these concepts — don't memorize, just understand the "why":

**Why Flask vs Plain Python Scripts?**

- A Python script runs once and exits
- Flask is a web server — it runs continuously, waiting for requests
- Plivo needs to "call back" your code when something happens (incoming call, SMS received)
- Your code needs to be reachable via a URL — Flask provides that

**Core Flask Concepts:**

- **Routes:** URLs that your server responds to (e.g., /answer-call, /handle-input)
- **GET vs POST:** GET retrieves data, POST sends data. Plivo webhooks use POST (sending call details to you)
- **Starting Flask:** flask run or python app.py — server starts and listens on a port (usually 5000)
- **Request/Response:** Plivo sends a request with call info → your Flask route processes it → returns XML response

**Verification:** Can you explain to someone why a plain Python script won't work for handling Plivo callbacks?


**Part 2: ngrok — Making Your Local Server Reachable**

Ask Claude (browser) to explain:

**The Problem:**

- Your Flask server runs on localhost:5000 — only your computer can access it
- Plivo's servers are on the internet — they can't reach your localhost
- You need a public URL that forwards to your local machine

**ngrok's Role:**

- ngrok creates a tunnel: https://abc123.ngrok.io → localhost:5000
- Plivo can now send webhooks to your public ngrok URL
- Your local Flask server receives the request and responds

**Why Not Just Deploy?**

- During development, you want fast iteration
- Change code → save → test immediately (no deploy wait)
- ngrok is for development only; production uses real servers

**Verification:** Can you draw (on paper) the flow: Phone call → Plivo → ngrok → your Flask server → response back?

**Part 3: Redis & PostgreSQL Setup**

**Install via Homebrew:**

bash

brew install redis

brew install postgresql@15

brew services start redis

brew services start postgresql@15

**Install a Database Viewer:**

- Install[ ](https://tableplus.com/)[TablePlus](https://tableplus.com/) (free tier available) or[ ](https://dbeaver.io/)[DBeaver](https://dbeaver.io/) (free)
- These let you visually browse your database tables, run queries, see data

**Ask Claude (browser) to explain:**

**Redis — What & Why:**

- In-memory data store (very fast, data lives in RAM)
- Use cases: caching, session storage, real-time counters
- Data can expire automatically (TTL - time to live)
- For our IVR: store active call state, track caller through menu navigation

**PostgreSQL — What & Why:**

- Relational database (data persists to disk)
- Use cases: permanent storage, structured data, queries
- For our IVR: store call logs, caller history, menu configurations

**SQLAlchemy — What & Why:**

- Python library to interact with databases
- Write Python code instead of raw SQL
- Handles connections, queries, and data mapping

**Verification:**

- Open TablePlus, connect to your local PostgreSQL (host: localhost, user: your Mac username, no password)
- Can you see the connection works?
- Run redis-cli ping in terminal — should return PONG

**Part 4: Plivo Voice Fundamentals**

**Set Up:**

- Create Plivo account, get Auth ID and Auth Token
- Buy a phone number with voice capability
- Read[ ](https://www.plivo.com/docs/voice/)[Plivo Voice Quickstart docs](https://www.plivo.com/docs/voice/)

**Ask Claude (browser) to explain:**

**How Plivo Voice Works:**

1. Someone calls your Plivo number
1. Plivo sends a webhook (POST request) to your server with call details
1. Your server responds with XML instructions (what to say, what to do)
1. Plivo executes those instructions

**Key XML Elements:**

- <Speak> — text-to-speech, say something to caller
- <Play> — play an audio file
- <GetDigits> — wait for caller to press buttons, then send those digits to another webhook
- <Redirect> — send call to a different URL for next instructions

**Verification:** Look at a Plivo XML example in the docs. Can you identify what each element does?
####
#### <a name="_ho1dxavcrf3v"></a><a name="_9ojyjq6cdcfe"></a>**Day 4**
**Mini-Projects**

**Project 1: Basic Flask Server with ngrok**

Ask Claude Code to build a Flask server that:

- Has a route /health that returns {"status": "ok"} (GET request)
- Has a route /webhook-test that accepts POST, logs whatever data is received, returns {"received": true}
- Runs on port 5000

**Your job:**

1. Run the Flask server
1. Open browser, go to http://localhost:5000/health — verify you see the JSON response
1. Start ngrok: ngrok http 5000
1. Copy the ngrok URL (e.g., https://abc123.ngrok.io)
1. Use Claude Code to write a quick script that sends a POST request to your ngrok URL /webhook-test
1. Check your Flask terminal — verify the data was logged

**Verification Checklist:**

- Flask server running
- Health endpoint works in browser
- ngrok tunnel active
- POST to ngrok URL received by local Flask


**Project 2: PostgreSQL + SQLAlchemy Integration**

Ask Claude Code to extend your Flask app:

- Add SQLAlchemy with PostgreSQL connection
- Create a CallLog model with fields: id, caller\_number, called\_number, call\_status, created\_at
- Add a route /log-call (POST) that creates a new call log entry
- Add a route /call-logs (GET) that returns all call logs as JSON

**Your job:**

1. Run the app (it should create the table automatically)
1. Open TablePlus, connect to PostgreSQL, verify call\_logs table exists
1. Use Claude Code to write a test script that POSTs fake call data to /log-call
1. Refresh TablePlus — verify the row appears
1. Hit /call-logs in browser — verify you see the data as JSON

**Verification Checklist:**

- PostgreSQL connection working
- Table visible in TablePlus
- Can insert data via API
- Can read data via API and in TablePlus

**Project 3: Redis for Call State**

Ask Claude Code to add Redis to your Flask app:

- Connect to local Redis
- Add a route /start-session/<caller\_id> that stores {caller\_id: {"step": "greeting", "started\_at": timestamp}} in Redis with 30-minute expiry
- Add a route /get-session/<caller\_id> that retrieves the session
- Add a route /update-session/<caller\_id>/<step> that updates the step value

**Your job:**

1. Test the session flow: start → get → update → get
1. Verify in terminal using redis-cli:
   1. redis-cli KEYS \* — see your session keys
   1. redis-cli GET <key> — see the data
   1. redis-cli TTL <key> — see time remaining before expiry
1. Wait 30 minutes (or set shorter TTL for testing) — verify session auto-deletes

**Verification Checklist:**

- Can create session via API
- Can see session in redis-cli
- Session has correct TTL
- Session auto-expires

**Project 4: Plivo Voice IVR with Full Stack**

Ask Claude Code to build a complete IVR system using Flask + Plivo Python SDK + Redis + PostgreSQL:

**Requirements:**

- Route /answer — Plivo calls this when someone dials in
  - Store call session in Redis (caller number, current step = "main\_menu")
  - Log call start in PostgreSQL
  - Return XML: "Welcome to Acme Corp. Press 1 for Sales, Press 2 for Support, Press 3 to hear your caller ID"
- Route /handle-input — Plivo calls this with digit pressed
  - Read current session from Redis
  - Update session step based on input
  - If 1: Return XML "Connecting to sales. Goodbye." + update call log with status "routed\_sales"
  - If 2: Return XML "Connecting to support. Goodbye." + update call log with status "routed\_support"
  - If 3: Read caller's phone number from Plivo request, return XML speaking their number back
  - Invalid input: Return XML "Invalid option" and redirect back to /answer
- Route /call-history/<phone\_number> (GET) — Returns all past calls from that number as JSON

**Your job:**

1. **Setup:**
   1. Get your ngrok URL
   1. In Plivo console, set your phone number's Answer URL to https://your-ngrok.io/answer
1. **Test the flow:**
   1. Call your Plivo number from your phone
   1. Verify you hear the greeting
   1. Press 1 — verify you hear "Connecting to sales"
   1. Call again, press 3 — verify it reads your phone number back
   1. Call again, press 9 — verify it says "Invalid option" and replays menu
1. **Verify data layer:**
   1. Check Redis (redis-cli) — see active call session during call
   1. Check PostgreSQL (TablePlus) — see call log entries after each call
   1. Hit /call-history/<your-phone> — verify your calls appear
1. **Test edge cases:**
   1. What happens if caller hangs up mid-call? (Check if call log captures this)
   1. What happens if Redis is down? (Stop Redis, make a call — does it fail gracefully?)

**Verification Checklist:**

- Answer URL configured in Plivo console
- Can call and hear greeting
- All 3 menu options work correctly
- Invalid input handled properly
- Sessions visible in Redis during active calls
- Call logs written to PostgreSQL
- Call history API returns correct data

**End of Project Checklist**

- Can explain why Flask is needed for webhooks (vs plain scripts)
- Can explain ngrok's role in development
- Redis installed and running (redis-cli ping returns PONG)
- PostgreSQL installed and running
- TablePlus connected to PostgreSQL
- Project 1: Flask + ngrok working
- Project 2: PostgreSQL read/write verified in TablePlus
- Project 3: Redis sessions working with TTL
- Project 4: Full IVR working end-to-end
- Project 4: Can see data in both Redis and PostgreSQL
- Made at least 5 test calls to verify all menu paths


#### <a name="_hmtbya2wzoka"></a>**Day 5**
## <a name="_cs54kwhwzxo0"></a>**Cloud Deployment with Vercel**
**Goal:** Deploy your IVR app to production using Vercel with managed Redis and Postgres, all provisioned directly through Vercel's dashboard.

### <a name="_ud2f1decr1sg"></a>**Shorts to Watch First**
- [Vercel in 100 Seconds - Fireship](https://youtube.com/watch?v=JgKLOVNBeZY)
- [Serverless Functions in 100 Seconds - Fireship](https://youtube.com/watch?v=W_VV2Fx32_Y)

### <a name="_lnq6n4vjtdye"></a>**Prerequisites: Sign Up for Vercel**

|**Service**|**Sign Up URL**|**What You Need**|
| :-: | :-: | :-: |
|**Vercel**|[vercel.com/signup](https://vercel.com/signup)|Connect your GitHub account|

That's it — Redis and Postgres are provisioned directly through Vercel's Storage tab. No separate signups needed.

**Your job:**

- Create Vercel account
- Connect your GitHub account during signup

**Verification:** Can you log into Vercel dashboard and see your GitHub repos?

### <a name="_mee0uldxroeg"></a>**Part 1: Understanding Local vs Production (Learn from Claude)**
Ask Claude (browser) to explain:

**Why Can't We Just Run Flask + ngrok Forever?**

- Your laptop turns off, loses internet, changes IP
- ngrok URLs change every restart (unless paid)
- No redundancy — laptop crashes = service down
- Production needs: always-on, scalable, reliable

**Serverless vs Traditional Servers:**

- Traditional: Rent a server, runs 24/7, pay monthly
- Serverless: Code runs only when triggered, pay per request, scales automatically
- Vercel = serverless (perfect for webhooks!)

**Managed Databases vs Local:**

- Local PostgreSQL/Redis: Only accessible from your machine, data lost if you don't back up
- Vercel Storage: Accessible from anywhere, backed up, managed for you, environment variables auto-configured

**Verification:** Can you explain why ngrok + local databases won't work for a real production app?

### <a name="_bg0e3uhg87c"></a>**Part 2: Vercel Storage Options (Learn from Claude)**
Ask Claude (browser) to explain:

**Vercel Storage Marketplace:**

- Go to any project → **Storage** tab → **Create Database**
- Vercel partners with best-in-class providers but you manage everything through Vercel
- **Redis** (powered by Upstash): Key-value store for sessions, caching
- **Postgres** (powered by Neon): Relational database for structured data
- Environment variables are **automatically added** to your project

**How Vercel Serverless Functions Work:**

- Your Flask routes become serverless functions in /api folder
- Each request spins up a function, runs your code, returns response
- No server to manage — Vercel handles scaling

**Verification:** Can you explain what happens when Plivo sends a webhook to your Vercel URL?

###
### <a name="_orgmlak2fhi1"></a><a name="_s688thykv7zu"></a>**Mini-Projects**

### <a name="_t50h0v5ihfwy"></a>**Project 1: Deploy Basic Flask to Vercel**
Ask Claude Code to convert your Day 4 Flask app for Vercel:

**Requirements:**

- Restructure project for Vercel serverless functions
- Create vercel.json configuration
- Create an /api/health endpoint that returns {"status": "ok"}
- Create an /api/webhook-test endpoint that accepts POST and returns the received data

**Your job:**

1. **Restructure the project:**
   1. Ask Claude Code to create Vercel-compatible structure
   1. Verify it creates /api folder with Python files
1. **Install Vercel CLI:**

bash

   npm install -g vercel

3. **Deploy:**

bash

   vercel

- Follow prompts to link to your Vercel account
- Say "Yes" to link to existing project or create new
- Note the URL: https://your-project.vercel.app
4. **Test:**
   1. Visit https://your-project.vercel.app/api/health in browser
   1. Use Claude Code to write a script that POSTs to /api/webhook-test
   1. Check Vercel dashboard → **Logs** to see the request

**Verification Checklist:**

- Project restructured for Vercel
- vercel CLI installed
- Deployed successfully
- Health endpoint works
- Webhook test endpoint receives POST data
- Can see logs in Vercel dashboard

### <a name="_hstgk1gv9u2"></a>**Project 2: Add Redis via Vercel Storage**
**Provision Redis through Vercel (no separate signup):**

1. Go to[ ](https://vercel.com/dashboard)[vercel.com/dashboard](https://vercel.com/dashboard)
1. Click on your deployed project
1. Go to **Storage** tab
1. Click **Create Database**
1. Select **Redis** (powered by Upstash)
1. Name it ivr-sessions
1. Select region closest to you
1. Click **Create**
1. When prompted, click **Connect to Project** → select your project
1. Vercel automatically adds these environment variables:
   1. KV\_REST\_API\_URL
   1. KV\_REST\_API\_TOKEN
   1. KV\_URL

Ask Claude Code to add Redis session management:

**Requirements:**

- Connect to Redis using KV\_REST\_API\_URL and KV\_REST\_API\_TOKEN environment variables
- Use the @upstash/redis package or HTTP REST API
- Create /api/start-session that stores {"step": "greeting", "started\_at": timestamp} with 30-min TTL
- Create /api/get-session that retrieves session by caller ID
- Create /api/update-session that updates session step

**Your job:**

1. **Redeploy to pick up new environment variables:**

bash

   vercel --prod

2. **Test session endpoints:**
   1. POST to /api/start-session?caller\_id=+1234567890
   1. GET /api/get-session?caller\_id=+1234567890 — verify session exists
   1. POST to /api/update-session?caller\_id=+1234567890&step=menu\_selection
   1. GET again — verify step updated
2. **Verify in Vercel dashboard:**
   1. Go to **Storage** → click on your Redis database
   1. Click **Data Browser** tab
   1. See your session keys and values

**Verification Checklist:**

- Redis created via Vercel Storage tab
- Connected to your project
- Environment variables auto-configured (check Settings → Environment Variables)
- Session endpoints working
- Can see data in Data Browser
- Sessions expire after TTL
-----
### <a name="_eb6p5i2moy7n"></a>**Project 3: Add Postgres via Vercel Storage**
**Provision Postgres through Vercel (no separate signup):**

1. Go to Vercel dashboard → your project → **Storage** tab
1. Click **Create Database**
1. Select **Postgres** (powered by Neon)
1. Name it ivr-call-logs
1. Select region (same as your Redis for lowest latency)
1. Click **Create**
1. Click **Connect to Project** → select your project
1. Vercel automatically adds these environment variables:
   1. POSTGRES\_URL
   1. POSTGRES\_PRISMA\_URL
   1. POSTGRES\_URL\_NON\_POOLING
   1. POSTGRES\_USER
   1. POSTGRES\_HOST
   1. POSTGRES\_PASSWORD
   1. POSTGRES\_DATABASE

Ask Claude Code to add Postgres for call logs:

**Requirements:**

- Connect to Postgres using POSTGRES\_URL environment variable
- Create /api/setup-db that creates the call\_logs table (run once)
- Create /api/log-call (POST) that inserts a call record
- Create /api/call-logs (GET) that returns all logs as JSON
- Create /api/call-history/[phone] that returns logs for a specific number

**Your job:**

1. **Redeploy:**

bash

   vercel --prod

2. **Initialize database:**
   1. Hit /api/setup-db once in browser to create the table
   1. Should return {"message": "Table created successfully"}
2. **Test CRUD operations:**
   1. Use Claude Code to write a script that POSTs fake call data to /api/log-call
   1. GET /api/call-logs — verify data appears
   1. GET /api/call-history/+1234567890 — verify filtering works
2. **Verify in Vercel dashboard:**
   1. Go to **Storage** → click on your Postgres database
   1. Click **Data** tab to browse tables
   1. Or click **Query** tab and run: SELECT \* FROM call\_logs;

**Verification Checklist:**

- Postgres created via Vercel Storage tab
- Connected to your project
- Environment variables auto-configured
- Table created successfully
- Can insert call logs via API
- Can read call logs via API
- Can filter by phone number
- Data visible in Vercel Storage Data tab

### <a name="_psbp4jakagro"></a>**Project 4: Full IVR Deployment to Vercel**
Ask Claude Code to deploy the complete IVR system:

**Requirements:**

- All IVR routes as Vercel serverless functions:
  - /api/answer — Plivo calls this on incoming call
  - /api/handle-input — Plivo calls this with digit pressed
  - /api/call-history/[phone] — Returns call history for a number
- Redis for session state (using Vercel's Redis)
- Postgres for call logs (using Vercel's Postgres)
- Plivo SDK for generating XML responses
- Read all credentials from environment variables

**Your job:**

1. **Add Plivo credentials to Vercel:**
   1. Go to Vercel dashboard → your project → **Settings** → **Environment Variables**
   1. Add PLIVO\_AUTH\_ID → paste your Auth ID
   1. Add PLIVO\_AUTH\_TOKEN → paste your Auth Token
   1. Select all environments (Production, Preview, Development)
   1. Click **Save**
1. **Deploy:**

bash

   vercel --prod

3. **Configure Plivo to use your Vercel URL:**
   1. Go to Plivo console → **Phone Numbers** → click your number
   1. Set **Answer URL** to: https://your-project.vercel.app/api/answer
   1. Set **Method** to: POST
   1. Click **Save**
3. **Test the full flow:**
   1. Call your Plivo number from your phone
   1. Verify you hear: "Welcome to Acme Corp. Press 1 for Sales..."
   1. Press 1 → hear "Connecting to sales. Goodbye."
   1. Call again, press 2 → hear "Connecting to support. Goodbye."
   1. Call again, press 3 → hear your phone number read back
   1. Call again, press 9 → hear "Invalid option" and menu replays
3. **Verify data persistence:**
   1. During an active call: Go to Vercel Storage → Redis → Data Browser → see session
   1. After calls: Go to Vercel Storage → Postgres → Data tab → see call log entries
   1. Hit /api/call-history/<your-phone> in browser → see your calls as JSON
3. **Test with an external caller:**
   1. Have a colleague or friend call your Plivo number
   1. Verify it works for them too
   1. Check that their call appears in the call logs

**Verification Checklist:**

- Plivo credentials added to Vercel Environment Variables
- IVR deployed to production URL
- Plivo Answer URL updated to Vercel (no more ngrok!)
- Can call and hear greeting
- Press 1 → Sales message works
- Press 2 → Support message works
- Press 3 → Phone number readback works
- Press 9 → Invalid input handling works
- Sessions visible in Redis Data Browser during calls
- Call logs visible in Postgres Data tab
- /api/call-history endpoint returns correct data
- Works for external callers

### <a name="_1vythqvrruhq"></a>**Project 5: Production Health Check & Monitoring**
Ask Claude Code to add production-ready health monitoring:

**Requirements:**

- /api/health endpoint that checks:
  - Redis connectivity (try to ping)
  - Postgres connectivity (try a simple query)
  - Returns: {"status": "healthy", "redis": "ok", "postgres": "ok", "timestamp": "..."}
  - If any service fails: {"status": "unhealthy", "redis": "error", "postgres": "ok", "error": "..."}
- Proper error handling in all IVR routes that logs errors (visible in Vercel Logs)

**Your job:**

1. **Deploy and test health check:**

bash

   vercel --prod

- Hit /api/health — verify all services show "ok"
2. **Explore Vercel dashboard monitoring:**
   1. **Deployments** tab: See all your deploys, rollback if needed
   1. **Logs** tab: See real-time request logs and errors
   1. **Analytics** tab: See traffic patterns (may need to enable)
   1. **Storage** tab: Monitor database usage
2. **Test error scenarios:**
   1. Make a call and check Vercel Logs — see the request/response flow
   1. Intentionally cause an error (e.g., invalid input) — verify it's logged

**Verification Checklist:**

- Health endpoint checks Redis and Postgres connectivity
- Health endpoint returns proper status
- Can view real-time logs in Vercel dashboard
- Can see deployment history
- Understand how to rollback if needed
- Errors are logged and visible




<a name="_8521i8607v06"></a>Week 2 - AI Agents

**Goal: Understand LLM APIs, Speech AI (STT/TTS), and build production-ready voice AI agents using Pipecat and LiveKit, deployed publicly.**
##
## <a name="_k4dpx5e3qnuo"></a><a name="_ojbhdcsf7o7w"></a>**Prerequisites: Sign Up for All Services (Do This First)**
**Complete these signups before starting Week 2. All have free tiers sufficient for learning.**

|**Service**|**Sign Up URL**|**What You Need**|
| :- | :-: | :-: |
|**OpenAI**|[**platform.openai.com**](https://platform.openai.com)|**API key, add $5-10 credits**|
|**Deepgram**|[**console.deepgram.com**](https://console.deepgram.com)|**API key (free $200 credits)**|
|**ElevenLabs**|[**elevenlabs.io**](https://elevenlabs.io)|**API key (free tier: 10k chars/month)**|
|**LiveKit Cloud**|[**cloud.livekit.io**](https://cloud.livekit.io)|**Free tier account**|
|**Railway**|[**railway.app**](https://railway.app)|**For deployment (free tier: $5/month credits)**|
##
##
## <a name="_dx7fb9sftzyy"></a><a name="_3tpux8pvhmjf"></a><a name="_up51y2qocn99"></a>**Day 1:** 
## <a name="_qrahwib9jcxu"></a>**LLM APIs — The Brain of Your Agent**
**Goal:** Understand how LLMs work via APIs, make your first API calls, and build a conversational chatbot.

### <a name="_nc63cd20zxdf"></a>**Shorts to Watch First**
- [GPT-4 in 100 Seconds - Fireship](https://youtube.com/watch?v=--khbXchTeE)
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer) — interactive tool to see how tokens work

### <a name="_gov7wsnmmiko"></a>**Part 1: LLM Fundamentals (Learn from Claude)**
Ask Claude (browser) to explain these concepts:

**Tokens:**

- LLMs don't see words, they see "tokens" (word pieces)
- "Hello world" = 2 tokens, "Authentication" = 1-2 tokens
- Why it matters: You pay per token, context has token limits
- Rule of thumb: 1 token ≈ 4 characters or ¾ of a word

**Context Window:**

- The "memory" of a single conversation
- GPT-5.2: 128k tokens
- Everything (system prompt + conversation history + your message) must fit
- For voice AI: Keep it small for low latency

**Temperature:**

- Controls randomness/creativity (0.0 to 2.0)
- 0.0 = deterministic, same input → same output
- 1.0 = creative, varied responses
- For voice AI: Usually 0.7-0.8 (natural but not wild)

**Streaming:**

- Normal: Wait for full response, then display
- Streaming: Get response token-by-token as it's generated
- For voice AI: Essential! Start speaking before full response is ready

**System Prompts:**

- Instructions that define the AI's personality and behavior
- Set at the start of conversation, persists throughout
- For voice AI: "You are a helpful receptionist for Acme Corp..."

**Verification:** Can you explain to someone what happens if your context window fills up? (Answer: Oldest messages get dropped or you get an error)

### <a name="_txk1qonoxkem"></a>**Part 2: API Structure (Learn from Claude)**
Ask Claude (browser) to explain the anatomy of an API call:

**OpenAI Chat Completions API:**

python

response = openai.chat.completions.create(

`    `model="gpt-4o",

`    `messages=[

`        `{"role": "system", "content": "You are a helpful assistant."},

`        `{"role": "user", "content": "Hello!"},

`        `{"role": "assistant", "content": "Hi there! How can I help?"},

`        `{"role": "user", "content": "What's the weather?"}

`    `],

`    `temperature=0.7,

`    `max\_tokens=150,

`    `stream=True  *# For streaming*

)

\```

\*\*Message Roles:\*\*

\- `system`: Instructions for the AI (set once)

\- `user`: Human messages

\- `assistant`: AI responses (include previous ones for context)



**Verification:** Why do we include previous assistant messages in the messages array?


*### Mini-Projects*

\---

*### Project 1: First OpenAI API Call*

Ask Claude Code to create a Python script that:

\*\*Requirements:\*\*

\- Loads API key from `.env` file

\- Makes a simple call to OpenAI GPT-5.2

\- Prints the response

\- Measures and prints response time

\*\*Your job:\*\*

1\. Create `.env` file with your API key:

\```

`   `OPENAI\_API\_KEY=sk-...

\```

2\. Run the script

3\. Try changing the prompt

4\. Try changing temperature (0.0 vs 1.0) — notice the difference?

\*\*Verification Checklist:\*\*

\- [ ] OpenAI API call works

\- [ ] Response printed

\- [ ] Response time measured

\- [ ] Tried different temperatures

\---

*### Project 2: Streaming Responses*

Ask Claude Code to modify the script to:

\*\*Requirements:\*\*

\- Use streaming API

\- Print tokens as they arrive (character by character effect)

\- Measure time-to-first-token (TTFT) vs total time

\*\*Your job:\*\*

1\. Run the streaming version

2\. Notice how text appears incrementally

3\. Note the TTFT — this is when voice AI can start speaking!

4\. Compare TTFT to total response time

\*\*Verification Checklist:\*\*

\- [ ] Streaming works

\- [ ] Can see tokens arriving one by one

\- [ ] Measured TTFT

\- [ ] Understand why TTFT matters for voice AI

\---

*### Project 3: CLI Chatbot*

Ask Claude Code to build a terminal chatbot:

\*\*Requirements:\*\*

\- Interactive loop: user types → AI responds → repeat

\- Maintains conversation history (sends all previous messages)

\- Uses OpenAI GPT-5.2 with streaming

\- System prompt: "You are a helpful assistant. Keep responses concise."

\- Type "quit" to exit

\- Shows token count after each response

\*\*Your job:\*\*

1\. Run the chatbot

2\. Have a multi-turn conversation (5+ exchanges)

3\. Notice how it remembers context from earlier messages

4\. Watch the token count grow with each turn

5\. Try to fill up the context (keep talking until it gets slow or errors)

\*\*Verification Checklist:\*\*

\- [ ] Chatbot runs in terminal

\- [ ] Maintains conversation context

\- [ ] Streaming responses work

\- [ ] Token count displayed

\- [ ] Can quit gracefully

\---

*### Project 4: Function Calling (Tools)*

Ask Claude Code to add function calling to your chatbot:

\*\*Requirements:\*\*

\- Add a "get\_current\_time" function that returns the current time

\- Add a "get\_weather" function (mock it — return fake data)

\- LLM decides when to call functions based on user query

\- Display when a function is called and its result

\*\*Your job:\*\*

1\. Ask "What time is it?" — verify function is called

2\. Ask "What's the weather in Tokyo?" — verify function is called

3\. Ask "Tell me a joke" — verify NO function is called

4\. Understand how the LLM decides when to use tools

\*\*Verification Checklist:\*\*

\- [ ] Time function works

\- [ ] Weather function works

\- [ ] LLM correctly chooses when to call functions

\- [ ] Regular questions work without function calls

\---

*### End of Day 1 Checklist*

| Item | Verified? |

\|------|-----------|

| Can explain tokens, context window, temperature | ☐ |

| Can explain streaming and why it matters | ☐ |

| OpenAI API calls working | ☐ |

| Streaming responses working | ☐ |

| CLI chatbot with history working | ☐ |

| Function calling working | ☐ |

| Understand time-to-first-token concept | ☐ |

\---

## <a name="_554fzdo1by9u"></a>Day 2: 
## <a name="_z3yvk75jkuad"></a>Speech AI — STT & TTS

\*\*Goal:\*\* Understand speech-to-text (STT) and text-to-speech (TTS), work with audio formats, and build scripts that transcribe and generate speech.

\---


*### Part 1: Audio Fundamentals (Learn from Claude)*

Ask Claude (browser) to explain:

\*\*Audio Formats:\*\*

\- \*\*WAV:\*\* Uncompressed, high quality, large files

\- \*\*MP3:\*\* Compressed, smaller files, slight quality loss

\- \*\*PCM:\*\* Raw audio data (what microphones capture)

\- \*\*Opus/WebM:\*\* Modern, efficient, used in real-time streaming

\*\*Sample Rate:\*\*

\- How many audio samples per second (measured in Hz)

\- 8000 Hz (8kHz): Phone quality

\- 16000 Hz (16kHz): Common for speech recognition

\- 44100 Hz (44.1kHz): CD quality

\- Higher = better quality but larger files

\*\*Channels:\*\*

\- Mono (1 channel): Sufficient for voice

\- Stereo (2 channels): Left/right, not needed for voice AI

\*\*Bit Depth:\*\*

\- 16-bit: Standard for speech

\- 24-bit: Higher quality, larger files

\*\*For Voice AI:\*\*

\- Input (STT): 16kHz, mono, 16-bit PCM or WAV

\- Output (TTS): Usually MP3 or PCM for streaming

\*\*Verification:\*\* If someone says "send me 16kHz mono PCM audio," do you understand what they mean?

\---

*### Part 2: Speech-to-Text (STT) with Deepgram*

Ask Claude (browser) to explain:

\*\*How STT Works:\*\*

\- Audio goes in → text comes out

\- Models trained on millions of hours of speech

\- Deepgram uses neural networks optimized for real-time

\*\*Deepgram Features:\*\*

\- \*\*Real-time streaming:\*\* Transcribe as audio arrives

\- \*\*Pre-recorded:\*\* Upload file, get transcript

\- \*\*Diarization:\*\* Identify different speakers

\- \*\*Punctuation:\*\* Automatic punctuation

\- \*\*Language detection:\*\* Auto-detect language

\*\*Key Deepgram Parameters:\*\*

\- `model`: "nova-3" (best accuracy)

\- `language`: "en" for English

\- `punctuate`: true/false

\- `diarize`: true/false (speaker separation)

\*\*Verification:\*\* What's the difference between streaming STT and pre-recorded STT? (Answer: Streaming gives you words as they're spoken; pre-recorded processes entire file at once)

\---

*### Part 3: Text-to-Speech (TTS) with ElevenLabs*

Ask Claude (browser) to explain:

\*\*How TTS Works:\*\*

\- Text goes in → audio comes out

\- Modern TTS uses neural networks for natural-sounding speech

\- ElevenLabs is known for highly realistic voices

\*\*ElevenLabs Features:\*\*

\- \*\*Voice cloning:\*\* Create custom voices

\- \*\*Pre-made voices:\*\* Library of ready-to-use voices

\- \*\*Streaming:\*\* Generate audio chunk by chunk

\- \*\*Multilingual:\*\* Supports many languages

\*\*Key Parameters:\*\*

\- `voice\_id`: Which voice to use

\- `model\_id`: "eleven\_turbo\_v2\_5" (fast) or "eleven\_multilingual\_v2" (quality)

\- `stability`: How consistent the voice is (0-1)

\- `similarity\_boost`: How close to original voice (0-1)

\*\*For Voice AI:\*\*

\- Use streaming TTS to start playing audio before full generation

\- Use "turbo" models for lower latency

\*\*Verification:\*\* Why do we want streaming TTS for voice AI? (Answer: Start playing audio sooner, reduces perceived latency)

\---

*### Mini-Projects*

\---

*### Project 1: Transcribe Audio File with Deepgram*

Ask Claude Code to build a script that:

\*\*Requirements:\*\*

\- Takes an audio file path as input (WAV or MP3)

\- Sends to Deepgram's pre-recorded API

\- Returns the transcript with timestamps

\- Saves transcript to a text file

\*\*Your job:\*\*

1\. Record a short audio clip (use your phone or QuickTime)

2\. Save it as WAV or MP3

3\. Run the script on your recording

4\. Verify the transcript is accurate

5\. Try with different audio qualities

\*\*Verification Checklist:\*\*

\- [ ] Script accepts audio file

\- [ ] Deepgram API call works

\- [ ] Transcript is accurate

\- [ ] Timestamps are included

\- [ ] Saved to text file

\---

*### Project 2: Real-Time Transcription with Deepgram*

Ask Claude Code to build a script that:

\*\*Requirements:\*\*

\- Opens your microphone (use `pyaudio` or `sounddevice`)

\- Streams audio to Deepgram's real-time API via WebSocket

\- Prints words as they're recognized (live!)

\- Press Ctrl+C to stop

\*\*Your job:\*\*

1\. Run the script

2\. Speak into your microphone

3\. Watch words appear in real-time as you speak

4\. Notice the slight delay (latency)

5\. Try speaking fast vs slow

\*\*Verification Checklist:\*\*

\- [ ] Microphone input works

\- [ ] WebSocket connection to Deepgram established

\- [ ] Words appear in real-time

\- [ ] Can stop gracefully with Ctrl+C

\---

*### Project 3: Generate Speech with ElevenLabs*

Ask Claude Code to build a script that:

\*\*Requirements:\*\*

\- Takes text input (from command line or file)

\- Sends to ElevenLabs API

\- Saves generated audio as MP3

\- Plays the audio automatically (use `playsound` or `pygame`)

\*\*Your job:\*\*

1\. Run with a simple sentence

2\. Listen to the output — does it sound natural?

3\. Try different voices (get voice IDs from ElevenLabs dashboard)

4\. Try different stability/similarity settings

5\. Generate a longer paragraph

\*\*Verification Checklist:\*\*

\- [ ] Text sent to ElevenLabs

\- [ ] Audio file generated

\- [ ] Audio plays automatically

\- [ ] Tried different voices

\- [ ] Quality sounds natural

\---

*### Project 4: Streaming TTS with ElevenLabs*

Ask Claude Code to modify the script for streaming:

\*\*Requirements:\*\*

\- Use ElevenLabs streaming API

\- Play audio chunks as they arrive (not after full generation)

\- Measure time-to-first-audio

\*\*Your job:\*\*

1\. Compare time-to-first-audio: streaming vs non-streaming

2\. Notice how streaming starts playing sooner

3\. Try with a long paragraph — streaming advantage is more obvious

\*\*Verification Checklist:\*\*

\- [ ] Streaming API works

\- [ ] Audio plays incrementally

\- [ ] Measured time-to-first-audio

\- [ ] Understand the latency benefit

\---

*### Project 5: Full Pipeline — Speech In → Text → Speech Out*

Ask Claude Code to combine STT and TTS:

\*\*Requirements:\*\*

\- Record audio from microphone (5 seconds)

\- Transcribe with Deepgram

\- Pass transcript to OpenAI for a response

\- Generate speech from response with ElevenLabs

\- Play the audio response

\*\*Your job:\*\*

1\. Run the script

2\. Speak a question (e.g., "What is the capital of France?")

3\. Wait for the AI to respond with speech

4\. Measure total end-to-end latency

This is your first "voice AI" — it's slow and not real-time, but it's the full pipeline!

\*\*Verification Checklist:\*\*

\- [ ] Microphone recording works

\- [ ] Transcription works

\- [ ] LLM response generated

\- [ ] TTS audio generated and plays

\- [ ] Measured end-to-end latency (probably 5-15 seconds — that's okay for now!)

\---

*### End of Day 2 Checklist*

| Item | Verified? |

\|------|-----------|

| Understand audio formats (WAV, PCM, sample rate) | ☐ |

| Deepgram pre-recorded transcription working | ☐ |

| Deepgram real-time transcription working | ☐ |

| ElevenLabs TTS working | ☐ |

| ElevenLabs streaming TTS working | ☐ |

| Full pipeline (STT → LLM → TTS) working | ☐ |

| Understand where latency comes from | ☐ |



Here's the corrected and reformatted Day 3-7 for Google Docs:

##
## <a name="_wptducoqd0xd"></a><a name="_w5vp1oit3w2l"></a>**Day 3**
## <a name="_mhyqlg6ov7r6"></a>**Voice AI Frameworks — Pipecat**
Goal: Learn Pipecat framework for building real-time voice AI agents with proper latency handling.

### <a name="_5mtldytysnhq"></a>**Shorts to Watch First**
- WebSockets in 100 Seconds - Fireship (<https://youtube.com/watch?v=1BfCnjr_Vjg>)
- Search: "Pipecat AI voice agent demo" on YouTube

### <a name="_xc4fkc55eau7"></a>**Part 1: Why Frameworks? (Learn from Claude)**
Ask Claude (browser) to explain:

The Problem with DIY Voice AI:

- Your Day 2 pipeline had 5-15 second latency
- Real conversations need <500ms response time
- Managing streaming, interruptions, turn-taking is complex
- Handling WebSocket connections, audio buffers is error-prone

What Pipecat Solves:

- Pipeline architecture: Audio flows through processors
- Streaming by default: Everything streams end-to-end
- Interruption handling: User can interrupt the AI mid-speech
- Transport agnostic: Works with Plivo, Daily, LiveKit, local audio
- Service integrations: Built-in support for Deepgram, ElevenLabs, OpenAI

Pipecat Architecture:

Audio In → VAD → STT → LLM → TTS → Audio Out

`             `↓

`        `(Voice Activity Detection - detects when user stops speaking)

Key Concepts:

- Frames: Units of data flowing through pipeline (audio, text, control)
- Processors: Transform frames (STT processor, LLM processor, etc.)
- Pipeline: Chain of processors
- Transport: How audio gets in/out (Plivo, Daily, LiveKit, local)

Verification: Why is streaming important for low-latency voice AI? (Answer: Each component can start processing before the previous one finishes)


### <a name="_526yh1jnnmwd"></a>**Part 2: Pipecat Components We'll Use (Learn from Claude)**
Ask Claude (browser) to explain each component:

Our Stack:

- Transport: PlivoTransport (for phone calls via WebSocket audio streaming)
- VAD: SileroVAD (voice activity detection)
- Turn Detection: SmartTurn (semantic turn detection - knows when user is done speaking)
- STT: DeepgramSTTService (real-time transcription)
- LLM: OpenAILLMService with GPT-4.1-mini (fast, streaming)
- TTS: ElevenLabsTTSService (high-quality, streaming)

SileroVAD - What & Why:

- Detects when someone starts speaking
- Detects when someone stops speaking
- Runs locally, very fast
- Essential for knowing when to start/stop listening

SmartTurn - What & Why:

- Goes beyond simple silence detection
- Uses semantic understanding to detect turn completion
- Knows difference between "thinking pause" and "done speaking"
- Reduces false interruptions

Verification: What does VAD do and why is it important? (Answer: Detects speech vs silence, so the system knows when user finished talking)



### <a name="_bxeq2curoafr"></a>**Mini-Projects**


### <a name="_ti9gfchripug"></a>**Project 1: Install Pipecat and Run Example**
Ask Claude Code to:

Requirements:

- Create a new project folder for Pipecat experiments
- Install Pipecat with required dependencies
- Set up .env with all API keys (OpenAI, Deepgram, ElevenLabs)
- Run the basic local audio example from Pipecat

Your job:

Review the example code structure

Verification Checklist:

- Pipecat installed successfully
- All dependencies resolved
- .env file configured
- Can import pipecat without errors

### <a name="_3pd8af59lbb7"></a>**Project 2: Local Voice Bot (Microphone/Speaker)**

Ask Claude Code to build a Pipecat bot that:

Requirements:

- Uses LocalAudioTransport (your mic and speakers)
- Pipeline: Microphone → SileroVAD → Deepgram STT → OpenAI GPT-4.1-mini → ElevenLabs TTS → Speaker
- System prompt: "You are a helpful assistant. Keep responses under 2 sentences."
- Handles interruptions (if you speak while AI is talking, it stops)

Your job:

1. Run the bot
1. Wait for it to initialize
1. Speak a question
1. Listen for the response
1. Try interrupting mid-response — does it stop?
1. Have a 5-turn conversation

Verification Checklist:

- Bot starts and listens
- Transcription works (you can add logging to see it)
- LLM generates response
- TTS plays through speakers
- Interruption handling works
- Latency feels conversational (under 2 seconds)

### <a name="_sv77oty6v9ab"></a>**Project 3: Add SmartTurn for Better Turn Detection**

Ask Claude Code to enhance the bot with SmartTurn:

Requirements:

- Add SmartTurn processor after VAD
- Configure for natural conversation flow
- Log when turns are detected vs simple silence

Your job:

1. Run bot without SmartTurn, note behavior
1. Run bot with SmartTurn, compare behavior
1. Test with sentences that have natural pauses (e.g., "I want to order... hmm... maybe a pizza")
1. Verify SmartTurn waits for you to finish vs interrupting at pauses

Verification Checklist:

- SmartTurn integrated
- Bot waits for complete thoughts
- Doesn't interrupt during thinking pauses
- Feels more natural than VAD alone


### <a name="_ojjm60xhcrkp"></a>**Project 4: Measure and Optimize Latency**

Ask Claude Code to add latency tracking:

Requirements:

- Log timestamp when user stops speaking (VAD end-of-speech)
- Log timestamp when first TTS audio plays
- Calculate and display end-to-end latency
- Display latency after each exchange

Your job:

1. Run multiple conversations
1. Note average latency
1. Try GPT-4.1-mini vs GPT-4o, compare latency
1. Target: under 1.5 seconds end-to-end

Verification Checklist:

- Latency logging implemented
- Measured average latency
- Understand where latency comes from (STT, LLM, TTS)
- Latency under 2 seconds consistently


### <a name="_m0csx5sv60x5"></a>**Project 5: Add Function Calling to Voice Bot**
Ask Claude Code to add tools to your Pipecat bot:

Requirements:

- Add a "get\_current\_time" function
- Add a "tell\_joke" function (returns a random joke)
- Add a "lookup\_order" function (mock data — return fake order status)
- LLM decides when to call functions based on voice query

Your job:

1. Ask "What time is it?" — verify function is called
1. Ask "Tell me a joke" — verify joke is told
1. Ask "What's the status of order 12345?" — verify lookup works
1. Ask a general question — verify no function is called

Verification Checklist:

- Time function works via voice
- Joke function works via voice
- Order lookup works via voice
- Natural questions work without functions
- Function results are spoken naturally


### <a name="_t8xez5iwx2o"></a>**End of Day 3 Checklist**
- Understand Pipecat architecture (frames, processors, pipeline)
- Understand our stack: SileroVAD, SmartTurn, Deepgram, OpenAI, ElevenLabs
- Pipecat installed and running
- Local voice bot working (mic/speaker)
- SmartTurn integrated for better turn detection
- Interruption handling working
- Latency measured (target: under 2 seconds)
- Function calling working via voice


## <a name="_ayvsifg9juzw"></a>**Day 4**
## <a name="_1vlt569uu26x"></a>**Pipecat + Plivo — Phone Calls via WebSocket Audio Streaming**
Goal: Connect your Pipecat voice bot to real phone calls using Plivo's WebSocket audio streaming.


### <a name="_2w25g8e2rwzj"></a>**Part 1: How Plivo Audio Streaming Works (Learn from Claude)**
Ask Claude (browser) to explain:

Plivo Audio Streaming Flow:

Caller's Phone 

`    `↓

Plivo (receives call)

`    `↓

WebSocket connection to your server

`    `↓

Your Pipecat bot receives audio frames

`    `↓

Pipecat processes: VAD → STT → LLM → TTS

`    `↓

Audio frames sent back via WebSocket

`    `↓

Plivo plays audio to caller

Key Concepts:

Audio Format from Plivo:

- Format: mulaw (μ-law) or linear16
- Sample rate: 8kHz (phone quality)
- Mono channel

Bidirectional WebSocket:

- Plivo sends audio TO your server
- Your server sends audio BACK to Plivo
- Real-time, full-duplex communication

Answer URL vs Stream URL:

- Answer URL: Plivo calls this when someone dials in, returns XML
- The XML tells Plivo to start streaming to your WebSocket URL

Verification: What happens when someone calls your Plivo number? (Answer: Plivo hits your Answer URL, gets XML instructions, then opens WebSocket to stream audio)


### <a name="_p1h0rnlwx7la"></a>**Part 2: Plivo Transport in Pipecat (Learn from Claude)**
Ask Claude (browser) to explain:

PlivoTransport:

- Built-in Pipecat transport for Plivo audio streaming
- Handles WebSocket connection from Plivo
- Converts Plivo audio format to Pipecat frames
- Converts Pipecat audio frames back to Plivo format

Configuration Needed:

- WebSocket server endpoint (your server URL)
- Audio format settings (mulaw/linear16, sample rate)
- Answer URL that returns Plivo XML

Verification: What does PlivoTransport handle for you? (Answer: WebSocket connection, audio format conversion, bidirectional streaming)


### <a name="_lxh8umt5gn7d"></a>**Mini-Projects**


### <a name="_2myrwzyheluk"></a>**Project 1: Basic Plivo WebSocket Server**
Ask Claude Code to build a basic server that:

Requirements:

- Flask app with an /answer endpoint that returns Plivo XML
- XML tells Plivo to stream audio to a WebSocket endpoint
- WebSocket server that logs when Plivo connects
- Logs when audio packets arrive (don't process yet)

Your job:

1. Run the server locally
1. Start ngrok: ngrok http 5000
1. Configure Plivo phone number:
   1. Go to Plivo console → Phone Numbers → your number
   1. Set Answer URL to: <https://your-ngrok-url/answer>
   1. Set Method to: POST
1. Call your Plivo number from your phone
1. Watch the logs — see WebSocket connect and audio packets

Verification Checklist:

- Flask server running
- ngrok tunnel active
- Plivo Answer URL configured
- Can call and see WebSocket connection
- Audio packets logging


### <a name="_jhooq74avy1"></a>**Project 2: Pipecat Bot with Plivo Transport**
Ask Claude Code to create a full Pipecat bot with Plivo:

Requirements:

- Use PlivoTransport for audio I/O
- Pipeline: PlivoTransport → SileroVAD → SmartTurn → Deepgram STT → OpenAI GPT-4.1-mini → ElevenLabs TTS → PlivoTransport
- System prompt: "You are a helpful phone assistant. Keep responses brief and conversational."
- Handle the Plivo audio format correctly (mulaw, 8kHz)
- Flask endpoint for /answer that returns streaming XML

Your job:

1. Run the Pipecat bot server
1. Start ngrok
1. Update Plivo Answer URL to your ngrok URL
1. Call your Plivo number
1. Have a conversation!

Verification Checklist:

- Bot answers phone call
- You hear a greeting (or bot waits for you to speak)
- Transcription works over phone
- LLM responds appropriately
- You hear TTS response clearly
- Multi-turn conversation works


### <a name="_sg94srhd11eh"></a>**Project 3: AI Receptionist**
Ask Claude Code to build a complete AI receptionist:

Requirements:

System Prompt:

You are a friendly receptionist for Acme Corp. 

When someone calls:

1\. Greet them: "Hello, thank you for calling Acme Corp. How can I help you today?"

2\. Listen to their request

3\. If they want sales: Say "I'll connect you to our sales team. One moment please." then end gracefully.

4\. If they want support: Say "I'll connect you to support. Can you briefly describe your issue?"

5\. If they ask about hours: Say "We're open Monday to Friday, 9 AM to 5 PM Pacific time."

6\. If they ask about location: Say "We're located at 123 Main Street, San Francisco."

7\. If unclear: Say "I'm sorry, could you repeat that?"

Keep responses brief and natural. Don't be robotic.

Function Calling:

- get\_business\_hours() - returns hours
- get\_location() - returns address
- transfer\_to\_sales() - logs intent, says transferring
- transfer\_to\_support() - logs intent, says transferring

Logging:

- Log each call to Vercel Postgres (from Week 1)
- Store: caller\_number, transcript, detected\_intent, duration, timestamp

Your job:

1. Deploy with ngrok
1. Test all scenarios:
   1. Call and ask about sales
   1. Call and ask about hours
   1. Call and ask about location
   1. Call and say something unclear
1. Check Vercel Postgres for logs after each call

Verification Checklist:

- Answers with greeting
- Sales intent handled correctly
- Support intent handled correctly
- Hours FAQ works
- Location FAQ works
- Unclear queries handled gracefully
- All calls logged to Postgres with transcript


### <a name="_30jmc0fvzmj0"></a>**Project 4: Improve Conversation Quality**
Ask Claude Code to add these enhancements:

Requirements:

- Better interruption handling: Stop TTS immediately when caller speaks
- Conversation context: Remember what was discussed earlier in the call
- Graceful ending: "Is there anything else I can help you with?" → "Thank you for calling. Goodbye!"
- Error recovery: If STT fails, say "I'm having trouble hearing you, could you repeat that?"

Your job:

1. Test interruption: Start speaking while bot is talking
1. Test context: Ask a follow-up question ("What about weekends?" after asking about hours)
1. Test ending: Say "That's all, thanks"
1. Test error: Make noise/mumble, see if it recovers

Verification Checklist:

- Interruptions stop TTS immediately
- Bot remembers context within call
- Ending is natural
- Errors handled gracefully


### <a name="_cpxvp71svz5q"></a>**End of Day 4 Checklist**
- Understand Plivo WebSocket audio streaming
- Basic WebSocket server receiving Plivo audio
- Pipecat bot with PlivoTransport working
- Can have phone conversations with AI
- AI Receptionist with intent detection working
- Function calling working (hours, location, transfers)
- Call logging to Vercel Postgres working
- Conversation quality improvements implemented


##
## <a name="_nbht2cof024m"></a><a name="_3qimm0xyrbal"></a>**Day 5**
## <a name="_38ksihbomo8q"></a>**LiveKit with Plivo SIP Trunking — Alternative Approach**
Goal: Learn LiveKit as an alternative to Pipecat, using Plivo SIP trunking for phone connectivity.


### <a name="_w8fpqji7v1uw"></a>**Shorts to Watch First**
- WebRTC in 100 Seconds - Fireship (<https://youtube.com/watch?v=WmR9IMUD_CY>)


### <a name="_zam6bzha3nki"></a>**Part 1: LiveKit vs Pipecat (Learn from Claude)**
Ask Claude (browser) to explain:

Two Different Approaches:

Pipecat + Plivo WebSocket (Day 4):

- Plivo streams raw audio over WebSocket
- Your Pipecat server processes audio directly
- You manage the audio pipeline
- More control, more code

LiveKit + Plivo SIP (Day 5):

- Plivo forwards calls via SIP trunk to LiveKit
- LiveKit handles WebRTC/media
- Phone caller appears as a "participant" in a LiveKit room
- Your AI agent is another "participant"
- LiveKit manages audio routing
- Less code, more abstraction

When to Use Each:

Use Pipecat + Plivo WebSocket when:

- You want full control over audio processing
- You need custom audio manipulation
- You're building on Plivo's infrastructure

Use LiveKit + SIP when:

- You want simpler architecture
- You also need browser/mobile WebRTC support
- You want LiveKit's built-in features (recording, rooms, etc.)

Verification: What's the main difference between these approaches? (Answer: Pipecat handles audio directly; LiveKit treats phone as a room participant)


### <a name="_ygujqle7t48w"></a>**Part 2: LiveKit Fundamentals (Learn from Claude)**
Ask Claude (browser) to explain:

LiveKit Concepts:

- Room: Virtual space where participants connect
- Participant: Anyone in a room (human, bot, phone caller)
- Track: Audio or video stream
- Token: JWT for authentication

LiveKit Cloud vs Self-Hosted:

- LiveKit Cloud: Managed service, free tier, no setup
- Self-hosted: Run your own (more complex)
- For learning: Use LiveKit Cloud

SIP Trunking with LiveKit:

- Plivo SIP trunk connects to LiveKit
- Incoming phone call → LiveKit creates participant
- Your agent joins same room
- LiveKit routes audio between them

LiveKit Agents Framework:

- LiveKit's own agent framework (similar to Pipecat)
- Integrates with Deepgram, OpenAI, ElevenLabs
- Handles VAD, turn detection, pipeline

Verification: In the LiveKit model, what is a phone caller? (Answer: A participant in a LiveKit room, just like a browser user)


### <a name="_du35c0up3pn6"></a>**Mini-Projects**


### <a name="_640ywshmw8n8"></a>**Project 1: Set Up LiveKit Cloud**
Your job (manual setup):

1. Go to cloud.livekit.io
1. Create a new project
1. Note your:
   1. API Key
   1. API Secret
   1. WebSocket URL (wss://your-project.livekit.cloud)
1. Add to your .env:

LIVEKIT\_API\_KEY=your-api-key

LIVEKIT\_API\_SECRET=your-api-secret

LIVEKIT\_URL=wss://your-project.livekit.cloud

Ask Claude Code to create a token generation script:

Requirements:

- Generate a LiveKit access token for a room
- Token allows publishing and subscribing audio
- Print the token

Verification Checklist:

- LiveKit Cloud account created
- API credentials saved in .env
- Token generation script works


### <a name="_19xymnfakj2a"></a>**Project 2: LiveKit Agent (Browser Test First)**
Ask Claude Code to create a LiveKit agent using LiveKit Agents framework:

Requirements:

- Use LiveKit Agents SDK (not Pipecat)
- Pipeline: VAD → Deepgram STT → OpenAI GPT-4.1-mini → ElevenLabs TTS
- Agent joins a room and waits for participants
- When someone joins and speaks, agent responds
- System prompt: "You are a helpful assistant. Keep responses brief."

Your job:

1. Run the agent
1. Open LiveKit Playground: <https://agents-playground.livekit.io/>
1. Connect to your LiveKit project
1. Join a room
1. Speak to the agent
1. Verify you hear responses

Verification Checklist:

- Agent running and connected to LiveKit
- Can join room from browser playground
- Agent hears your speech
- Agent responds with voice
- Latency is acceptable


### <a name="_7o5dxmhqdoe0"></a>**Project 3: Configure Plivo SIP Trunk to LiveKit**
Your job (manual setup with Claude's guidance):

Ask Claude (browser) to explain the steps, then do them:

1. In LiveKit Cloud dashboard:
   1. Go to SIP settings
   1. Create an inbound SIP trunk
   1. Note the SIP URI (something like sip:...@livekit.cloud)
1. In Plivo console:
   1. Create a SIP endpoint pointing to LiveKit's SIP URI
   1. Configure your Plivo phone number to forward to this SIP endpoint
1. Configure LiveKit to dispatch calls to your agent:
   1. Set up dispatch rules so incoming SIP calls create rooms
   1. Your agent auto-joins when a room is created

Ask Claude Code to help update configuration files as needed.

Verification Checklist:

- LiveKit SIP trunk configured
- Plivo SIP endpoint created
- Plivo number forwards to SIP endpoint
- Test call reaches LiveKit


### <a name="_xeeq4nh7jlf1"></a>**Project 4: Phone to LiveKit Agent**
Your job:

1. Ensure your LiveKit agent is running
1. Call your Plivo number from your phone
1. The call should:
   1. Go to Plivo
   1. Forward via SIP to LiveKit
   1. Create a room with you as participant
   1. Your agent joins the room
   1. You can talk to the agent!

Verification Checklist:

- Phone call connects via SIP
- Agent responds to phone caller
- Multi-turn conversation works
- Audio quality acceptable


### <a name="_mebxl4m0n1th"></a>**Project 5: LiveKit AI Receptionist**
Ask Claude Code to build the same receptionist but using LiveKit Agents:

Requirements:

- Same functionality as Day 4 receptionist
- Greeting, intent detection (sales/support/FAQ)
- Function calling for hours, location
- Log calls to Vercel Postgres
- Use LiveKit Agents framework (not Pipecat)

Your job:

1. Deploy the agent
1. Test via phone call
1. Compare to Pipecat version — any differences?
1. Verify logging works

Verification Checklist:

- Receptionist works via phone
- Intent detection works
- FAQs work
- Logging to Postgres works
- Can compare to Pipecat approach


### <a name="_sq8hbcmd5ye8"></a>**Part 3: Comparing Approaches (Learn from Claude)**
After completing both Days 4 and 5, ask Claude to help you compare:

Pipecat + Plivo WebSocket:

- Pros: Full control, works with any transport, flexible
- Cons: More code, manage audio pipeline yourself

LiveKit + Plivo SIP:

- Pros: Simpler, LiveKit handles media routing, easy browser support
- Cons: Depends on LiveKit, less control

For Plivo customers:

- Pipecat approach is more direct (Plivo → your server)
- LiveKit approach adds a layer but simplifies browser support

Verification: Which approach would you use for a production Plivo voice AI? (Answer: Depends on requirements — Pipecat for control, LiveKit for simplicity and browser support)


### <a name="_kq5gtmr8f8tl"></a>**End of Day 5 Checklist**
- Understand LiveKit architecture (rooms, participants, tracks)
- Understand difference between Pipecat and LiveKit Agents
- LiveKit Cloud account set up
- LiveKit agent working via browser
- Plivo SIP trunk configured to LiveKit
- Phone calls working via LiveKit SIP
- AI Receptionist working on LiveKit
- Can compare both approaches (Pipecat vs LiveKit)


##
## <a name="_4x64d1dz6u27"></a><a name="_nb0ac09vyuh4"></a>**Day 6**
## <a name="_k5aywad6irt1"></a>**Deployment with Railway — Make It Public**
Goal: Deploy your voice AI agent to Railway so it runs 24/7 without your laptop.


### <a name="_q82jabnwfm6a"></a>**Part 1: Why Railway? (Learn from Claude)**
Ask Claude (browser) to explain:

The Problem: Vercel Won't Work for Voice AI

Vercel Limitations:

- Serverless functions timeout after 10 seconds (hobby) or 60 seconds (pro)
- No persistent WebSocket connections
- Can't handle long-running processes

Voice AI Requirements:

- Phone calls last 2-10 minutes
- Need persistent WebSocket connection for entire call
- Bot must run continuously, waiting for calls

Why Railway Works:

- Runs persistent processes (like a traditional server)
- No timeout limits
- WebSocket connections stay open indefinitely
- Your bot runs 24/7
- Free tier: $5/month credits (enough for learning)

Architecture:

┌─────────────────┐     ┌─────────────────┐

│     VERCEL      │     │     RAILWAY     │

│   (Week 1)      │     │    (Week 2)     │

├─────────────────┤     ├─────────────────┤

│ • Postgres DB   │◄───►│ • Pipecat Bot   │

│ • Redis         │     │ • WebSocket     │

│ • Web frontend  │     │ • Voice AI      │

│ • API endpoints │     │                 │

└─────────────────┘     └─────────────────┘

`        `↑                       ↑

`        `│                       │

`   `Browser/API            Phone calls

`    `requests               via Plivo

Verification: Why can't we deploy Pipecat to Vercel? (Answer: Vercel has timeout limits; voice calls need persistent connections lasting minutes)


### <a name="_kq6tcm248ln4"></a>**Part 2: Railway Basics (Learn from Claude)**
Ask Claude (browser) to explain:

Railway Concepts:

- Project: A collection of services
- Service: A single app/container (your bot)
- Deployment: A version of your service
- Variables: Environment variables

Railway vs Vercel:

Vercel:

- Best for: Frontends, short API calls
- Model: Serverless (spin up/down per request)
- Timeout: 10-60 seconds

Railway:

- Best for: Backends, long-running processes
- Model: Container (runs continuously)
- Timeout: None

Verification: What's the main difference between Vercel and Railway? (Answer: Vercel is serverless with timeouts; Railway runs containers continuously)


### <a name="_ihsil6o4cjjd"></a>**Mini-Projects**


### <a name="_s03d24yo29zq"></a>**Project 1: Set Up Railway Account and CLI**
Your job:

1. Go to railway.app
1. Sign up with GitHub
1. Install Railway CLI:

npm install -g @railway/cli

railway login

4. Verify login:

railway whoami

Verification Checklist:

- Railway account created
- CLI installed
- Logged in via CLI


### <a name="_vdnufdszg6bu"></a>**Project 2: Prepare Pipecat Bot for Railway**
Ask Claude Code to prepare the project:

Requirements:

- Create a Dockerfile for the Pipecat bot
- Ensure all config is via environment variables
- Add a /health endpoint for monitoring
- Create requirements.txt with all dependencies
- Ensure the server binds to 0.0.0.0 and uses PORT env var

Your job:

1. Review the Dockerfile
1. Verify requirements.txt is complete
1. Test locally with Docker (optional):

docker build -t pipecat-bot .

docker run -p 5000:5000 --env-file .env pipecat-bot

Verification Checklist:

- Dockerfile created
- requirements.txt complete
- Health endpoint works
- Bot runs in container (if tested)


### <a name="_s31iu7sfbm3n"></a>**Project 3: Deploy to Railway**
Your job:

1. Initialize Railway project:

cd your-pipecat-project

railway init

2. Link to project:

railway link

3. Set environment variables:

railway variables set OPENAI\_API\_KEY=sk-...

railway variables set DEEPGRAM\_API\_KEY=...

railway variables set ELEVENLABS\_API\_KEY=...

railway variables set PLIVO\_AUTH\_ID=...

railway variables set PLIVO\_AUTH\_TOKEN=...

railway variables set POSTGRES\_URL="postgres://..."

4. Deploy:

railway up

5. Get your public URL:

railway domain

(Or go to Railway dashboard → Settings → Generate Domain)

6. Check logs:

railway logs

Verification Checklist:

- Railway project created
- Environment variables set
- Deploy successful
- Got public URL (e.g., [https://your-app.up.railway.app](https://your-app.up.railway.app/))
- Logs visible

### <a name="_o1gib99qc9ib"></a>**Project 4: Update Plivo to Use Railway**
Your job:

1. Copy your Railway URL
1. Update Plivo phone number:
   1. Go to Plivo console → Phone Numbers → your number
   1. Set Answer URL to: <https://your-app.up.railway.app/answer>
   1. Set Method to: POST
   1. Save
1. Test with a phone call:
   1. Call your Plivo number
   1. Talk to your AI receptionist
   1. Verify it works!
1. Watch logs while calling:

railway logs --tail

Verification Checklist:

- Plivo pointing to Railway URL (not ngrok!)
- Phone call connects
- Voice AI responds
- Logs show call activity


### <a name="_6seurk811hzy"></a>**Project 5: Verify Database Logging**
Your job:

1. Make a few test calls to your Railway-deployed bot
1. Check Vercel dashboard → Storage → Postgres → Data tab
1. Verify calls are logged with:
   1. Caller number
   1. Transcript
   1. Detected intent
   1. Duration

Verification Checklist:

- Calls logged to Vercel Postgres
- Transcript saved correctly
- Intents detected correctly
- Duration recorded


### <a name="_b4212fx8pnkx"></a>**Project 6: Deploy LiveKit Agent to Railway (If Using LiveKit)**
If you built the LiveKit version on Day 5, deploy that too:

Ask Claude Code to prepare the LiveKit agent for Railway:

Requirements:

- Dockerfile for LiveKit agent
- Environment variables for LiveKit credentials
- Health endpoint

Your job:

1. Deploy to Railway (same process as Pipecat)
1. Ensure SIP trunk still works with Railway-hosted agent
1. Test phone calls

Verification Checklist:

- LiveKit agent deployed to Railway
- SIP calls still work
- Agent responds to phone calls


### <a name="_u3gdwcu3v0pf"></a>**End of Day 6 Checklist**
- Understand why Railway is needed (vs Vercel)
- Railway account created
- Railway CLI installed and working
- Pipecat bot deployed to Railway
- Plivo pointing to Railway URL (not ngrok!)
- Phone calls working 24/7
- Call logs saved to Vercel Postgres
- No local processes needed — everything in cloud
- (Optional) LiveKit agent also deployed


## <a name="_8uxau46lyg50"></a>**Day 7**
## <a name="_w3i6d1r6lto"></a>**Polish & Capstone Demo**
Goal: Polish your AI receptionist, add final features, and record a demo video.


### <a name="_pftq7964sk9t"></a>**Final Enhancements**
Ask Claude Code to add these final features:

Requirements:

1. Better interruption handling:
   1. Stop TTS immediately when caller speaks
   1. Don't restart from beginning, continue naturally
1. Conversation memory:
   1. Remember context within the call
   1. "As I mentioned earlier..." type references
1. Graceful ending:
   1. After handling request: "Is there anything else I can help you with?"
   1. When done: "Thank you for calling Acme Corp. Have a great day!"
1. Error handling:
   1. If STT fails: "I'm having trouble hearing you, could you repeat that?"
   1. If LLM fails: "One moment please..." then retry
   1. If TTS fails: Fallback to simpler response
1. Call summary:
   1. At end of call, generate a 1-2 sentence summary
   1. Save summary to database along with transcript

Your job:

1. Implement each enhancement
1. Test thoroughly:
   1. Make 10+ test calls
   1. Test interruptions
   1. Test context memory
   1. Test error scenarios (speak gibberish, make noise)
1. Redeploy to Railway:

railway up

Verification Checklist:

- Interruptions handled smoothly
- Context remembered within call
- Calls end gracefully
- Errors handled without crashing
- Summaries saved to database


### <a name="_p0u5o92vk0cu"></a>**Capstone: Record Demo Video**
Your job:

1. Record a screen capture with audio showing:
   1. You dialing your Plivo number
   1. Phone ringing and AI answering
   1. You asking about sales → AI responds appropriately
   1. You asking about hours → AI gives FAQ answer
   1. You asking a random question → AI handles it
   1. Natural ending of the call
   1. Full conversation (2-3 minutes)
1. Show the data:
   1. After the call, open Vercel dashboard
   1. Show the database entry
   1. Show the transcript
   1. Show the detected intent
   1. Show the call summary
1. Recording tools:
   1. QuickTime (Mac): File → New Screen Recording
   1. OBS (free): For more control
   1. Loom: Easy sharing

Demo Script Example:

[Show phone dialing Plivo number]

AI: "Hello, thank you for calling Acme Corp. How can I help you today?"

You: "Hi, I'm interested in learning about your products."

AI: "I'd be happy to connect you to our sales team. Before I do, may I ask what product you're interested in?"

You: "Actually, first can you tell me what your hours are?"

AI: "Of course! We're open Monday to Friday, 9 AM to 5 PM Pacific time. Would you still like to speak with sales?"

You: "No, that's all I needed. Thanks!"

AI: "You're welcome! Is there anything else I can help you with?"

You: "Nope, bye!"

AI: "Thank you for calling Acme Corp. Have a great day!"

[Show Vercel dashboard with call log]

[Show transcript]

[Show detected intent: sales → faq → end]

[Show summary: "Caller inquired about sales, then asked about business hours. No transfer needed."]

Verification Checklist:

- Video recorded
- Shows complete conversation
- Shows database logs in Vercel
- Audio quality is clear
- Demo is under 5 minutes


### <a name="_wjhonbu3wv4x"></a>**Share with Someone**
Your job:

1. Send your Plivo phone number to a friend or colleague
1. Ask them to call and talk to your AI receptionist
1. Don't tell them what to say — let them interact naturally
1. Check logs to see their call
1. Get feedback:
   1. Did it feel natural?
   1. Was latency acceptable?
   1. Did it understand them?
   1. Any issues?

Verification Checklist:

- Someone else successfully called
- Bot worked for external caller
- Call logged correctly
- Got feedback
- Noted any issues to fix


### <a name="_gjrp5vvdfbsg"></a>**Week 2 Complete!**
By the end of Week 2, you can:

- Call OpenAI APIs with streaming
- Transcribe audio in real-time with Deepgram
- Generate speech with ElevenLabs (streaming)
- Build voice AI pipelines with Pipecat (SileroVAD, SmartTurn)
- Connect phone calls via Plivo WebSocket audio streaming
- (Alternative) Use LiveKit with Plivo SIP trunking
- Deploy voice AI to Railway for 24/7 availability
- Understand when to use Vercel vs Railway
- Build a complete AI receptionist that handles intents and FAQs
- Log calls with transcripts to a database


### <a name="_fpvp93g07dqp"></a>**Architecture Summary**
Option A: Pipecat + Plivo WebSocket

Phone Call

`    `↓

Plivo

`    `↓ (WebSocket audio streaming)

Railway (Pipecat Bot)

`    `├── SileroVAD

`    `├── SmartTurn  

`    `├── Deepgram STT

`    `├── OpenAI GPT-4.1-mini

`    `└── ElevenLabs TTS

`    `↓

Vercel Postgres (call logs)

Option B: LiveKit + Plivo SIP

Phone Call

`    `↓

Plivo

`    `↓ (SIP Trunk)

LiveKit Cloud

`    `↓ (Room participant)

Railway (LiveKit Agent)

`    `├── VAD

`    `├── Deepgram STT

`    `├── OpenAI GPT-4.1-mini

`    `└── ElevenLabs TTS

`    `↓

Vercel Postgres (call logs)



### <a name="_hotyfmvn5ycd"></a>**End of Week 2 Checklist**
- OpenAI API working with streaming
- Function calling working
- Deepgram STT working (real-time)
- ElevenLabs TTS working (streaming)
- Pipecat with SileroVAD and SmartTurn working
- Pipecat + Plivo WebSocket working
- (Optional) LiveKit + Plivo SIP working
- AI Receptionist with intent detection working
- Deployed to Railway (24/7)
- Call logs saved to Vercel Postgres
- External person tested the system
- Demo video recorded



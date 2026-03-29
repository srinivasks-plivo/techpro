# Tech Ramp-Up Program

A 2-week hands-on program building production voice AI systems — from raw API calls to a deployed AI receptionist handling real phone calls 24/7.

## Architecture

```
Phone Call
    |
    v
  Plivo (Telephony)
    |
    |--- Option A: WebSocket Audio Streaming (Week 2, Day 4)
    |       |
    |       v
    |     Railway (Pipecat Bot)
    |       |-- Silero VAD (Voice Activity Detection)
    |       |-- Deepgram STT (Speech-to-Text)
    |       |-- OpenAI GPT-4.1-mini (LLM)
    |       |-- ElevenLabs TTS (Text-to-Speech)
    |       |-- Function Calling (hours, location, transfers)
    |
    |--- Option B: SIP Trunking (Week 2, Day 5)
            |
            v
          LiveKit Cloud (Media Routing)
            |
            v
          LiveKit Agent
            |-- Silero VAD
            |-- Deepgram STT
            |-- OpenAI GPT-4.1-mini
            |-- ElevenLabs TTS
            |-- Function Calling
    |
    v
  Neon Postgres (Call Logs, Transcripts, Intents)
```

## Repository Structure

```
TECHPRO/
├── Day3/                        # Week 1 — IVR System on Vercel
│   ├── app.py                   # Flask IVR application
│   ├── services/                # Plivo, Redis, Postgres integrations
│   ├── models/                  # Database models
│   └── scripts/                 # Setup and utility scripts
│
├── ivr-vercel/                  # Week 1 — Vercel-deployed IVR API
│   ├── api/                     # Serverless API endpoints
│   ├── services/                # Business logic
│   └── vercel.json              # Vercel deployment config
│
├── week2/                       # Week 2 — Voice AI
│   ├── Day1/                    # OpenAI API: streaming, chatbot, function calling
│   ├── Day2/                    # Deepgram STT + ElevenLabs TTS pipeline
│   ├── Day3/                    # Pipecat: local voice bot with VAD + SmartTurn
│   ├── Day4/                    # Pipecat + Plivo: phone-connected AI receptionist
│   ├── Day5/                    # LiveKit + SIP: agent with Plivo SIP trunking
│   └── Day6/                    # Railway deployment: 24/7 cloud-hosted receptionist
│
└── Tech Ramp-Up Plan.md         # Full program curriculum
```

## Week 1 — IVR System

Built a traditional IVR (Interactive Voice Response) system deployed on Vercel:
- Plivo voice call handling with DTMF input
- Call routing and menu navigation
- Redis for session management
- Vercel Postgres for call logging
- Deployed as serverless functions on Vercel

## Week 2 — Voice AI

### Day 1 — OpenAI API Fundamentals
- Streaming completions
- Multi-turn chatbot
- Function calling with tool definitions

### Day 2 — Speech Services
- Deepgram real-time speech-to-text
- ElevenLabs streaming text-to-speech
- Full STT → LLM → TTS pipeline

### Day 3 — Pipecat Voice Bot
- Local voice bot using Pipecat framework
- Silero VAD for voice activity detection
- SmartTurn for natural turn-taking
- Latency tracking and optimization
- Function calling within voice pipeline

### Day 4 — Plivo Phone Integration
Progression from basic WebSocket to full AI receptionist:
1. **Project 1** — Basic Plivo WebSocket server (logs audio packets)
2. **Project 2** — Pipecat pipeline connected to Plivo (STT → LLM → TTS)
3. **Project 3** — AI receptionist with intent detection + DB logging
4. **Project 4** — Improved receptionist with interruption handling, context memory, warm-start

### Day 5 — LiveKit + SIP Trunking
Alternative architecture using LiveKit for media routing:
1. **Project 1-2** — LiveKit token setup + basic voice agent
3. **Project 3** — SIP trunk + dispatch rule configuration
4. **Project 4** — Phone agent with call logging and latency metrics
5. **Project 5** — Full receptionist with function calling and intent detection

### Day 6 — Railway Deployment
Deployed the Pipecat AI receptionist to Railway for 24/7 availability:
- Dockerized Pipecat application (no PyTorch — uses onnxruntime)
- Health endpoint for monitoring
- Plivo Answer URL pointing to Railway (no ngrok needed)
- Call logging with transcripts to Neon Postgres
- Caller number, intent detection, and call duration tracking

**Live endpoint:** Deployed on Railway, accessible via Plivo phone number

## Tech Stack

| Component | Technology |
|---|---|
| Telephony | Plivo (Voice API, SIP Trunking) |
| Voice Framework | Pipecat, LiveKit Agents |
| Speech-to-Text | Deepgram |
| LLM | OpenAI GPT-4.1-mini |
| Text-to-Speech | ElevenLabs |
| VAD | Silero (onnxruntime) |
| Deployment | Railway (Week 2), Vercel (Week 1) |
| Database | Neon Postgres, Vercel Postgres, SQLite |
| IVR | Plivo XML, Redis |

## Key Optimizations

- **Warm-start**: Silero VAD model pre-loaded at server startup
- **TTSSpeakFrame**: Greeting sent directly to TTS, skipping LLM round trip
- **Top-level imports**: All Pipecat modules loaded once at startup, not per call
- **Per-call service instances**: Fresh STT/LLM/TTS connections per call to avoid stale WebSockets

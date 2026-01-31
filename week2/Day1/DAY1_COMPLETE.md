# Day 1: LLM APIs - COMPLETE! ✅

## What You Built Today

### Project 1: First OpenAI API Call
- **File**: `project1_first_call.py`
- **Learned**: Tokens, temperature, basic API structure
- **Result**: Successfully made API calls with different temperatures
- **Response Time**: 1.7 - 4 seconds

### Project 2: Streaming Responses
- **File**: `project2_streaming.py`
- **Learned**: TTFT (Time To First Token), streaming vs non-streaming
- **Result**: Reduced perceived latency from 4.89s → 0.82s TTFT
- **Key Insight**: Streaming is ESSENTIAL for voice AI

### Project 3: CLI Chatbot
- **File**: `project3_chatbot.py`
- **Learned**: Conversation history, context windows, token counting
- **Result**: Built a chatbot that remembers previous messages
- **Key Insight**: Every message includes full conversation history

### Project 4: Function Calling
- **File**: `project4_function_calling.py`
- **Learned**: Tools/functions, AI decision-making, real-world actions
- **Result**: AI that intelligently calls functions when needed
- **Key Insight**: This is how voice AI agents actually DO things

---

## Key Concepts Mastered

### Tokens
- LLMs see "tokens" not words
- 1 token ≈ 4 characters or ¾ of a word
- You pay per token, context has limits

### Context Window
- The "memory" of a conversation
- GPT-4: 128k tokens
- Everything (system prompt + history + message) must fit
- When full: oldest messages get dropped or error

### Temperature (0.0 - 2.0)
- **0.0**: Deterministic, same input → same output
- **1.0**: Creative, varied responses
- **For voice AI**: Usually 0.7-0.8

### Streaming
- **Normal**: Wait for full response
- **Streaming**: Get tokens as generated
- **TTFT**: Time to first token - when voice AI can start speaking
- **Voice AI**: Streaming is MANDATORY for low latency

### System Prompts
- Instructions that define AI personality
- Set once at conversation start
- Persists throughout conversation

### Message Roles
- **system**: AI instructions (set once)
- **user**: Human messages
- **assistant**: AI responses (include previous ones for context)
- **tool**: Function call results

### Function Calling (Tools)
- AI can call functions based on user queries
- Define function schemas → AI decides when to use
- Foundation for agents that take actions

---

## Performance Metrics

| Metric | Value | Why It Matters |
|--------|-------|----------------|
| **Non-streaming response** | 4.89s | Total wait time before seeing anything |
| **Streaming TTFT** | 0.82s | When voice AI can start speaking |
| **Latency improvement** | 1.27s - 2.2s | Massive UX improvement for voice |
| **Token growth** | 33 → 108 | How context expands with conversation |

---

## End of Day 1 Checklist

| Item | Status |
|------|--------|
| Can explain tokens, context window, temperature | ✅ |
| Can explain streaming and why it matters | ✅ |
| OpenAI API calls working | ✅ |
| Streaming responses working | ✅ |
| CLI chatbot with history working | ✅ |
| Function calling working | ✅ |
| Understand time-to-first-token concept | ✅ |

---

## Files Created

```
day1/
├── .env                          # API keys (keep secret!)
├── requirements.txt              # Python dependencies
├── project1_first_call.py       # Basic API calls
├── project2_streaming.py        # Streaming demo
├── project3_chatbot.py          # Interactive chatbot
├── project4_function_calling.py # Tools/functions
├── venv/                        # Virtual environment
└── DAY1_COMPLETE.md            # This file
```

---

## How to Run the Projects

### Setup (one time)
```bash
cd /Users/intern-srinivas/Desktop/TECHPRO/week2/day1
source venv/bin/activate
```

### Run Any Project
```bash
python project1_first_call.py       # Basic API call
python project2_streaming.py        # Streaming demo
python project3_chatbot.py          # Interactive chatbot
python project4_function_calling.py # Function calling
```

---

## What's Next: Day 2

Tomorrow you'll learn:
- **Speech-to-Text** (STT) with Deepgram
- **Text-to-Speech** (TTS) with ElevenLabs
- **Audio formats** (WAV, PCM, sample rates)
- Build the full pipeline: Speech → Text → LLM → Speech

You'll need:
- Deepgram API key
- ElevenLabs API key

---

## Key Takeaway

Today you learned the **BRAIN** of voice AI - how LLMs work via APIs.

Tomorrow you'll add **EARS** (STT) and a **VOICE** (TTS).

By Day 4, you'll have a working AI receptionist that answers phone calls!

---

**Great work today! 🚀**

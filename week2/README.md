# Week 2: AI Agents

Building production-ready voice AI agents using LLMs, Speech AI, and real-time communication frameworks.

## 🎯 Goal

Understand LLM APIs, Speech AI (STT/TTS), and build production-ready voice AI agents using Pipecat and LiveKit, deployed publicly.

## 📁 Project Structure

```
week2/
├── .env.example          # Template for environment variables
├── .gitignore           # Files to exclude from git
├── README.md            # This file
├── plan.txt             # Full week plan
│
├── day1/                # LLM APIs
│   ├── .env            # Your API keys (git ignored)
│   ├── venv/           # Virtual environment (git ignored)
│   ├── requirements.txt
│   ├── project1_first_call.py
│   ├── project2_streaming.py
│   ├── project3_chatbot.py
│   ├── project4_function_calling.py
│   └── DAY1_COMPLETE.md
│
├── day2/                # Speech AI (STT & TTS) - Coming soon
├── day3/                # Pipecat Framework - Coming soon
├── day4/                # Plivo Integration - Coming soon
├── day5/                # LiveKit Alternative - Coming soon
├── day6/                # Railway Deployment - Coming soon
└── day7/                # Polish & Demo - Coming soon
```

## 🚀 Quick Start

### 1. Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your actual API keys
# NEVER commit the .env file!
```

### 2. Day-Specific Setup

Each day has its own directory with a virtual environment:

```bash
cd day1
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Projects

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run any project
python project1_first_call.py
```

## 🔑 Required API Keys

| Service | Day | Purpose | Get Key From |
|---------|-----|---------|--------------|
| OpenAI | 1 | LLM (GPT-4o) | https://platform.openai.com/api-keys |
| Deepgram | 2 | Speech-to-Text | https://console.deepgram.com/ |
| ElevenLabs | 2 | Text-to-Speech | https://elevenlabs.io/app/settings/api-keys |
| Plivo | 4 | Phone Calls | https://console.plivo.com/dashboard/ |
| LiveKit | 5 | WebRTC/Media | https://cloud.livekit.io/ |
| Railway | 6 | Deployment | https://railway.app/ |
| Vercel Postgres | 6 | Database | https://vercel.com/dashboard |

## 📚 What You'll Learn

### Day 1: LLM APIs ✅
- Tokens, context windows, temperature
- Streaming responses (TTFT)
- Conversation memory
- Function calling (tools)

### Day 2: Speech AI
- Audio formats (WAV, PCM, sample rates)
- Speech-to-Text with Deepgram
- Text-to-Speech with ElevenLabs
- Full pipeline: Speech → Text → LLM → Speech

### Day 3: Pipecat Framework
- Real-time voice AI architecture
- VAD (Voice Activity Detection)
- SmartTurn (turn detection)
- Interruption handling
- Latency optimization

### Day 4: Phone Integration
- Plivo WebSocket audio streaming
- AI Receptionist
- Intent detection
- Call logging to database

### Day 5: LiveKit Alternative
- WebRTC fundamentals
- SIP trunking
- LiveKit Agents framework
- Comparing approaches

### Day 6: Deployment
- Railway vs Vercel (when to use each)
- Containerization with Docker
- Environment variables in production
- 24/7 availability

### Day 7: Polish & Demo
- Final enhancements
- Error handling
- Demo video creation
- Production readiness

## ⚠️ Important Security Notes

### NEVER Commit These Files:
- `.env` - Contains your API keys
- `venv/` - Virtual environment (large)
- `*.wav`, `*.mp3` - Audio files (large)
- Any file with "secret" or "private" in the name

### If You Accidentally Expose Keys:
1. Immediately rotate/delete the exposed keys
2. Go to the service provider and regenerate new keys
3. Update your `.env` file
4. Check git history: `git log --all --full-history -- .env`

## 🛠️ Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Install new packages
pip install package-name
pip freeze > requirements.txt

# Check what's ignored by git
git status --ignored

# See git ignore rules
git check-ignore -v filename
```

## 📈 Progress Tracking

- [x] Day 1: LLM APIs
- [ ] Day 2: Speech AI
- [ ] Day 3: Pipecat
- [ ] Day 4: Plivo
- [ ] Day 5: LiveKit
- [ ] Day 6: Railway
- [ ] Day 7: Demo

## 🆘 Troubleshooting

### "Import Error: No module named 'openai'"
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### "401 Unauthorized" API Error
- Check your API key in `.env`
- Make sure there are no extra spaces
- Verify the key is active in the service dashboard

### "Rate Limit Exceeded"
- You've hit the API rate limit
- Wait a few minutes and try again
- Check your API usage/quota

### Git Pushed .env File Accidentally
1. Remove from git: `git rm --cached .env`
2. Commit: `git commit -m "Remove .env"`
3. Push: `git push`
4. **ROTATE ALL YOUR API KEYS IMMEDIATELY**

## 🎓 Resources

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Deepgram Docs](https://developers.deepgram.com/)
- [ElevenLabs API](https://elevenlabs.io/docs)
- [Pipecat GitHub](https://github.com/pipecat-ai/pipecat)
- [LiveKit Docs](https://docs.livekit.io/)
- [Plivo WebSocket Streaming](https://www.plivo.com/docs/voice/api/stream/)

## 📝 Notes

- All free tiers should be sufficient for learning
- Costs during the week should be < $5 total
- Test locally before deploying to production
- Keep latency under 2 seconds for good UX

---

**Happy Building! 🚀**

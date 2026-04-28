#!/bin/bash

# Self-permission fix
chmod +x "$0"

# Go to project directory
cd ~/Desktop/cyber-shark || { echo "❌ Project folder not found at ~/Desktop/cyber-shark"; exit 1; }

# Check venv exists
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Virtual environment not found. Run setup first:"
    echo "   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check API key
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. AI features will be disabled."
    echo "   Create .env with: OPENROUTER_API_KEY=your-key-here"
fi

# Suppress noise
export ALSA_CARD=0
export PYGAME_HIDE_SUPPORT_PROMPT=1
export PYTHONWARNINGS=ignore
export SDL_AUDIODRIVER=alsa

echo "🦈 Starting Cyber Shark..."

# Run
python3 cyber_shark_kali.py 2>/dev/null

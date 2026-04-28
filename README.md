# 🦈 CYBER SHARK - Kali Linux Edition

AI-Powered Cybersecurity Assistant with Voice Control  
**B.Tech IT Final Year Project — GNDEC Ludhiana**

---

## Features

- 13 integrated security tools across 6 categories
- Llama 3.3 70B via OpenRouter for intelligent command parsing & analysis
- Red team AI persona for penetration testing analysis
- Voice command input (Google Speech Recognition)
- Text-to-speech output (gTTS + pygame)
- Intent classification — distinguishes questions from scan commands
- Target validation before execution
- TF-IDF + fuzzy matching FAQ system
- Automated security reports saved to `~/cyber-shark-reports/`

---

## Security Tools

| Category | Tools |
|----------|-------|
| Network Scanning | nmap |
| Network Analysis | netstat |
| Network Testing | ping |
| Web Scanning | nikto, sqlmap, dirb |
| OSINT | whois, dig, nslookup, theHarvester |
| Password Cracking | john, hydra |
| Web Testing | curl |

---

## Requirements

- Kali Linux (recommended)
- Python 3.10–3.12 (avoid 3.13 — numpy incompatibility)
- Microphone (for voice input)
- Internet connection (for gTTS + OpenRouter AI)
- OpenRouter API key — get one free at https://openrouter.ai

---

## Setup

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y portaudio19-dev python3-dev python3-pip \
    python3-venv python3-pyaudio espeak nmap nikto sqlmap \
    dirb whois dnsutils theharvester john hydra curl

# 2. Extract rockyou wordlist (needed for hydra/john)
sudo gunzip /usr/share/wordlists/rockyou.txt.gz

# 3. Clone / go to project directory
cd ~/Desktop/cyber-shark

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install -r requirements.txt

# 6. Copy system PyAudio into venv (avoids build issues)
cp -r /usr/lib/python3/dist-packages/pyaudio* venv/lib/python3.*/site-packages/

# 7. Download NLTK data
python3 -c "import nltk; nltk.download('punkt')"

# 8. Configure API key
cp .env.example .env
nano .env
# Add: OPENROUTER_API_KEY=your-key-here

# 9. Make run script executable (only needed once)
chmod +x run.sh

# 10. Run Cyber Shark
./run.sh
```

---

## .env File

Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

> The app uses **OpenRouter** (not Anthropic directly) to access  
> `meta-llama/llama-3.3-70b-instruct` for command parsing and scan analysis.

---

## Example Commands

**Security Scans**
```
scan 192.168.1.1
nmap google.com
whois gndec.ac.in
dirb gndec.ac.in
check localhost for vulnerabilities
dig google.com
show network connections
ping google.com
```

**Informational Queries** (routes to AI, no tool executed)
```
what is nmap
how does sqlmap work
explain hydra
what is a port scan
```

**System Commands**
```
open browser
open terminal
open youtube
search kali linux tools
close firefox
```

**Exit**
```
exit / quit / bye / goodbye / shutdown
```

---

## How It Works

```
User Input (voice or keyboard)
        │
        ▼
handle_command()
        │
        ├── System command? → open/close apps, search web
        │
        ├── Security keyword detected?
        │       │
        │       ├── classify_intent() → "info"   → get_answer() → FAQ / AI Q&A
        │       └── classify_intent() → "action" → execute_security_task()
        │                                               │
        │                                         is_valid_target()?
        │                                               │
        │                                         run_security_tool()
        │                                               │
        │                                         analyze_results_with_claude()
        │                                               │
        │                                         save_report()
        │
        └── No keyword → get_answer() → TF-IDF + Fuzzy FAQ match → AI fallback
```

---

## Project Structure

```
cyber-shark/
├── cyber_shark_kali.py     # Main application
├── run.sh                  # Launch script
├── requirements.txt        # Python dependencies
├── faqs.json               # FAQ database (auto-created)
├── .env                    # API key (not committed to git)
├── README.md
└── ~/cyber-shark-reports/  # Auto-generated scan reports
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `numpy` import error on Python 3.13 | Use Python 3.11/3.12 or `pip install --upgrade numpy` |
| Voice input not working | Check microphone `device_index` in `listen()` |
| gTTS audio delayed | Audio runs in background thread — expected |
| `rockyou.txt` not found | Run `sudo gunzip /usr/share/wordlists/rockyou.txt.gz` |
| AI not responding | Check `OPENROUTER_API_KEY` in `.env` |
| `run.sh` loses permissions | Run `chmod +x run.sh` once, or use `bash run.sh` |

---

## Author

**Sumit Kumar**  
B.Tech IT — Final Year Project  
GNDEC Ludhiana  
[LinkedIn](https://www.linkedin.com/in/roysaab0786) | Instagram: @roysaab0786

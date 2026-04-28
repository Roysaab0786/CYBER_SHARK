#!/usr/bin/env python3
"""
CYBER SHARK - Kali Linux Enhanced Version
AI-Powered Security Assistant with Voice Control
"""

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from pathlib import Path
import datetime
import subprocess
import threading
import time
import json
import os
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Voice and NLP
try:
    import speech_recognition as sr
    VOICE_INPUT = True
except ImportError:
    VOICE_INPUT = False
    print("⚠️ SpeechRecognition not available - voice input disabled")


# AI Integration
try:
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    CLAUDE_AVAILABLE = True  # reusing flag name to avoid changing logic
except ImportError:
    CLAUDE_AVAILABLE = False
    print("⚠️ OpenAI library not installed - AI features disabled")

# gTTS + Pygame Voice
try:
    from gtts import gTTS
    import pygame
    VOICE_OUTPUT = True
except ImportError:
    VOICE_OUTPUT = False
    print("⚠️ gTTS or pygame not available - voice output disabled")

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class CyberSharkKali:
    """
    Enhanced Cyber Shark for Kali Linux with 15+ security tools
    """

    def __init__(self):
        print("🦈 Initializing Cyber Shark Kali Edition...")

        # Configuration
        self.assistant_name = "Cyber Shark - Kali Edition"
        self.reports_dir = Path.home() / "cyber-shark-reports"
        self.reports_dir.mkdir(exist_ok=True)

        # AI Setup
        self.claude_client = None
        if CLAUDE_AVAILABLE:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key:
                try:
                    self.claude_client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key,
                    )
                    print("✓ Llama 3.3 via OpenRouter connected")
                except Exception as e:
                    print(f"⚠ OpenRouter AI unavailable: {e}")

        # FAQ System
        self.faqs = {}
        self.load_faqs()

        self.vectorizer = TfidfVectorizer()
        self.questions = list(self.faqs.keys())
        if self.questions:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.questions)
        else:
            self.tfidf_matrix = None

        # Audio Engine (gTTS + pygame)
        if VOICE_OUTPUT:
            try:
                pygame.mixer.pre_init(
                    frequency=22050, size=-16, channels=1, buffer=2048)
                pygame.mixer.init()
                print("✓ Voice engine ready (gTTS)")
            except Exception as e:
                print(f"⚠ Audio engine failed: {e}")

        # Security Tools
        self.security_tools = {
            "nmap": {"cmd": "nmap", "category": "Network Scanning"},
            "netstat": {"cmd": "netstat -tulnp", "category": "Network Analysis"},
            "ping": {"cmd": "ping -c 4", "category": "Network Testing"},
            "nikto": {"cmd": "nikto -h", "category": "Web Scanning"},
            "sqlmap": {"cmd": "sqlmap -u", "category": "Web Scanning"},
            "dirb": {"cmd": "dirb", "category": "Web Scanning"},
            "whois": {"cmd": "whois", "category": "OSINT"},
            "dig": {"cmd": "dig", "category": "OSINT"},
            "nslookup": {"cmd": "nslookup", "category": "OSINT"},
            "theHarvester": {"cmd": "theHarvester -d", "category": "OSINT"},
            "john": {"cmd": "john", "category": "Password Cracking"},
            "hydra": {"cmd": "hydra", "category": "Password Cracking"},
            "curl": {"cmd": "curl -I", "category": "Web Testing"},
        }

        self.check_available_tools()
        print(f"✓ Cyber Shark ready with {len(self.available_tools)} tools!")

    def check_available_tools(self):
        """Check which security tools are installed"""
        self.available_tools = []
        print("\n🔍 Checking available security tools...")

        for tool_name, tool_info in self.security_tools.items():
            cmd = tool_info["cmd"].split()[0]
            try:
                result = subprocess.run(
                    f"which {cmd}",
                    shell=True,
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    self.available_tools.append(tool_name)
                    print(f"  ✓ {tool_name}")
                else:
                    print(f"  ✗ {tool_name} not found")
            except BaseException:
                print(f"  ✗ {tool_name} check failed")

        print(f"\n✓ {len(self.available_tools)} tools available\n")

    def speak(self, text):
        """Text-to-speech output using gTTS"""
        print(f"🦈 {text}")

        if not VOICE_OUTPUT:
            return

        try:
            import tempfile

            tts = gTTS(text=text, lang='en', slow=False, tld='co.uk')

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                temp_path = f.name
                tts.save(temp_path)

            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            os.remove(temp_path)

        except Exception as e:
            print(f"⚠ Voice error: {e}")

    def listen(self):
        """Voice input recognition"""
        if not VOICE_INPUT:
            return ""

        recognizer = sr.Recognizer()

        with sr.Microphone(device_index=1) as source:
            print("\n🎤 Listening...")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(
                    source, timeout=5, phrase_time_limit=10)
                query = recognizer.recognize_google(audio).lower()
                print(f"👤 You: {query}")
                return query
            except sr.WaitTimeoutError:
                print("⚠ No speech detected, switching to keyboard...")
                return ""
            except sr.UnknownValueError:
                print("⚠ Couldn't understand speech, try again...")
                return ""
            except sr.RequestError as e:
                print(f"⚠ Google Speech API error: {e}")
                return ""
            except Exception as e:
                print(f"⚠ Listen error: {e}")
                return ""

    def run_security_tool(self, tool, target="", options=""):
        """Execute security tool and capture output"""
        if tool not in self.available_tools:
            return f"Tool '{tool}' not available on this system"

        tool_info = self.security_tools[tool]

        if tool == "sqlmap":
            command = f"{tool_info['cmd']} {target} --batch --level=1 --risk=1"
        elif tool == "nmap":
            command = f"nmap -sV --open {options} {target}"
        elif tool == "theHarvester":
            command = f"{tool_info['cmd']} {target} -b google -l 100"
        elif tool == "hydra":
            command = (
                f"hydra -L /usr/share/wordlists/metasploit/unix_users.txt "
                f"-P /usr/share/wordlists/rockyou.txt "
                f"{target} ssh"  # or http, ftp etc
            )
        elif tool == "john":
            command = (
                f"john {target} "
                f"--wordlist=/usr/share/wordlists/rockyou.txt "
                f"--format=auto"
            )
        elif tool == "dirb":
            if not target.startswith("http://") and not target.startswith("https://"):
                target = f"http://{target}"
                command = f"{tool_info['cmd']} {target}"
        else:
            command = f"{tool_info['cmd']} {options} {target}".strip()


        print(f"\n🔧 Executing: {command}")
        self.speak(f"Running {tool} scan...")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=180
            )

            output = result.stdout if result.stdout else result.stderr
            return output if output else "Command completed with no output"

        except subprocess.TimeoutExpired:
            return "⚠️ Command timed out after 3 minutes"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def analyze_with_claude(self, user_command):
        """Use Claude to parse security command"""
        if not self.claude_client:
            command_lower = user_command.lower()

            if "sql" in command_lower or "injection" in command_lower:
                return {
                    "tool": "sqlmap",
                    "target": self.extract_target(user_command)}
            elif "port" in command_lower or "nmap" in command_lower or "scan" in command_lower:
                return {
                    "tool": "nmap",
                    "target": self.extract_target(user_command)}
            elif "web" in command_lower or "nikto" in command_lower or "vulnerab" in command_lower:
                return {
                    "tool": "nikto",
                    "target": self.extract_target(user_command)}
            elif "whois" in command_lower:
                return {
                    "tool": "whois",
                    "target": self.extract_target(user_command)}
            elif "directory" in command_lower or "dirb" in command_lower:
                return {
                    "tool": "dirb",
                    "target": self.extract_target(user_command)}
            elif "dns" in command_lower or "dig" in command_lower:
                return {
                    "tool": "dig",
                    "target": self.extract_target(user_command)}
            elif "connection" in command_lower or "netstat" in command_lower:
                return {"tool": "netstat", "target": ""}

            return None

        try:
            tool_list = ", ".join(self.available_tools)
            response = self.claude_client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                max_tokens=512,
                messages=[
    {
        "role": "system",
        "content": "You are a red team cybersecurity professional with expertise in penetration testing and offensive security. Parse commands precisely and identify the correct security tool and target."
    },
    {
        "role": "user",
        "content": f"""Parse: "{user_command}"

Available tools: {tool_list}

Respond JSON only:
{{"tool": "tool_name", "target": "target_here"}}"""
                }]
            )

            result_text = response.choices[0].message.content.strip()
            if "{" in result_text:
                json_str = result_text[result_text.find(
                    "{"):result_text.rfind("}") + 1]
                return json.loads(json_str)

            return None

        except Exception as e:
            print(f"Claude error: {e}")
            print("⚠ Falling back to keyword matching...")
            command_lower = user_command.lower()

            if "sql" in command_lower or "injection" in command_lower:
                return {
                    "tool": "sqlmap",
                    "target": self.extract_target(user_command)}
            elif "port" in command_lower or "nmap" in command_lower or "scan" in command_lower:
                return {
                    "tool": "nmap",
                    "target": self.extract_target(user_command)}
            elif "web" in command_lower or "nikto" in command_lower or "vulnerab" in command_lower:
                return {
                    "tool": "nikto",
                    "target": self.extract_target(user_command)}
            elif "whois" in command_lower:
                return {
                    "tool": "whois",
                    "target": self.extract_target(user_command)}
            elif "directory" in command_lower or "dirb" in command_lower:
                return {
                    "tool": "dirb",
                    "target": self.extract_target(user_command)}
            elif "dns" in command_lower or "dig" in command_lower:
                return {
                    "tool": "dig",
                    "target": self.extract_target(user_command)}
            elif "connection" in command_lower or "netstat" in command_lower:
                return {"tool": "netstat", "target": ""}
            return None

    def extract_target(self, command):
        """Extract target from command"""
        words = command.split()
        for word in words:
            if "." in word and " " not in word:
                return word.replace(",", "").replace(":", "")
        return "localhost"

    def analyze_results_with_claude(self, tool, target, raw_output):
        """AI analysis of results"""
        if not self.claude_client:
            return "AI analysis not available. Check raw output above."

        try:
            output_preview = raw_output[:10000] if len(
                raw_output) > 10000 else raw_output

            response = self.claude_client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                max_tokens=1024,
                messages=[
    {
        "role": "system",
        "content": "You are a red team cybersecurity professional with expertise in penetration testing, vulnerability assessment, and offensive security operations. Analyze scan results with a red team mindset — identify attack vectors, exploitable vulnerabilities, and provide actionable recommendations."
    },
    {
        "role": "user",
        "content": f"""Analyze {tool} scan of {target}:

{output_preview}

Provide:
1. Summary (2-3 sentences)
2. Key Findings
3. Vulnerabilities
4. Recommendations"""
                }]
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"⚠ Analysis failed: {e}")
            return None

    def classify_intent(self, command):
        """
        Returns 'info' if user is asking a question,
        'action' if user wants a tool executed.
        """
        info_phrases = [
            "what is", "what are", "what does", "how does", "how do",
            "explain", "tell me", "describe", "define", "meaning of",
            "what's", "whats", "how to", "why is", "can you explain"
        ]
        command_lower = command.lower().strip()
        for phrase in info_phrases:
            if command_lower.startswith(phrase) or f" {phrase} " in command_lower:
                return "info"
        return "action"

    def is_valid_target(self, target, tool):
        """
        Returns True only if target looks like a real IP or domain.
        Tools like netstat don't need a target, so they're excluded.
        """
        import re
        no_target_tools = ["netstat"]
        if tool in no_target_tools:
            return True

        if not target or target.strip() in ["", "target_here", "localhost"]:
            # localhost is technically valid, keep it
            if target.strip() == "localhost":
                return True
            return False

        # Match IPv4
        ip_pattern = r'^\d{1,3}(\.\d{1,3}){3}$'
        # Match domain like google.com, sub.domain.org
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'

        if re.match(ip_pattern, target) or re.match(domain_pattern, target):
            return True

        return False

    def execute_security_task(self, user_command):
        """Main security handler"""
        self.speak("Analyzing request...")

        intent_data = self.analyze_with_claude(user_command)

        if not intent_data or not intent_data.get("tool"):
            self.speak("Couldn't understand that command.")
            print("\n💡 Try:")
            print("  - scan localhost")
            print("  - whois google.com")
            print("  - show network connections")
            return

        tool = intent_data.get("tool")
        target = intent_data.get("target", "")

        if tool not in self.available_tools:
            self.speak(f"{tool} not available.")
            return

        # Validate target before executing
        if not self.is_valid_target(target, tool):
            self.speak(
                f"No valid target found for {tool}. "
                "Please specify an IP address or domain name."
            )
            print(f"\n💡 Example: scan 192.168.1.1  or  scan example.com\n")
            return

        raw_output = self.run_security_tool(tool, target)

        print(f"\n{'=' * 70}")
        print(f"{tool.upper()} RESULTS:")
        print(f"{'=' * 70}")
        print(raw_output)

        self.speak("Analyzing results...")
        analysis = self.analyze_results_with_claude(tool, target, raw_output)

        print(f"\n{'='*70}")
        print("AI SECURITY ANALYSIS:")
        print(f"{'='*70}")

        if analysis:
            print(analysis)
            print(f"{'='*70}\n")
            summary = ". ".join(analysis.split(".")[:2]) + "."
            self.speak(summary)
        else:
            print("AI analysis unavailable.")
            print(f"{'='*70}\n")
            self.speak("Scan complete. AI analysis unavailable.")

        report_path = self.save_report(
            user_command, tool, target, raw_output, analysis)
        self.speak(f"Report saved to {report_path.name}")

    def save_report(self, command, tool, target, output, analysis):
        """Save security report"""
        timestamp = datetime.datetime.now()
        filename = f"report_{tool}_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self.reports_dir / filename

        with open(filepath, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("CYBER SHARK SECURITY REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Command: {command}\n")
            f.write(f"Tool: {tool}\n")
            f.write(f"Target: {target}\n\n")

            f.write("AI ANALYSIS:\n" + "="*80 + "\n")
            f.write((analysis if analysis else "AI analysis unavailable.") + "\n\n")

            f.write("RAW OUTPUT:\n" + "=" * 80 + "\n")
            f.write(output + "\n")

        return filepath

    def get_answer(self, question):
        """FAQ answer with improved matching"""
        if self.tfidf_matrix is None or not self.questions:
            self.speak("No FAQ data available.")
            return

        try:
            from fuzzywuzzy import fuzz

            question = self.preprocess(question)

            # TF-IDF score
            user_vec = self.vectorizer.transform([question])
            similarities = cosine_similarity(user_vec, self.tfidf_matrix)
            tfidf_scores = similarities[0].tolist()  # convert to plain list
            tfidf_index = int(tfidf_scores.index(max(tfidf_scores)))
            tfidf_score = float(max(tfidf_scores))

            # Fuzzy score
            fuzzy_scores = []
            for q in self.questions:
                s = float(
                    fuzz.ratio(question, q) * 0.5 +
                    fuzz.partial_ratio(question, q) * 0.3 +
                    fuzz.token_sort_ratio(question, q) * 0.2
                )
                fuzzy_scores.append(s)

            fuzzy_index = int(fuzzy_scores.index(max(fuzzy_scores)))
            fuzzy_score = float(max(fuzzy_scores)) / 100.0

            # Pick best
            if tfidf_score >= fuzzy_score:
                best_index = tfidf_index
                best_score = tfidf_score
            else:
                best_index = fuzzy_index
                best_score = fuzzy_score

            print(
                f"  Match: '{self.questions[best_index]}' (score: {best_score:.2f})")

            if best_score >= 0.65:
                self.speak(self.faqs[self.questions[best_index]])
            else:
                if self.claude_client:
                    self.answer_with_claude(question)
                else:
                    self.speak("I don't have information about that.")

        except Exception as e:
            print(f"FAQ error: {e}")
            self.speak("I don't have information about that.")

    def answer_with_claude(self, question):
        """Use Claude to answer questions not in FAQ"""
        try:
            response = self.claude_client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                max_tokens=200,
                messages=[
    {
        "role": "system",
        "content": "You are Cyber Shark, a red team cybersecurity professional and assistant with deep expertise in penetration testing, ethical hacking, and offensive security. Answer concisely and from a red team perspective."
    },
    {
        "role": "user",
        "content": f"Answer briefly: {question}"
                }]
            )
            self.speak(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠ Claude error: {e}")  # only print, never speak
            self.speak("I don't have information about that.")

    def preprocess(self, text):
        """Clean text for better matching"""
        import re
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
        text = re.sub(r'\s+', ' ', text)      # remove extra spaces
        return text

    def load_faqs(self, filename="faqs.json"):
        """Load FAQ database"""
        try:
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    self.faqs = json.load(file)
        except BaseException:
            self.faqs = {}

    def save_faqs(self, filename="faqs.json"):
        """Save FAQ database"""
        try:
            with open(filename, "w") as file:
                json.dump(self.faqs, file, indent=4)
        except BaseException:
            pass

    def handle_system_command(self, command):
        """Handle system/app commands"""

        # Open applications
        if "open notepad" in command or "open text editor" in command:
            subprocess.Popen(['mousepad'])
            self.speak("Opening text editor.")
            return True

        elif "close notepad" in command or "close text editor" in command:
            subprocess.run(['pkill', 'mousepad'])
            self.speak("Closing text editor.")
            return True

        elif "open browser" in command or "open firefox" in command:
            subprocess.Popen(['firefox'])
            self.speak("Opening Firefox.")
            return True

        elif "close browser" in command or "close firefox" in command:
            subprocess.run(['pkill', 'firefox'])
            self.speak("Closing Firefox.")
            return True

        elif "open youtube" in command:
            subprocess.Popen(['firefox', 'https://www.youtube.com'])
            self.speak("Opening YouTube.")
            return True

        elif "open google" in command:
            subprocess.Popen(['firefox', 'https://www.google.com'])
            self.speak("Opening Google.")
            return True

        elif "open terminal" in command or "open a new terminal" in command:
            subprocess.Popen(['qterminal'])
            self.speak("Opening terminal.")
            return True

        elif "close terminal" in command:
            subprocess.run(['pkill', 'qterminal'])
            self.speak("Closing terminal.")
            return True

        # Search the web
        elif "search" in command:
            query = command.replace("search", "").strip()
            if query:
                url = f"https://www.google.com/search?q={
                    query.replace(
                        ' ', '+')}"
                subprocess.Popen(['firefox', url])
                self.speak(f"Searching for {query}.")
                return True

        # Open any website
        elif "open" in command and "." in command:
            words = command.split()
            for word in words:
                if "." in word and word != command:
                    url = word if word.startswith(
                        "http") else f"https://{word}"
                    subprocess.Popen(['firefox', url])
                    self.speak(f"Opening {word}.")
                    return True

        return False  # not a system command

    def handle_command(self, command):
        """Command router"""
        command = command.lower().strip()

        if not command:
            return

        # System commands first
        if self.handle_system_command(command):
            return

        security_keywords = [
            "scan", "check", "analyze", "test", "vulnerability",
            "whois", "netstat", "nikto", "nmap", "sqlmap",
            "harvest", "dig", "dns", "port", "directory",
            "ping", "curl", "hydra", "john", "crack",
            "brute", "force", "enumerate", "exploit",
            "nslookup", "lookup", "traceroute", "recon"
        ]

        if any(kw in command for kw in security_keywords):
            intent = self.classify_intent(command)
            if intent == "info":
                # Route to FAQ / Claude Q&A instead of tool execution
                self.get_answer(command)
            else:
                self.execute_security_task(command)
            return

        self.get_answer(command)

    def run(self):
        """Main loop"""
        self.speak(f"Hello! I am {self.assistant_name}.")

        print("\n" + "=" * 70)
        print("CYBER SHARK KALI EDITION")
        print("=" * 70)
        print(f"\n📦 Available Tools ({len(self.available_tools)}):")

        by_category = {}
        for tool in self.available_tools:
            cat = self.security_tools[tool]["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tool)

        for cat, tools in sorted(by_category.items()):
            print(f"\n  {cat}:")
            for tool in tools:
                print(f"    • {tool}")

        print("\n" + "=" * 70)
        print("EXAMPLE COMMANDS:")
        print("=" * 70)
        print("  • scan localhost")
        print("  • whois google.com")
        print("  • show network connections")
        print("  • check localhost for vulnerabilities")
        print("\n  Type 'exit' to quit")
        print("=" * 70 + "\n")

        while True:
            command = self.listen() if VOICE_INPUT else ""

            if not command:
                try:
                    command = input("💬 Command: ").lower()
                except BaseException:
                    command = "exit"

            if command in ["exit", "quit", "bye", "goodbye", "shut down", "good bye",
               "shutdown", "see you", "terminate", "you can go now",
                           "turn off", "power off", "that's all", "thats all"]:
                self.save_faqs()
                self.speak("Goodbye!")
                break

            try:
                self.handle_command(command)
            except Exception as e:
                print(f"\n⚠ Error: {e}")


if __name__ == "__main__":
    try:
        shark = CyberSharkKali()
        shark.run()
    except KeyboardInterrupt:
        print("\n\n🦈 Interrupted. Goodbye!")

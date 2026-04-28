# 🎯 TalentScout – AI Hiring Assistant

> An intelligent chatbot that conducts initial candidate screening for technology roles — powered by Claude (Anthropic) and built with Streamlit.

---

## 📌 Project Overview

TalentScout is a conversational AI hiring assistant designed for **TalentScout**, a fictional technology recruitment agency. It automates the initial screening stage by:

1. **Greeting** candidates and explaining the process
2. **Gathering** essential profile information (name, contact, location, experience, desired role)
3. **Prompting** candidates to declare their tech stack
4. **Generating** 3–5 tailored technical questions per technology
5. **Concluding** gracefully and informing candidates of next steps

The chatbot maintains full conversational context, handles unexpected inputs with fallback responses, and stores session data locally in compliance with GDPR best practices.

---

## 🗂️ Project Structure

```
talentscout/
├── app.py              # Streamlit entry point & session orchestration
├── chatbot.py          # Core bot logic & Claude API integration
├── prompts.py          # All LLM-facing prompts & greeting message
├── ui_components.py    # Custom CSS, chat bubbles, sidebar renderer
├── data_handler.py     # Session persistence & GDPR-safe storage
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore
├── .streamlit/
│   └── config.toml     # Streamlit dark-theme configuration
└── data/               # Auto-created; stores session JSON files (git-ignored)
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/talentscout.git
cd talentscout

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
cp .env.example .env
# Edit .env and paste your ANTHROPIC_API_KEY

# 5. Run the app
streamlit run app.py
```

Open your browser at **http://localhost:8501**.

---

## 🚀 Usage Guide

1. **Start the app** — you'll be greeted by Scout, the AI hiring assistant.
2. **Answer questions one at a time** — Scout guides you step-by-step.
3. **Declare your tech stack** — list your languages, frameworks, databases, and tools.
4. **Answer technical questions** — Scout generates 3–5 questions per technology.
5. **End the session** — type any exit keyword (`bye`, `quit`, `exit`, etc.) or wait for Scout to wrap up naturally.
6. **Review your summary** — a session summary appears after completion.

---

## 🧠 Technical Details

| Component | Details |
|-----------|---------|
| **Language** | Python 3.11+ |
| **Frontend** | Streamlit 1.35+ with custom CSS (dark theme, Google Fonts) |
| **LLM** | `claude-sonnet-4-20250514` via Anthropic Python SDK |
| **Conversation** | Full multi-turn history passed on every API call |
| **Data storage** | Local JSON files in `./data/` (SHA-256 hashed filenames) |

---

## ✍️ Prompt Design

### System Prompt (`prompts.py`)
The system prompt defines Scout's persona, goals, and strict rules:

- **Sequential information gathering** — one field at a time to avoid overwhelming the candidate.
- **Dynamic difficulty scaling** — question complexity adapts to stated years of experience (0–2 yrs → foundational, 3–5 → applied, 6+ → architectural/trade-off).
- **Candidate context injection** — already-collected fields are appended to the system prompt each turn so the model never re-asks for known data.
- **Strict topic enforcement** — the model is instructed to redirect off-topic input back to the interview.
- **Fallback rules** — clear instructions for unclear, irrelevant, or sensitive inputs.

### Technical Question Generation
Questions are scenario-based, not definitional:
```
❌ "What is a Django ORM?"
✅ "Walk me through how you'd optimise a slow Django ORM query on a 10M-row table."
```
Questions are delivered one at a time with brief acknowledgement between answers to simulate natural conversation flow.

### Greeting
A fixed string (no API call) for instant, deterministic first impressions.

---

## 🔒 Data Privacy & GDPR

- Candidate data is stored **locally only** — never sent to third-party services beyond the Anthropic API.
- Session filenames use **one-way SHA-256 hashes** of email + random salt (no raw PII in filenames).
- The `data/` directory is **git-ignored** to prevent accidental PII commits.
- The candidate is informed of data usage at session start (inline in the greeting).
- Only the minimum required fields are collected (no salary, DOB, or SSN).

---

## 🏆 Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Maintaining context across turns | Full conversation history (`self.history`) passed to Claude on every request, plus a candidate profile block appended to the system prompt |
| Avoiding repeated questions | Context block in the system prompt lists all already-collected fields; Claude instructed to skip them |
| Tech stack detection | Lightweight keyword scan (`_infer_tech_stack`) for immediate UI feedback; Claude handles nuanced extraction |
| Conversation end detection | Dual mechanism: exit keyword fast-path + `_did_model_end` heuristic on the reply text |
| GDPR-safe storage | Hashed filenames, local-only storage, minimal PII, git-ignored data directory |
| Streamlit re-rendering | `st.rerun()` called after each message to flush the chat container cleanly |

---

## 🎁 Optional Enhancements Implemented

- ✅ **Custom dark-mode UI** with Syne + DM Sans fonts, animated chat bubbles
- ✅ **Live candidate profile sidebar** — fields populate in real-time as information is collected
- ✅ **Session summary** — displayed on conversation end
- ✅ **GDPR-compliant local storage** with hashed session IDs
- ✅ **Graceful fallback** — model redirects irrelevant/harmful input

---

## 📄 License

MIT — free to use, modify, and distribute.

---

*Built for the TalentScout AI/ML Intern Assignment · 2025*
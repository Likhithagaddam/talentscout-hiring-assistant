"""
TalentScout Chatbot Core
Handles all LLM interactions via the Groq API (llama-3.3-70b-versatile).
"""

import os
import re
import json
from groq import Groq
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, GREETING_MESSAGE, END_KEYWORDS

load_dotenv()

# ── Groq client ───────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

MODEL = "llama-3.3-70b-versatile"   # Fast, free-tier Groq model
MAX_TOKENS = 1024


class TalentScoutBot:
    """
    Stateful hiring assistant that gathers candidate info and
    generates tailored technical questions.
    """

    def __init__(self):
        self.history: list[dict] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def get_greeting(self) -> str:
        """Return the fixed opening message."""
        return GREETING_MESSAGE

    def respond(
        self,
        user_message: str,
        current_info: dict,
    ) -> tuple[str, dict, bool]:
        """
        Process user input and return (assistant_reply, updated_info, ended).

        Parameters
        ----------
        user_message : str
            Raw text from the candidate.
        current_info : dict
            Accumulated candidate data from previous turns.

        Returns
        -------
        str   – assistant reply
        dict  – newly extracted candidate fields (merged by caller)
        bool  – True when the conversation should end
        """
        # Check for exit intent first (fast path)
        if self._is_exit_intent(user_message):
            farewell = self._farewell(current_info)
            return farewell, {}, True

        # Append user turn to history
        self.history.append({"role": "user", "content": user_message})

        # Build context-aware system prompt
        system = self._build_system_prompt(current_info)

        # Call Groq
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[
                    {"role": "system", "content": system},
                    *self.history,
                ],
            )
            reply: str = completion.choices[0].message.content
        except Exception as exc:  # pragma: no cover
            reply = (
                "I'm sorry, I encountered a technical issue. "
                f"Please try again in a moment. (Error: {exc})"
            )

        # Append assistant turn
        self.history.append({"role": "assistant", "content": reply})

        # Extract any structured info the model embedded
        extracted = self._extract_candidate_info(reply, user_message, current_info)

        # Detect graceful conversation end triggered by the model
        ended = self._did_model_end(reply)

        return reply, extracted, ended

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _is_exit_intent(self, text: str) -> bool:
        """Return True if the user typed a conversation-ending keyword."""
        lowered = text.strip().lower()
        return any(kw in lowered for kw in END_KEYWORDS)

    def _farewell(self, info: dict) -> str:
        """Generate a personalised goodbye."""
        name = info.get("full_name", "there")
        first = name.split()[0] if name and name != "there" else name
        return (
            f"Thank you so much, {first}! 🎉 It was a pleasure speaking with you.\n\n"
            "Our recruitment team at **TalentScout** will carefully review your responses "
            "and get back to you within **2–3 business days**.\n\n"
            "In the meantime, feel free to reach us at **careers@talentscout.ai**.\n\n"
            "Wishing you the very best of luck! 🚀"
        )

    def _build_system_prompt(self, info: dict) -> str:
        """Inject current candidate context into the system prompt."""
        context_block = ""
        if info:
            context_block = "\n\n**CANDIDATE PROFILE SO FAR:**\n```json\n"
            context_block += json.dumps(info, indent=2)
            context_block += "\n```\nUse this to avoid re-asking collected fields."
        return SYSTEM_PROMPT + context_block

    # ── Info extraction ───────────────────────────────────────────────────────

    def _extract_candidate_info(
        self, reply: str, user_msg: str, existing: dict
    ) -> dict:
        """
        Heuristically pull structured fields from the conversation.
        A lightweight extraction so we don't need a second LLM call.
        """
        extracted: dict = {}

        # ── Full name (user message, simple heuristic) ────────────────────
        if "full_name" not in existing:
            name_match = self._find_name(user_msg, reply)
            if name_match:
                extracted["full_name"] = name_match

        # ── Email ─────────────────────────────────────────────────────────
        if "email" not in existing:
            email = self._find_pattern(
                r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", user_msg
            )
            if email:
                extracted["email"] = email

        # ── Phone ─────────────────────────────────────────────────────────
        if "phone" not in existing:
            phone = self._find_pattern(
                r"(\+?\d[\d\s\-().]{7,}\d)", user_msg
            )
            if phone:
                extracted["phone"] = phone.strip()

        # ── Years of experience ───────────────────────────────────────────
        if "years_of_experience" not in existing:
            yoe = self._find_pattern(r"\b(\d+)\s*(?:years?|yrs?)\b", user_msg)
            if yoe:
                extracted["years_of_experience"] = yoe

        # ── Location ──────────────────────────────────────────────────────
        if "location" not in existing:
            loc = self._infer_location(user_msg, reply)
            if loc:
                extracted["location"] = loc

        # ── Tech stack ────────────────────────────────────────────────────
        if "tech_stack" not in existing:
            tech = self._infer_tech_stack(user_msg)
            if tech:
                extracted["tech_stack"] = tech

        # ── Desired position ──────────────────────────────────────────────
        if "desired_position" not in existing:
            pos = self._infer_position(user_msg, reply)
            if pos:
                extracted["desired_position"] = pos

        return extracted

    # ── Regex helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _find_pattern(pattern: str, text: str) -> str | None:
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(0) if m else None

    @staticmethod
    def _find_name(user_msg: str, reply: str) -> str | None:
        """
        Detect name if the assistant just asked for it and the user replied
        with 1-4 capitalised words that look like a name.
        """
        asking_for_name = any(
            kw in reply.lower()
            for kw in ("full name", "your name", "may i know your name", "could you share your name")
        )
        if asking_for_name:
            m = re.match(r"^([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,3})$", user_msg.strip())
            if m:
                return m.group(1)
        return None

    @staticmethod
    def _infer_location(user_msg: str, reply: str) -> str | None:
        asking = any(
            kw in reply.lower()
            for kw in ("location", "based", "city", "country", "where are you")
        )
        if asking and len(user_msg.strip()) < 60:
            return user_msg.strip().title()
        return None

    @staticmethod
    def _infer_position(user_msg: str, reply: str) -> str | None:
        asking = any(
            kw in reply.lower()
            for kw in ("position", "role", "applying for", "interested in")
        )
        if asking and len(user_msg.strip()) < 80:
            return user_msg.strip()
        return None

    @staticmethod
    def _infer_tech_stack(user_msg: str) -> str | None:
        """Detect tech keywords in a message."""
        TECH_KEYWORDS = [
            "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
            "react", "vue", "angular", "next", "django", "flask", "fastapi", "spring",
            "node", "express", "laravel", "rails", "postgres", "mysql", "mongodb",
            "redis", "docker", "kubernetes", "aws", "gcp", "azure", "terraform",
            "git", "linux", "graphql", "rest", "tensorflow", "pytorch", "scikit",
        ]
        found = [kw for kw in TECH_KEYWORDS if kw in user_msg.lower()]
        return ", ".join(found) if len(found) >= 2 else None

    @staticmethod
    def _did_model_end(reply: str) -> bool:
        """Check if the model's reply signals the end of the interview."""
        END_PHRASES = [
            "thank you for your time",
            "best of luck",
            "our team will be in touch",
            "we will review your responses",
            "recruitment team will",
            "goodbye",
            "all the best",
        ]
        lowered = reply.lower()
        return sum(p in lowered for p in END_PHRASES) >= 2
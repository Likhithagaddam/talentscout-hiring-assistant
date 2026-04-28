"""
TalentScout – Streamlit UI helpers.
Custom CSS, chat message rendering, and the sidebar.
"""

import streamlit as st


# ── CSS injection ─────────────────────────────────────────────────────────────
def inject_custom_css() -> None:
    """Inject custom CSS for a polished dark-mode interface."""
    st.markdown(
        """
        <style>
        /* ── Google Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

        /* ── Root palette ── */
        :root {
            --bg:          #0d0f14;
            --surface:     #161920;
            --surface2:    #1e2230;
            --border:      #2a2f42;
            --accent:      #6c63ff;
            --accent2:     #ff6584;
            --text:        #e8eaf0;
            --text-muted:  #7b82a0;
            --success:     #4ade80;
            --radius:      12px;
        }

        /* ── Global resets ── */
        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            background-color: var(--bg) !important;
            color: var(--text) !important;
        }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1.5rem !important; max-width: 860px; }

        /* ── Header ── */
        .header-block {
            display: flex;
            align-items: baseline;
            gap: 1rem;
        }
        .logo-text {
            font-family: 'Syne', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .tagline {
            font-size: 0.85rem;
            color: var(--text-muted);
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .status-badge {
            background: rgba(74, 222, 128, 0.12);
            color: var(--success);
            border: 1px solid rgba(74, 222, 128, 0.25);
            border-radius: 20px;
            padding: 0.3rem 0.9rem;
            font-size: 0.78rem;
            letter-spacing: 0.05em;
            font-weight: 500;
            text-align: right;
            margin-top: 0.6rem;
        }
        .divider {
            height: 1px;
            background: linear-gradient(90deg, var(--accent) 0%, transparent 100%);
            margin: 0.8rem 0 1.4rem;
            opacity: 0.35;
        }

        /* ── Chat bubbles ── */
        .chat-row {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.1rem;
            align-items: flex-start;
            animation: fadeUp 0.3s ease;
        }
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .chat-row.user  { flex-direction: row-reverse; }
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            flex-shrink: 0;
        }
        .avatar.assistant { background: linear-gradient(135deg, var(--accent), #8b5cf6); }
        .avatar.user      { background: linear-gradient(135deg, #f59e0b, var(--accent2)); }
        .bubble {
            max-width: 78%;
            padding: 0.85rem 1.1rem;
            border-radius: var(--radius);
            line-height: 1.6;
            font-size: 0.93rem;
        }
        .bubble.assistant {
            background: var(--surface);
            border: 1px solid var(--border);
            border-top-left-radius: 3px;
        }
        .bubble.user {
            background: linear-gradient(135deg, var(--accent) 0%, #8b5cf6 100%);
            color: #fff;
            border-top-right-radius: 3px;
        }
        .bubble p { margin: 0 0 0.5rem; }
        .bubble p:last-child { margin-bottom: 0; }
        .bubble code {
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            padding: 0.1em 0.4em;
            font-size: 0.88em;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: var(--surface) !important;
            border-right: 1px solid var(--border) !important;
        }
        .sidebar-title {
            font-family: 'Syne', sans-serif;
            font-weight: 700;
            font-size: 1rem;
            color: var(--accent);
            margin-bottom: 1rem;
            letter-spacing: 0.04em;
        }
        .info-card {
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 0.75rem 1rem;
            margin-bottom: 0.6rem;
        }
        .info-label {
            font-size: 0.72rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.2rem;
        }
        .info-value {
            font-size: 0.9rem;
            color: var(--text);
            font-weight: 500;
        }
        .privacy-note {
            font-size: 0.72rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border);
            padding-top: 0.75rem;
            margin-top: 1rem;
            line-height: 1.5;
        }

        /* ── Chat input override ── */
        [data-testid="stChatInput"] textarea {
            background: var(--surface2) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important;
            color: var(--text) !important;
            font-family: 'DM Sans', sans-serif !important;
        }
        [data-testid="stChatInput"] textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px rgba(108,99,255,0.2) !important;
        }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(135deg, var(--accent), #8b5cf6) !important;
            color: #fff !important;
            border: none !important;
            border-radius: var(--radius) !important;
            font-family: 'Syne', sans-serif !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.2rem !important;
        }

        /* ── Spinner ── */
        .stSpinner > div { border-top-color: var(--accent) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Chat message renderer ─────────────────────────────────────────────────────
def render_chat_message(role: str, content: str) -> None:
    """Render a single chat bubble with avatar."""
    avatar = "🤖" if role == "assistant" else "👤"
    bubble_class = role

    st.markdown(
        f"""
        <div class="chat-row {role}">
            <div class="avatar {role}">{avatar}</div>
            <div class="bubble {bubble_class}">{_md_to_html(content)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _md_to_html(text: str) -> str:
    """
    Minimal markdown → HTML conversion for the bubble renderer.
    (Streamlit's native markdown doesn't render inside custom HTML.)
    """
    import re

    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Inline code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Newlines → <br> / paragraphs
    paragraphs = text.split("\n\n")
    rendered = []
    for para in paragraphs:
        lines = para.split("\n")
        rendered.append("<br>".join(lines))
    return "<p>" + "</p><p>".join(rendered) + "</p>"


# ── Sidebar ───────────────────────────────────────────────────────────────────
FIELD_LABELS = {
    "full_name":          "Full Name",
    "email":              "Email",
    "phone":              "Phone",
    "location":           "Location",
    "years_of_experience":"Experience",
    "desired_position":   "Desired Role",
    "tech_stack":         "Tech Stack",
}


def render_sidebar(candidate_info: dict) -> None:
    """Render the candidate profile sidebar."""
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🗂️ Candidate Profile</div>', unsafe_allow_html=True)

        if not candidate_info:
            st.markdown(
                '<p style="color:var(--text-muted);font-size:0.85rem;">'
                "Your details will appear here as the conversation progresses.</p>",
                unsafe_allow_html=True,
            )
        else:
            for key, label in FIELD_LABELS.items():
                if key in candidate_info:
                    value = candidate_info[key]
                    st.markdown(
                        f"""
                        <div class="info-card">
                            <div class="info-label">{label}</div>
                            <div class="info-value">{value}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown(
            """
            <div class="privacy-note">
                🔒 Your data is handled securely and used solely for recruitment purposes,
                in compliance with GDPR guidelines.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(
            '<p style="color:var(--text-muted);font-size:0.75rem;text-align:center;">'
            "TalentScout © 2025 · AI Hiring Assistant</p>",
            unsafe_allow_html=True,
        )
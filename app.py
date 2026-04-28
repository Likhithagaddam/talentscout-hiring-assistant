"""
TalentScout - AI Hiring Assistant Chatbot
Main Streamlit application entry point.
"""

import streamlit as st
from chatbot import TalentScoutBot
from ui_components import render_sidebar, render_chat_message, inject_custom_css
from data_handler import save_candidate_session, load_session_summary

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TalentScout | AI Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

# ── Session state bootstrap ───────────────────────────────────────────────────
def init_session():
    if "bot" not in st.session_state:
        st.session_state.bot = TalentScoutBot()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_ended" not in st.session_state:
        st.session_state.conversation_ended = False
    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info = {}
    if "initialized" not in st.session_state:
        st.session_state.initialized = False

init_session()

# ── Header ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(
        """
        <div class="header-block">
            <span class="logo-text">🎯 TalentScout</span>
            <span class="tagline">AI-Powered Hiring Assistant</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        '<div class="status-badge">● Live Session</div>', unsafe_allow_html=True
    )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
render_sidebar(st.session_state.candidate_info)

# ── Chat container ────────────────────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    # Send greeting on first load
    if not st.session_state.initialized:
        greeting = st.session_state.bot.get_greeting()
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.session_state.initialized = True

    # Render all messages
    for msg in st.session_state.messages:
        render_chat_message(msg["role"], msg["content"])

# ── Input area ────────────────────────────────────────────────────────────────
st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

if st.session_state.conversation_ended:
    st.success(
        "✅ Interview session completed! Our team will review your responses and get back to you."
    )
    summary = load_session_summary(st.session_state.candidate_info)
    if summary:
        with st.expander("📋 Your Session Summary"):
            st.markdown(summary)

    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("🔄 Start New Session", type="primary"):
            for key in ["bot", "messages", "conversation_ended", "candidate_info", "initialized"]:
                st.session_state.pop(key, None)
            st.rerun()
else:
    user_input = st.chat_input(
        "Type your response here…",
        disabled=st.session_state.conversation_ended,
    )

    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get bot response
        with st.spinner("TalentScout is thinking…"):
            response, candidate_info, ended = st.session_state.bot.respond(
                user_input, st.session_state.candidate_info
            )

        # Update state
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.candidate_info.update(candidate_info)

        if ended:
            st.session_state.conversation_ended = True
            save_candidate_session(
                st.session_state.candidate_info,
                st.session_state.messages,
            )

        st.rerun()
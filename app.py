"""Streamlit chat UI for the IUBAT FAQ chatbot. Run: streamlit run app.py"""
import time

import streamlit as st

from chatbot import FAQChatbot

CONTACT_EMAIL = "admissions@iubat.edu"
WELCOME = (
    "Hello! I'm the IUBAT Admission Assistant. Ask me about admission "
    "requirements, programs, scholarships, the campus or how to contact the "
    "admission office."
)

# (button label, question sent to the bot)
QUICK_QUESTIONS = [
    ("📝  Admission requirements", "What are the admission requirements?"),
    ("🎓  Programs offered", "Which programs does IUBAT offer?"),
    ("🏅  Scholarships", "What scholarships are available?"),
    ("📅  Admission deadline", "When is the admission deadline?"),
    ("📍  Campus location", "Where is the campus located?"),
    ("✉️  Contact", "How can I contact the admission office?"),
]

CATEGORY_LABELS = {
    "about": "About IUBAT",
    "programs": "Programs",
    "admission": "Admission",
    "fees": "Fees",
    "scholarship": "Scholarships",
    "contact": "Contact",
    "smalltalk": "Assistant",
}

st.set_page_config(
    page_title="IUBAT Admission Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp, button, input, textarea { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; height: 0; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 860px; padding-top: 1.2rem; padding-bottom: 6rem; }

/* ---------- hero ---------- */
.hero {
    background: linear-gradient(135deg, #064E32 0%, #0B7A4B 55%, #14A36A 100%);
    border-radius: 20px; padding: 2rem 2.2rem; color: #fff;
    box-shadow: 0 10px 30px rgba(6, 78, 50, .25); margin-bottom: 1.4rem;
}
.hero .pill {
    display: inline-block; font-size: .72rem; font-weight: 600; letter-spacing: .06em;
    text-transform: uppercase; background: rgba(255,255,255,.16);
    border: 1px solid rgba(255,255,255,.28); padding: .25rem .7rem; border-radius: 999px;
}
.hero h1 { color: #fff; font-size: 2rem; font-weight: 800; margin: .7rem 0 .35rem; padding: 0; line-height: 1.15; }
.hero p  { color: rgba(255,255,255,.88); font-size: 1rem; margin: 0; max-width: 560px; line-height: 1.5; }

/* ---------- section label ---------- */
.label { font-size: .78rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
         color: #5B6B63; margin: .2rem 0 .6rem; }

/* ---------- quick-question buttons ---------- */
div.stButton > button {
    width: 100%; border-radius: 12px; border: 1px solid #D6E2DB; background: #FFFFFF;
    color: #14211B; font-weight: 600; font-size: .92rem; padding: .7rem .9rem;
    box-shadow: 0 1px 2px rgba(20, 33, 27, .05); transition: all .15s ease;
}
div.stButton > button:hover {
    border-color: #0B7A4B; color: #0B7A4B; background: #F0F9F4;
    transform: translateY(-1px); box-shadow: 0 6px 14px rgba(11, 122, 75, .12);
}
div.stButton > button:focus:not(:active) { border-color: #0B7A4B; color: #0B7A4B; }

/* ---------- chat bubbles ---------- */
[data-testid="stChatMessage"] {
    background: #FFFFFF; border: 1px solid #E1EAE5; border-radius: 16px;
    padding: 1rem 1.2rem; margin-bottom: .8rem; box-shadow: 0 1px 3px rgba(20, 33, 27, .05);
}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
    background: #E8F5EE; border-color: #CBE6D7;
}
[data-testid="stChatMessage"] p { font-size: .98rem; line-height: 1.6; }
.tag {
    display: inline-block; font-size: .7rem; font-weight: 700; letter-spacing: .05em;
    text-transform: uppercase; color: #0B7A4B; background: #E1F3E9;
    padding: .18rem .6rem; border-radius: 999px; margin-top: .3rem;
}
.tag.warn { color: #8A5A00; background: #FFF1D6; }

/* ---------- chat input ---------- */
[data-testid="stChatInput"] { border-radius: 14px; border: 1px solid #CBD9D0; box-shadow: 0 4px 16px rgba(20,33,27,.08); }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E1EAE5; }
.side-card { background: #F4F9F6; border: 1px solid #DCEBE2; border-radius: 14px; padding: 1rem; margin-bottom: 1rem; }
.side-card h4 { margin: 0 0 .4rem; font-size: .95rem; color: #064E32; }
.side-card p, .side-card li { font-size: .85rem; color: #34453C; line-height: 1.5; margin: 0; }
.side-card ul { padding-left: 1.1rem; margin: .2rem 0 0; }
.side-card a { color: #0B7A4B; font-weight: 600; text-decoration: none; }
.disclaimer { font-size: .75rem; color: #6B7B73; line-height: 1.5; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource
def load_bot() -> FAQChatbot:
    return FAQChatbot()


def type_out(text: str) -> None:
    """Show the answer word by word (typing effect) without extra libraries."""
    box = st.empty()
    shown = ""
    for word in text.split(" "):
        shown += word + " "
        box.markdown(shown + "▌")
        time.sleep(0.025)
    box.markdown(text)


def tag_html(result: dict) -> str:
    if result.get("found") and result.get("category"):
        label = CATEGORY_LABELS.get(result["category"], result["category"].title())
        return f'<span class="tag">{label}</span>'
    if not result.get("found"):
        return '<span class="tag warn">Not in my FAQ</span>'
    return ""


bot = load_bot()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("### 🎓 IUBAT Assistant")
    st.markdown(
        f"""
        <div class="side-card">
          <h4>Contact the admission office</h4>
          <p>✉️ <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
          <p style="margin-top:.4rem">🌐 <a href="https://iubat.edu/admission" target="_blank">iubat.edu/admission</a></p>
        </div>
        <div class="side-card">
          <h4>What I can help with</h4>
          <ul>
            <li>Admission requirements</li>
            <li>Programs and duration</li>
            <li>Scholarships</li>
            <li>Campus and contact info</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_details = st.toggle("Show match details", value=False, help="Shows how confident the bot is in each answer.")
    if st.button("🗑️  Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown(
        '<p class="disclaimer">Unofficial student project. Answers are based on public IUBAT '
        "admission information and may change. Always confirm at iubat.edu.</p>",
        unsafe_allow_html=True,
    )

# --------------------------------------------------------------------- hero
st.markdown(
    """
    <div class="hero">
      <span class="pill">AI FAQ Chatbot</span>
      <h1>IUBAT Admission Assistant</h1>
      <p>Instant answers about admission, programs, scholarships and campus life. Type a question or pick a topic below.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------ quick questions
st.markdown('<div class="label">Popular questions</div>', unsafe_allow_html=True)
cols = st.columns(3)
for i, (label, question) in enumerate(QUICK_QUESTIONS):
    if cols[i % 3].button(label, key=f"quick_{i}", use_container_width=True):
        st.session_state.queued = question

st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------ history
with st.chat_message("assistant", avatar=":material/school:"):
    st.markdown(WELCOME)

for msg in st.session_state.messages:
    avatar = ":material/person:" if msg["role"] == "user" else ":material/school:"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            st.markdown(msg.get("tag", ""), unsafe_allow_html=True)
            if show_details and msg.get("note"):
                st.caption(msg["note"])

# -------------------------------------------------------------- new question
queued = st.session_state.pop("queued", None)
prompt = st.chat_input("Ask about admission, programs, scholarships...") or queued

if prompt:
    result = bot.get_response(prompt)
    note = f"Confidence: {result['score']:.0%}" + (
        f"  ·  matched: “{result['matched']}”" if result["matched"] else ""
    )
    tag = tag_html(result)

    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar=":material/school:"):
        with st.spinner("Thinking..."):
            time.sleep(0.4)
        type_out(result["answer"])
        st.markdown(tag, unsafe_allow_html=True)
        if show_details:
            st.caption(note)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append(
        {"role": "assistant", "content": result["answer"], "tag": tag, "note": note}
    )
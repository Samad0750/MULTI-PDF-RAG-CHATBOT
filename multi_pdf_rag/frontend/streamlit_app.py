import streamlit as st
import requests
from datetime import datetime
import hashlib
import html
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Enterprise Multi PDF AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# BACKEND URL
# =========================
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")
REQUEST_TIMEOUT = 120


def safe_text(value):
    return html.escape(str(value))


def format_source(source):
    if isinstance(source, dict):
        source_name = source.get("source") or "Unknown source"
        page = source.get("page")
        if page is not None:
            return f"{source_name} - page {page}"
        return source_name
    return str(source)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>

/* Main App */
.stApp {
    background: linear-gradient(135deg, #050816 0%, #0b1120 40%, #111827 100%);
    color: white;
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 22px;
    padding: 20px;
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* Title */
.main-title {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    color: #9ca3af;
    font-size: 1.1rem;
    margin-bottom: 30px;
}

/* Metric Card */
.metric-card {
    background: rgba(255,255,255,0.05);
    padding: 18px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
}

/* Chat Bubble User */
.user-bubble {
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    padding: 15px;
    border-radius: 18px;
    margin-top: 10px;
    color: white;
}

/* Chat Bubble AI */
.ai-bubble {
    background: rgba(255,255,255,0.06);
    padding: 18px;
    border-radius: 18px;
    margin-top: 10px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(17,24,39,0.95);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 12px 20px;
    font-weight: 600;
    width: 100%;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 6px 20px rgba(124,58,237,0.5);
}

/* Text Input */
.stTextInput>div>div>input {
    background-color: rgba(255,255,255,0.06);
    color: white;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    padding: 12px;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.04);
    padding: 15px;
    border-radius: 18px;
    border: 1px dashed rgba(255,255,255,0.2);
}

/* Suggested Prompt */
.prompt-card {
    background: rgba(255,255,255,0.04);
    padding: 12px;
    border-radius: 14px;
    margin-bottom: 10px;
    border: 1px solid rgba(255,255,255,0.06);
}

/* Source Box */
.source-box {
    background: rgba(255,255,255,0.04);
    padding: 12px;
    border-radius: 14px;
    border-left: 4px solid #7c3aed;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "uploaded_file_hashes" not in st.session_state:
    st.session_state.uploaded_file_hashes = set()

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.markdown("## 🤖 Enterprise AI")
    st.markdown("---")

    st.markdown("### 📊 Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(st.session_state.uploaded_files)}</h2>
            <p>Documents</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(st.session_state.chat_history)}</h2>
            <p>Chats</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 💡 Suggested Prompts")

    prompts = [
        "Summarize all uploaded documents",
        "What are the key insights?",
        "Compare all PDFs",
        "Generate executive summary",
        "Find important statistics",
        "Extract action items"
    ]

    for prompt in prompts:
        st.markdown(
            f'<div class="prompt-card">✨ {prompt}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown("### 🕒 Conversation History")

    if st.session_state.chat_history:
        for idx, chat in enumerate(reversed(st.session_state.chat_history[-5:])):
            safe_history_question = safe_text(chat["question"][:40])
            st.markdown(
                f"""
                <div class="prompt-card">
                <b>Q:</b> {safe_history_question}...
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No conversations yet")

# =========================
# MAIN HEADER
# =========================
st.markdown(
    '<div class="main-title">Enterprise Multi PDF Q/A</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Upload multiple PDFs and chat with your enterprise knowledge base using AI.</div>',
    unsafe_allow_html=True
)

# =========================
# METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

metrics = [
    ("📄 Total PDFs", len(st.session_state.uploaded_files)),
    ("💬 Conversations", len(st.session_state.chat_history)),
    ("⚡ AI Status", "Online"),
    ("🔒 Security", "Enterprise")
]

for col, metric in zip([col1, col2, col3, col4], metrics):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3>{metric[1]}</h3>
                <p>{metric[0]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# FILE UPLOAD SECTION
# =========================
st.markdown("## 📂 Upload Documents")

uploaded_files = st.file_uploader(
    "Upload PDF Files",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload enterprise PDFs for AI analysis"
)

if uploaded_files:

    pending_files = []
    for file in uploaded_files:
        file_bytes = file.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        if file_hash not in st.session_state.uploaded_file_hashes:
            pending_files.append((file, file_bytes, file_hash))

    if not pending_files:
        st.info("Selected PDFs are already uploaded for this session.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        stats_container = st.empty()

        for idx, (file, file_bytes, file_hash) in enumerate(pending_files):

            status_text.info(f"Uploading {file.name}...")

            files = {
                "file": (file.name, file_bytes, "application/pdf")
            }

            try:
                response = requests.post(
                    f"{BACKEND_URL}/upload",
                    files=files,
                    timeout=REQUEST_TIMEOUT
                )

                if response.status_code == 200:
                    data = response.json()
                    upload_result = data.get("upload_result", {})
                    status = upload_result.get("status")

                    st.session_state.uploaded_file_hashes.add(file_hash)
                    if file.name not in st.session_state.uploaded_files:
                        st.session_state.uploaded_files.append(file.name)

                    if status == "skipped":
                        st.info(f"Already indexed: {file.name}")
                    else:
                        st.success(f"✅ Uploaded: {file.name}")

                    vec_stats = data.get("vec_stats")
                    if vec_stats:
                        with stats_container.expander("Vector DB stats after upload", expanded=True):
                            st.write(vec_stats)
                else:
                    st.error(
                        f"❌ Failed to upload {file.name}: {response.status_code} - {response.text}"
                    )

            except Exception as e:
                st.error(f"Backend Error: {e}")

            progress = (idx + 1) / len(pending_files)
            progress_bar.progress(progress)

        status_text.success("🎉 New documents are ready!")

# =========================
# CHAT SECTION
# =========================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("## 💬 AI Assistant")

question = st.text_input(
    "Ask anything about your documents",
    placeholder="Example: Summarize the financial report..."
)

colA, colB = st.columns([5,1])

with colA:
    generate = st.button("🚀 Generate Answer")

with colB:
    clear = st.button("🗑️ Clear")

# =========================
# CLEAR CHAT
# =========================
if clear:
    st.session_state.chat_history = []
    st.rerun()

# =========================
# GENERATE ANSWER
# =========================
if generate:

    if not question:
        st.warning("Please enter a question.")
    else:

        with st.spinner("🤖 AI is analyzing documents..."):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "question": question
                    },
                    timeout=REQUEST_TIMEOUT
                )

                if response.status_code == 200:

                    data = response.json()

                    answer = data.get("answer", "No answer found.")
                    sources = data.get("sources", [])
                    safe_question = safe_text(question)
                    safe_answer = safe_text(answer)

                    # Save History
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "time": datetime.now().strftime("%H:%M")
                    })

                    # USER MESSAGE
                    st.markdown(
                        f"""
                        <div class="user-bubble">
                        <b>🧑 You:</b><br><br>
                        {safe_question}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # AI RESPONSE
                    st.markdown(
                        f"""
                        <div class="ai-bubble">
                        <b>🤖 AI Assistant:</b><br><br>
                        {safe_answer}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # SOURCES
                    if sources:

                        st.markdown("### 📚 Sources")

                        for source in sources:
                            source = safe_text(format_source(source))

                            st.markdown(
                                f"""
                                <div class="source-box">
                                📄 {source}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                else:
                    st.error("Failed to generate answer.")

            except Exception as e:
                st.error(f"Connection Error: {e}")

# =========================
# RECENT CONVERSATIONS
# =========================
if st.session_state.chat_history:

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 🧠 Recent Conversations")

    for chat in reversed(st.session_state.chat_history[-3:]):

        with st.expander(f"🕒 {chat['time']} - {chat['question'][:80]}"):

            st.markdown(
                f"""
                <div class="ai-bubble">
                {safe_text(chat['answer'])}
                </div>
                """,
                unsafe_allow_html=True
            )

# =========================
# FOOTER
# =========================
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown(
    """
    <center>
    <p style='color:#6b7280'>
    Enterprise AI Document Intelligence • Built with Streamlit + FastAPI + LangChain
    </p>
    </center>
    """,
    unsafe_allow_html=True
)

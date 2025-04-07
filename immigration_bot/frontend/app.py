import streamlit as st
import requests

st.set_page_config(page_title="ImmigraBot", page_icon="🧠")
st.markdown(
    """
    <style>
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        width: fit-content;
        max-width: 80%;
    }
    .user-bubble {
        background-color: #DCF8C6;
        align-self: flex-end;
        margin-left: auto;
    }
    .bot-bubble {
        background-color: #F1F0F0;
        align-self: flex-start;
        margin-right: auto;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧠 ImmigraBot - U.S. Immigration Law Assistant")
st.info("⚠️ This tool is for informational purposes only and does not provide legal advice. Please consult an immigration attorney for legal matters.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render message history
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    bubble_class = "user-bubble" if role == "user" else "bot-bubble"
    emoji = "🧑" if role == "user" else "🤖"

    st.markdown(
        f"""
        <div class="chat-container">
            <div class="chat-bubble {bubble_class}">
                <b>{emoji} {role.capitalize()}:</b><br>{content}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Show sources if available
    if role == "bot" and msg.get("sources"):
        with st.expander("📄 Show sources"):
            for src in sorted(set(msg["sources"])):
                st.markdown(f"- `{src}`")

# Get user input
query = st.chat_input("Ask your question here...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    # Retrieve previous user message for memory
    previous = ""
    for msg in reversed(st.session_state.messages[:-1]):
        if msg["role"] == "user":
            previous = msg["content"]
            break

    full_query = f"Previous question: {previous}\n\nFollow-up: {query}" if previous else query

    with st.spinner("ImmigraBot is thinking..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/query",
                json={"query": full_query},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "Sorry, I couldn’t find an answer.")
                sources = data.get("sources", [])

                st.session_state.messages.append({
                    "role": "bot",
                    "content": answer,
                    "sources": sources
                })
                st.rerun()
            else:
                error_msg = f"⚠️ Error: {response.status_code} — {response.text}"
                st.session_state.messages.append({"role": "bot", "content": error_msg})

        except Exception as e:
            st.session_state.messages.append({"role": "bot", "content": str(e)})
            st.error(f"💥 Something went wrong: {e}") 
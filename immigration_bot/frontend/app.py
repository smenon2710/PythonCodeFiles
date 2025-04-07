import streamlit as st
import requests

st.set_page_config(page_title="ImmigraBot", page_icon="🧠")
st.title("🧠 ImmigraBot - U.S. Immigration Law Assistant")

st.info("⚠️ This tool is for informational purposes only and does not provide legal advice. Please consult an immigration attorney for legal matters.")

# Init chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.markdown(f"**🧑 You:** {content}")
    else:
        st.markdown(f"**🤖 ImmigraBot:** {content}")
        if msg.get("sources"):
            with st.expander("📄 Show sources"):
                unique_sources = sorted(set(msg["sources"]))
                for src in unique_sources:
                    st.markdown(f"- `{src}`")

# Chat input
query = st.chat_input("Ask your question here...")

if query:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": query})
    st.markdown(f"**🧑 You:** {query}")

    # Use previous user message for context
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

                # Save bot message with sources
                st.session_state.messages.append({
                    "role": "bot",
                    "content": answer,
                    "sources": sources
                })
                st.markdown(f"**🤖 ImmigraBot:** {answer}")
                if sources:
                    with st.expander("📄 Show sources"):
                        unique_sources = sorted(set(sources))
                        for src in unique_sources:
                            st.markdown(f"- `{src}`")

            else:
                error_msg = f"⚠️ Error: {response.status_code} — {response.text}"
                st.session_state.messages.append({"role": "bot", "content": error_msg})
                st.error(error_msg)

        except Exception as e:
            st.session_state.messages.append({"role": "bot", "content": str(e)})
            st.error(f"💥 Something went wrong: {e}")

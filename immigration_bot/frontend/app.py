import streamlit as st
import requests

st.title("🤖 ImmigraBot - AI Immigration Law Assistant")
st.info("⚠️ This chatbot is for informational purposes only and does not provide legal advice.")

query = st.text_input("Ask a question about U.S. immigration law:")

if query:
    with st.spinner("Thinking..."):
        res = requests.post("http://localhost:8000/query", json={"query": query})
        if res.ok:
            data = res.json()
            st.success(data["answer"])
            st.markdown("**Sources:**")
            for i, src in enumerate(data["sources"]):
                st.write(f"{i+1}. {src.get('source', 'Unknown Source')}")
        else:
            st.error("Something went wrong.")

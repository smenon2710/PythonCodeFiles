# 🧠 ImmigraBot - U.S. Immigration Law Assistant

This project is a local Retrieval-Augmented Generation (RAG) chatbot that helps answer U.S. immigration-related questions based on the official USCIS policy manual PDF.

> ⚠️ This tool is for educational and informational purposes only. It does not provide legal advice. Please consult a licensed immigration attorney for official guidance.

---

## 🚀 Features

- Question-answering over U.S. immigration PDF content
- Local FAISS vector store for fast document retrieval
- Streamlit-powered frontend chatbot
- FastAPI backend for processing responses
- Pre-ingested policy manual for plug-and-play experience

---

## 📁 Folder Structure
immigration_bot/ ├── backend/ │ ├── app.py # FastAPI app (backend) │ ├── ingest_docs.py # Script to ingest PDF and build FAISS index │ ├── rag_pipeline.py # RAG pipeline logic │ ├── vector_store.py # Optional: FAISS helper (if used) │ ├── test_faiss_query.py # Script to test index queries locally │ ├── data/ │ └── raw/ │ └── uscis_policy_manual.pdf # PDF used for ingestion │ ├── faiss_index/ # Prebuilt FAISS index (generated from PDF) │ ├── frontend/ │ └── app.py # Streamlit UI │ ├── requirements.txt ├── .env.example └── README.md



---

## 🧩 Requirements

- Python 3.10+
- OpenAI API key (for GPT-based responses)
- Virtualenv recommended

---

## 🛠️ Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/yourname/immigration_bot.git
cd immigration_bot


2. Set Up Virtual Environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows


3. Install Dependencies
pip install -r requirements.txt


4. Set Up Environment Variables
Create a .env file:
cp .env_example .env

Edit the .env file and add your OpenAI key:
OPENAI_API_KEY=your-key-here


📥 (Optional) Regenerate FAISS Index
If you change the PDF or embeddings, regenerate the index:
python immigration_bot/backend/ingest_docs.py


▶️ Start the App
1. Run Backend (FastAPI)
uvicorn immigration_bot.backend.app:app --host=0.0.0.0 --port=10000


2. Run Frontend (Streamlit)
In a new terminal:
streamlit run immigration_bot/frontend/app.py


🌐 Access the App
Go to your browser:
http://localhost:8501

🧾 License

MIT License © 2025 Sujith Kumar Menon

🙏 Acknowledgements
LangChain
FAISS
Sentence Transformers
USCIS (PDF source)



---

Would you like me to drop this in your `immigration_bot/README.md` right away, or tweak anything (like your GitHub username or licensing)?



Absolutely! Here's a clean and detailed `README.md` you can drop at the root of your `job_finder_bot` folder or in the `AGS_Purdue` repo with usage instructions tailored for your project.

---

```markdown
# 🧠 H1B-Aware Job Matcher

A smart Streamlit app that parses resumes, dynamically generates job search queries based on your experience and skills, scrapes fresh job listings using SerpAPI, and returns the most relevant job opportunities — with H1B sponsor filtering included!

---

## 🚀 Features

- Upload your PDF resume and extract structured information.
- Automatically generate job search queries based on:
  - Your **designation**, **skills**, and **experience**
  - Context-aware extraction using LLMs (OpenAI)
- Fetch real-time job postings from Google Jobs using **SerpAPI**
- Match jobs to your profile using semantic similarity
- Filter by **H1B sponsoring companies**
- Export results to Excel and download
- Streamlit-powered UI

---

## 📁 Folder Structure

```bash
AGS_Purdue/
├── job_finder_bot/
│   ├── data/                    # H1B sponsor company list
│   ├── output/                  # Auto-generated job match results
│   ├── parsers/                 # Resume parsing logic
│   ├── scrapers/                # Indeed/SerpAPI scraping logic
│   ├── matcher/                 # Job matching logic
│   ├── utils/                   # Helpers and query generation
│   ├── streamlit_app.py         # 🎯 MAIN APP ENTRY POINT
│   ├── main.py                  # Optional CLI fallback
│   ├── .env.example             # 🔑 Sample environment variables
│   └── requirements.txt         # Python dependencies
```

---

## 🧪 Local Setup

### ✅ 1. Clone the repository

```bash
git clone https://github.com/smenon2710/AGS_Purdue.git
cd AGS_Purdue/job_finder_bot
```

---

### ✅ 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

---

### ✅ 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### ✅ 4. Setup `.env` file

Create a `.env` file in the `job_finder_bot/` directory based on the template:

```bash
cp .env.example .env
```

Edit `.env` and add your [SerpAPI Key](https://serpapi.com/manage-api-key):

```
SERPAPI_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional, only if GPT is used
```

---

### ✅ 5. Run the Streamlit app

```bash
streamlit run streamlit_app.py
```

The app will launch at:  
**http://localhost:8501**

---

## 📥 How It Works

1. Upload your resume (PDF)
2. Resume is parsed using custom logic and spaCy
3. Dynamic job queries are generated (optionally using GPT if OpenAI key is set)
4. SerpAPI fetches job listings from Google Jobs
5. Jobs are semantically matched to your profile
6. Filter for H1B jobs (checkbox)
7. View/download results

---

## 📌 Notes

- Output Excel files are saved in: `output/streamlit_jobs_output.xlsx`
- The H1B sponsor list is located at: `data/h1b_companies.txt`
- The `.env` file is required for API access; never commit it to GitHub
- Works best with resumes that include clear skill and role data

---

## 👨‍💻 Contributing

If you'd like to contribute:
- Fork this repo
- Create a new branch
- Open a pull request!

---

## 🛡 License

MIT License — feel free to use, fork, and build on top of it!

---

## 🤝 Author

Made with 💻 by [Sujith Menon](https://github.com/smenon2710)
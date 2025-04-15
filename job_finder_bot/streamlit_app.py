import streamlit as st
import pandas as pd
import tempfile
import os
from parsers.resume_parser import parse_resume
from scrapers.serpapi_scraper import get_jobs_from_serpapi
from matcher.job_matcher import match_jobs
from utils.query_generator import generate_search_queries

from dotenv import load_dotenv
# 👇 Load .env from job_finder_bot directory
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
SERPAPI_API_KEY = os.getenv("SERP_API_KEY")



# Config

H1B_COMPANIES_FILE = os.path.join(os.path.dirname(__file__), "data/h1b_companies.txt")
#H1B_COMPANIES_FILE = "data/h1b_companies.txt"


# === Helper Functions ===
def load_h1b_companies(filepath):
    with open(filepath, "r") as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

def is_from_h1b_sponsor(company, sponsor_list):
    if not company:
        return False
    return any(sponsor in company.lower() for sponsor in sponsor_list)

# === Streamlit App ===
st.set_page_config(page_title="Job Matcher", layout="wide")
st.title("💼 H1B-Aware Job Matcher")

# Sidebar Controls
threshold = st.sidebar.slider("Match Score Threshold", 0.3, 1.0, 0.6, 0.05)
max_results = st.sidebar.slider("Max Jobs to Show", 5, 50, 25, 5)
enable_h1b_filter = st.sidebar.checkbox("Only show H1B sponsor jobs", value=True)

# Upload Resume
uploaded_file = st.file_uploader("📄 Upload your resume", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    parsed = parse_resume(tmp_path)

    st.markdown("### 🧾 Parsed Resume:")
    st.markdown(f"**Skills:** {', '.join(parsed['skills'])}")
    st.markdown("**Experience:**")
    st.json(parsed['experience'])

    with st.spinner("🔍 Scraping jobs and matching..."):
        #queries = ["Tableau", "Power BI", "Data Visualization", "Business Intelligence", "ETL", "Automation", "BI", "Analytics"]
        queries = generate_search_queries(parsed)
        st.markdown(f"**Generated Job Search Queries:** {', '.join(queries)}")
        all_jobs = []
        for query in queries:
            jobs = get_jobs_from_serpapi(query + " jobs", api_key=SERPAPI_API_KEY, limit=10)
            all_jobs.extend(jobs)

        context_text = "\n".join([
            " ".join(parsed.get("skills", [])),
            " ".join(parsed.get("experience", [])),
            " ".join(parsed.get("designation") if isinstance(parsed.get("designation"), list) else [str(parsed.get("designation"))]),
        ])

        matched_jobs = match_jobs(context_text, all_jobs, threshold=threshold)

        if enable_h1b_filter:
            h1b_companies = load_h1b_companies(H1B_COMPANIES_FILE)
            matched_jobs = [job for job in matched_jobs if is_from_h1b_sponsor(job.get("company", ""), h1b_companies)]

        if matched_jobs:
            df = pd.DataFrame(matched_jobs)
            df = df.head(max_results)
            st.success(f"✅ {len(df)} job(s) matched!")
            st.dataframe(df[["title", "company", "location", "link", "match_score"]])

            # ✅ Save to Excel file
            output_file = os.path.join("job_finder_bot", "output", "streamlit_jobs_output.xlsx")
            df.to_excel(output_file, index=False)
            st.success(f"📥 Jobs exported to: `{output_file}`")

            # ✅ Add download button
            from io import BytesIO
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            st.download_button("⬇️ Download matched jobs as Excel", data=buffer, file_name="matched_jobs.xlsx")
        else:
            st.warning("⚠️ No jobs matched your filters.")

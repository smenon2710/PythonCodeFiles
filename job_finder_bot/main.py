


from parsers.resume_parser import parse_resume
from scrapers.serpapi_scraper import get_jobs_from_serpapi
from matcher.job_matcher import match_jobs
import pandas as pd
import yagmail
import os

# 🔐 Config
# 🔑 Your SerpAPI and email settings
# SERP_API_KEY = "SERP_API_KEY"
# EMAIL_SENDER = "sender_email@gmail.com"
# EMAIL_PASSWORD = "sender_password"
# EMAIL_RECEIVER = "receiver_email@gmail.com"
# RESUME_PATH = "job_finder_bot/data/resume.pdf"
H1B_COMPANIES_FILE = "job_finder_bot/data/h1b_companies.txt"

MATCH_THRESHOLD = 0.35
MAX_EMAIL_JOBS = 25

def load_h1b_companies(filepath):
    with open(filepath, "r") as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

def is_from_h1b_sponsor(company, sponsor_list):
    company = company.lower()
    return any(sponsor in company for sponsor in sponsor_list)

def send_email_notification(jobs, total_count, excluded_count):
    subject = f"🔥 {len(jobs)} H1B-Eligible BI Jobs (of {total_count})"
    rows = ""
    for job in jobs[:MAX_EMAIL_JOBS]:
        rows += f"""
        <tr>
            <td>{round(job['match_score'] * 100)}%</td>
            <td>{job['title']}</td>
            <td>{job['company']}</td>
            <td>{job['location']}</td>
            <td><a href="{job['link']}">Apply</a></td>
        </tr>
        """

    html_content = f"""
    <h2>Matched Job Opportunities (Filtered for H1B Sponsor Companies)</h2>
    <p>Showing top {min(MAX_EMAIL_JOBS, len(jobs))} of {total_count} matched jobs.</p>
    <p>Excluded due to H1B sponsor mismatch: {excluded_count}</p>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr style="background-color:#f2f2f2;">
            <th>Match %</th>
            <th>Title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Link</th>
        </tr>
        {rows}
    </table>
    """

    yag = yagmail.SMTP(EMAIL_SENDER, EMAIL_PASSWORD)
    yag.send(to=EMAIL_RECEIVER, subject=subject, contents=html_content)
    print("📧 Email sent successfully!")

if __name__ == "__main__":
    parsed = parse_resume(RESUME_PATH)
    print("\n🧾 Parsed Resume:")
    print(f"Skills: {parsed['skills']}")
    print(f"Experience: {parsed['experience']}")
    print(f"Education: {parsed['education']}")

    focus_keywords = [
        "Tableau", "Power BI", "Data Visualization", "Business Intelligence", "ETL", "Automation"
    ]
    queries = [f"{kw} jobs" for kw in focus_keywords]

    all_jobs = []
    for q in queries:
        print(f"\n🔍 Searching: {q}")
        jobs = get_jobs_from_serpapi(q, api_key=SERP_API_KEY, limit=10)
        all_jobs.extend(jobs)

    print(f"\n✅ Total jobs scraped: {len(all_jobs)}")

    context_text = (
        parsed.get("raw_text", "") +
        " " + " ".join(parsed.get("skills") or []) +
        " " + " ".join(parsed.get("experience") or []) +
        " " + " ".join(parsed.get("designation") or [])
    )

    matched = match_jobs(context_text, all_jobs, threshold=MATCH_THRESHOLD)

    # H1B Filtering
    h1b_companies = load_h1b_companies(H1B_COMPANIES_FILE)
    matched_h1b = [job for job in matched if is_from_h1b_sponsor(job.get("company", ""), h1b_companies)]
    excluded_h1b = [job for job in matched if not is_from_h1b_sponsor(job.get("company", ""), h1b_companies)]

    # Save to files
    os.makedirs("job_finder_bot/output", exist_ok=True)
    pd.DataFrame(matched_h1b).to_excel("job_finder_bot/output/matched_jobs.xlsx", index=False)
    pd.DataFrame(excluded_h1b).to_excel("job_finder_bot/output/excluded_jobs.xlsx", index=False)

    # Debug: show excluded companies
    if excluded_h1b:
        print("\n❌ Excluded (H1B mismatch):")
        for job in excluded_h1b:
            print(f" - {job['company']}")

    if matched_h1b:
        send_email_notification(matched_h1b, len(matched), len(excluded_h1b))
    else:
        print("\n⚠️ No H1B-eligible matched jobs found.")

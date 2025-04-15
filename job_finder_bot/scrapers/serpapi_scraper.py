from serpapi import GoogleSearch

def get_jobs_from_serpapi(query, api_key, limit=10):
    search = GoogleSearch({
        "q": query,
        "engine": "google_jobs",
        "hl": "en",
        "api_key": api_key,
        "tbs": "qdr:d3"  # ✅ Jobs from the last 3 days
    })

    results = search.get_dict()
    if not results.get("jobs_results"):
        print(f"⚠️ No results for query: {query}")
        print(f"🧾 SerpAPI response: {results.get('error', 'No error reported')}")
        return []

    jobs = []
    for job in results.get("jobs_results", [])[:limit]:
        jobs.append({
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("location"),
            "link": job.get("related_links", [{}])[0].get("link", job.get("apply_options", [{}])[0].get("link", "")),
            "description": job.get("description", "")
        })

    return jobs

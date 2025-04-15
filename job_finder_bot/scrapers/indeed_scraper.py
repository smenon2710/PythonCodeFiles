import requests
from bs4 import BeautifulSoup

def get_indeed_jobs(query, location, limit=10):
    base_url = "https://www.indeed.com/jobs"
    params = {
        "q": query,
        "l": location,
        "limit": limit
    }

    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.text, "html.parser")

    job_cards = soup.find_all("a", class_="tapItem", limit=limit)
    jobs = []

    for card in job_cards:
        title_elem = card.find("h2", class_="jobTitle")
        company_elem = card.find("span", class_="companyName")
        location_elem = card.find("div", class_="companyLocation")
        link = "https://www.indeed.com" + card.get("href")

        jobs.append({
            "title": title_elem.text.strip() if title_elem else None,
            "company": company_elem.text.strip() if company_elem else None,
            "location": location_elem.text.strip() if location_elem else None,
            "link": link
        })

    return jobs

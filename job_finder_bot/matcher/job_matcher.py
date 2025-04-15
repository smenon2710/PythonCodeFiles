from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def match_jobs(resume_text, jobs, threshold=0.6):
    resume_vec = model.encode([resume_text])
    matched_jobs = []

    for job in jobs:
        job_text = f"{job['title']} {job['company']} {job['location']} {job.get('description', '')}"
        job_vec = model.encode([job_text])

        score = cosine_similarity(resume_vec, job_vec)[0][0]
        print(f"Match Score ({score:.2f}) -> {job['title']} @ {job['company']}")

        if score >= threshold:
            job['match_score'] = round(score, 2)
            matched_jobs.append(job)

    return matched_jobs

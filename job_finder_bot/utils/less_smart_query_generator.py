import re
from collections import Counter
import spacy

nlp = spacy.load("en_core_web_sm")

def generate_search_queries(parsed):
    search_terms = []

    # Add designations
    designation = parsed.get("designation")
    if isinstance(designation, list):
        search_terms.extend(designation)
    elif isinstance(designation, str):
        search_terms.append(designation)

    # Add skills
    search_terms.extend(parsed.get("skills", []))

    # Extract top noun chunks from experience
    experience_text = " ".join(parsed.get("experience", []))
    doc = nlp(experience_text)
    noun_chunks = [chunk.text.strip() for chunk in doc.noun_chunks if len(chunk.text.strip()) > 2]
    top_chunks = Counter(noun_chunks).most_common(10)
    search_terms.extend([term for term, _ in top_chunks])

    # Clean and deduplicate
    search_terms = [re.sub(r"[^a-zA-Z0-9\s]", "", s).strip() for s in search_terms if len(s.strip()) >= 3]
    return list(set(search_terms))[:8]  # Return top 8 unique queries

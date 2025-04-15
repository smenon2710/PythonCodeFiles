from pyresparser import ResumeParser

def parse_resume(file_path):
    parsed = ResumeParser(file_path).get_extracted_data()
    return {
        "skills": parsed.get("skills") or [],
        "experience": parsed.get("experience") or [],
        "education": parsed.get("education") or [],
        "designation": parsed.get("designation") or [],
        "raw_text": (
            (parsed.get("name") or "") + " " +
            " ".join(parsed.get("skills") or []) + " " +
            " ".join(parsed.get("experience") or []) + " " +
            " ".join(parsed.get("designation") or [])
        )
    }


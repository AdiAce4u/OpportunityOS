from app.tools.mock_jobs import search_jobs

def search_many(queries: list[str]) -> list[dict]:
    unique = {}
    for query in queries:
        for job in search_jobs(query):
            unique[job["external_id"]] = job
    return list(unique.values())

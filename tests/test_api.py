"""Tests run against the running stack (docker compose up).

Run inside the api container or locally with DATABASE_URL pointing at the db:
    pytest tests/
"""

import httpx

BASE = "http://localhost:8000"


def test_health():
    r = httpx.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_search():
    # Create a document
    r = httpx.post(
        f"{BASE}/api/documents",
        json={"title": "Kubernetes", "content": "Kubernetes orchestrates containers across a cluster of machines."},
    )
    assert r.status_code == 201
    doc_id = r.json()["id"]

    # It should surface for a semantically related query
    r = httpx.get(f"{BASE}/api/search", params={"q": "container orchestration cluster", "top_k": 3})
    assert r.status_code == 200
    titles = [res["title"] for res in r.json()["results"]]
    assert "Kubernetes" in titles

    # Scores are valid similarities
    assert all(0 <= res["score"] <= 1 for res in r.json()["results"])

    # Cleanup
    httpx.delete(f"{BASE}/api/documents/{doc_id}")


def test_search_ranking():
    """Closer matches should rank higher than unrelated ones."""
    r = httpx.get(f"{BASE}/api/search", params={"q": "store embeddings nearest neighbor", "top_k": 5})
    results = r.json()["results"]
    assert results[0]["score"] >= results[-1]["score"]

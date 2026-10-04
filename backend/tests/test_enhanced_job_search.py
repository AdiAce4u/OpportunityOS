import pytest
from app.tools.portal_search_engine import (
    search_live_portals,
    ROLE_CATEGORIES,
    build_portal_search_url,
    CompensationParser,
    CVProjectMatcher,
    ATSCrawler
)

def test_portal_search_url_builder():
    url = build_portal_search_url("linkedin", "Software Engineer", "Google", "Bangalore")
    assert "https://www.linkedin.com/jobs/search/?" in url
    assert "Software%20Engineer%20Google" in url or "Software+Engineer+Google" in url or "Software" in url

    indeed_url = build_portal_search_url("indeed", "ML Engineer", "NVIDIA", "India")
    assert "https://in.indeed.com/jobs?" in indeed_url

    glassdoor_url = build_portal_search_url("glassdoor", "Quantitative Analyst", "WorldQuant", "Mumbai")
    assert "https://www.glassdoor.co.in/Job/jobs.htm?" in glassdoor_url

def test_search_live_portals_all_tracks():
    tracks = ["software", "data", "consult", "finance", "core"]
    sample_projects = [
        {
            "name": "Autonomous Navigation Robot",
            "domain": "core",
            "description": "Built ROS2 robot with LiDAR and SLAM",
            "bullets": ["Implemented Pure Pursuit and obstacle avoidance"],
            "full_text": "Autonomous Navigation Robot ROS2 LiDAR SLAM Pure Pursuit Python C++"
        },
        {
            "name": "Skin Lesion Classifier",
            "domain": "data",
            "description": "Deep learning PyTorch model for medical imaging",
            "bullets": ["Trained CNN with 94% accuracy"],
            "full_text": "Skin Lesion Classifier PyTorch Deep Learning CNN Transformers"
        }
    ]

    for track in tracks:
        results = search_live_portals(
            search_term="",
            location="India",
            category=track,
            results_wanted=10,
            candidate_projects=sample_projects
        )
        assert len(results) > 0, f"Expected jobs for track {track}"

        # Verify link validity
        for j in results:
            url = j.get("job_url", "")
            assert url.startswith("http"), f"Job URL should be valid http: {url}"
            # Ensure no fake stub URLs
            assert not any(p in url for p in ["/uber-", "/swiggy-", "/razorpay-", "/xyz-robotics-", "/tower-research-"]), \
                f"Found invalid fake stub URL: {url}"
            assert j.get("match_score", 0) > 0

def test_ats_crawler_live():
    # Test that ATSCrawler returns well-structured job dicts
    jobs = ATSCrawler.fetch_live_category_jobs("sde", max_jobs=3)
    assert isinstance(jobs, list)
    if jobs:
        j = jobs[0]
        assert "title" in j
        assert "company" in j
        assert j.get("job_url", "").startswith("http")

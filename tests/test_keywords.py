from job_aggregator.main import match_keywords

def test_match_keywords_positive():
    text = "Senior Data Analyst with Python experience"
    keywords = ["data", "python"]
    assert match_keywords(text, keywords)

def test_match_keywords_negative():
    text = "Marketing Manager"
    keywords = ["data", "python"]
    assert not match_keywords(text, keywords)
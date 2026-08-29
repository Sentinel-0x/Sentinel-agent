import pytest
from job_agent import quick_filter

def test_quick_filter_restricted_location():
    # 测试限制地区（USA）是否能被成功拦截
    job = {"title": "AI Operations Specialist", "location": "USA Only"}
    passed, reason = quick_filter(job)
    assert passed is False
    assert "限制地区" in reason

def test_quick_filter_unwanted_role():
    # 测试排除职位（Engineer）是否能被成功拦截
    job = {"title": "Senior Backend Engineer", "location": "Remote"}
    passed, reason = quick_filter(job)
    assert passed is False
    assert "非目标岗位" in reason

def test_quick_filter_valid_job():
    # 测试符合条件的岗位是否能顺利通过粗筛
    job = {"title": "AI Solutions Specialist", "location": "Worldwide Remote"}
    passed, reason = quick_filter(job)
    assert passed is True
    assert reason == "通过粗筛"

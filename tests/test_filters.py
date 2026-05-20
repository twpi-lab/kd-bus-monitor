"""filters.py 단위 테스트"""
import pytest
from filters import match_keywords, urgency_tag, _kw_in


class TestKwIn:
    def test_korean_exact(self):
        assert _kw_in("버스", "시내버스 운행") is True

    def test_korean_miss(self):
        assert _kw_in("택시", "시내버스 운행") is False

    def test_english_case_insensitive(self):
        assert _kw_in("DRT", "drt 수요응답형") is True
        assert _kw_in("MaaS", "maas 플랫폼") is True

    def test_english_miss(self):
        assert _kw_in("DRT", "버스 입찰") is False


class TestMatchKeywords:
    def test_exclude_first(self):
        """제외 키워드가 있으면 버스+입찰이 있어도 비매칭"""
        is_match, _, _ = match_keywords("버스 입찰공고 승강장 설치")
        assert is_match is False

    def test_school_bus_standalone(self):
        """통학버스는 입찰/정책 키워드 없이도 단독 매칭"""
        is_match, bus, tender = match_keywords("통학버스 안전점검 안내")
        assert is_match is True
        assert "통학버스" in bus
        assert tender == ["통학버스단독"]

    def test_bus_and_tender(self):
        is_match, bus, tender = match_keywords("시내버스 노선 입찰공고")
        assert is_match is True
        assert any("버스" in k for k in bus)
        assert any("입찰" in k for k in tender)

    def test_bus_and_policy(self):
        is_match, bus, policy = match_keywords("버스 노선 개편 안내")
        assert is_match is True
        assert any("버스" in k for k in bus)
        assert any("개편" in k for k in policy)

    def test_no_match_bus_only(self):
        """버스 키워드만 있고 입찰/정책 없으면 비매칭"""
        is_match, _, _ = match_keywords("버스 시간표 변경")
        assert is_match is False

    def test_no_match_empty(self):
        is_match, _, _ = match_keywords("")
        assert is_match is False


class TestUrgencyTag:
    def test_urgent_keyword(self):
        assert urgency_tag("긴급 입찰공고") == "🚨 긴급 "

    def test_d_minus_3(self):
        assert urgency_tag("마감 D-3 입찰") == "🚨 긴급 "

    def test_d_minus_10_not_urgent(self):
        assert urgency_tag("마감 D-10 입찰") == ""

    def test_normal(self):
        assert urgency_tag("일반 공고") == ""

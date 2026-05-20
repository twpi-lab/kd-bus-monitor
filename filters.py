"""
키워드 매칭 + 긴급도 태그
"""
import re

from config import BUS_KEYWORDS, TENDER_KEYWORDS, EXCLUDE_KEYWORDS, POLICY_KEYWORDS, SCHOOL_BUS_KEYWORDS


def _kw_in(kw: str, text: str) -> bool:
    """키워드 포함 검사. 영문 포함 키워드는 대소문자 무시."""
    if any(c.isascii() and c.isalpha() for c in kw):
        return kw.lower() in text.lower()
    return kw in text


def match_keywords(title: str):
    """매칭 규칙 (제외 키워드 우선, 통학버스는 단독 매칭):
    0) 제외 키워드 포함 → 즉시 비매칭
    1) 통학버스 키워드 → 단독 매칭 (입찰/정책 키워드 없어도 OK)
    2) 버스 키워드 AND 입찰 키워드 → 매칭
    3) 버스 키워드 AND 정책 키워드 → 매칭
    """
    t = title or ""
    for ex in EXCLUDE_KEYWORDS:
        if _kw_in(ex, t):
            return (False, [], [])
    school = [kw for kw in SCHOOL_BUS_KEYWORDS if _kw_in(kw, t)]
    if school:
        return (True, school, ["통학버스단독"])
    bus    = [kw for kw in BUS_KEYWORDS    if _kw_in(kw, t)]
    tender = [kw for kw in TENDER_KEYWORDS if _kw_in(kw, t)]
    if bus and tender:
        return (True, bus, tender)
    policy = [kw for kw in POLICY_KEYWORDS if _kw_in(kw, t)]
    if bus and policy:
        return (True, bus, policy)
    return (False, [], [])


def urgency_tag(title: str) -> str:
    """긴급 키워드 또는 D-7 이내면 🚨 표시"""
    for w in ["긴급", "즉시", "당일"]:
        if w in title:
            return "🚨 긴급 "
    m = re.search(r"D-(\d+)", title)
    if m and int(m.group(1)) <= 7:
        return "🚨 긴급 "
    return ""

"""collectors/tenders.py 헬퍼 함수 단위 테스트"""
import pytest
from bs4 import BeautifulSoup
from collectors.tenders import (
    make_id,
    abs_link,
    extract_date,
    extract_idx,
    parse_default,
    fetch_notices,
)


class TestMakeId:
    def test_query_param_idx(self):
        link = "https://example.com/view?idx=12345"
        result = make_id("사이트A", link, "제목", "2026-01-01")
        assert result == "사이트A|idx=12345"

    def test_query_param_nttNo(self):
        link = "https://example.com/view?nttNo=999"
        result = make_id("사이트B", link, "제목", "2026-01-01")
        assert result == "사이트B|nttNo=999"

    def test_fallback_title_date(self):
        link = "https://example.com/view"
        result = make_id("사이트C", link, "아주 긴 제목입니다", "2026-01-01")
        assert result == "사이트C|아주 긴 제목입니다|2026-01-01"

    def test_empty_link(self):
        result = make_id("사이트D", "", "제목", "2026-05-20")
        assert result == "사이트D|제목|2026-05-20"


class TestAbsLink:
    def test_relative_path(self):
        assert abs_link("/board/view.do?id=1", "https://example.com") == \
            "https://example.com/board/view.do?id=1"

    def test_dot_relative(self):
        assert abs_link("./view.do", "https://example.com/board") == \
            "https://example.com/board/view.do"

    def test_absolute_url(self):
        assert abs_link("https://other.com/page", "https://example.com") == \
            "https://other.com/page"

    def test_javascript_void(self):
        assert abs_link("javascript:void(0)", "https://example.com") == ""

    def test_empty(self):
        assert abs_link("", "https://example.com") == ""

    def test_hash(self):
        assert abs_link("#", "https://example.com") == ""


class TestExtractDate:
    def test_date_with_dots(self):
        html = '<tr><td>공고</td><td>2026.05.20</td></tr>'
        row = BeautifulSoup(html, "html.parser").select_one("tr")
        assert extract_date(row) == "2026.05.20"

    def test_date_with_dashes(self):
        html = '<tr><td>공고</td><td>2026-05-20</td></tr>'
        row = BeautifulSoup(html, "html.parser").select_one("tr")
        assert extract_date(row) == "2026-05-20"

    def test_date_with_slashes(self):
        html = '<tr><td>공고</td><td>등록일 : 2026/05/15</td></tr>'
        row = BeautifulSoup(html, "html.parser").select_one("tr")
        assert extract_date(row) == "2026/05/15"

    def test_date_class(self):
        html = '<tr><td class="date">2026.01.01</td><td>기타</td></tr>'
        row = BeautifulSoup(html, "html.parser").select_one("tr")
        assert extract_date(row) == "2026.01.01"

    def test_no_date(self):
        html = '<tr><td>공고</td><td>조회수 123</td></tr>'
        row = BeautifulSoup(html, "html.parser").select_one("tr")
        assert extract_date(row) == ""


class TestExtractIdx:
    def test_idx_equals(self):
        html = '<tr><a onclick="view(idx=12345)">제목</a></tr>'
        soup = BeautifulSoup(html, "html.parser")
        row = soup.select_one("tr")
        tag = soup.select_one("a")
        assert extract_idx(row, tag) == "12345"

    def test_fn_pattern(self):
        html = '<tr><a onclick="fn_detail(\'99887\')">제목</a></tr>'
        soup = BeautifulSoup(html, "html.parser")
        row = soup.select_one("tr")
        tag = soup.select_one("a")
        assert extract_idx(row, tag) == "99887"

    def test_no_idx(self):
        html = '<tr><a href="/list">제목</a></tr>'
        soup = BeautifulSoup(html, "html.parser")
        row = soup.select_one("tr")
        tag = soup.select_one("a")
        assert extract_idx(row, tag) == ""


class TestParseDefault:
    def test_basic_table(self):
        html = """
        <table><tbody>
            <tr>
                <td class="subject"><a href="/view?idx=1">버스 입찰공고</a></td>
                <td>2026.05.20</td>
            </tr>
            <tr>
                <td class="subject"><a href="/view?idx=2">도로 공사</a></td>
                <td>2026.05.19</td>
            </tr>
        </tbody></table>
        """
        soup = BeautifulSoup(html, "html.parser")
        site = {"name": "테스트", "url": "https://example.com/list", "base": "https://example.com"}
        notices = parse_default(soup, site)
        assert len(notices) == 2
        assert notices[0]["title"] == "버스 입찰공고"
        assert "idx=1" in notices[0]["id"]

    def test_empty_table(self):
        html = "<table><tbody></tbody></table>"
        soup = BeautifulSoup(html, "html.parser")
        site = {"name": "테스트", "url": "https://example.com", "base": "https://example.com"}
        assert parse_default(soup, site) == []


class TestFetchNoticesRetry:
    def test_site_retry_settings_control_attempts_and_backoff(self, monkeypatch):
        calls = []
        sleeps = []

        class FakeResponse:
            text = """
            <table><tbody>
                <tr>
                    <td class="subject"><a href="/view?idx=1">버스 입찰공고</a></td>
                    <td>2026.05.20</td>
                </tr>
            </tbody></table>
            """
            encoding = ""

            def raise_for_status(self):
                return None

        def fake_get(*args, **kwargs):
            calls.append(kwargs)
            if len(calls) < 3:
                raise TimeoutError("temporary timeout")
            return FakeResponse()

        monkeypatch.setattr("collectors.tenders.requests.get", fake_get)
        monkeypatch.setattr("collectors.tenders.time.sleep", lambda seconds: sleeps.append(seconds))

        site = {
            "name": "의정부시 고시공고",
            "url": "https://www.ui4u.go.kr/portal/saeol/gosiList.do",
            "base": "https://www.ui4u.go.kr/portal/saeol",
            "ssl": True,
            "parser": "default",
            "max_try": 3,
            "retry_delay": 1,
            "retry_backoff": 2,
        }

        notices = fetch_notices(site)

        assert len(notices) == 1
        assert notices[0]["title"] == "버스 입찰공고"
        assert len(calls) == 3
        assert sleeps == [1, 2]
        assert all(call["timeout"] == 25 for call in calls)
        assert all(call["verify"] is True for call in calls)

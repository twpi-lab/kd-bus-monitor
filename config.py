"""
설정값 모음 (키워드 / 사이트 / 토큰 / 경로)
"""
import os
from pathlib import Path

# ────────────────────────────────────────────────
#  .env 파일 자동 로드 (로컬 실행용; GitHub Actions에서는 Secrets가 사용됨)
# ────────────────────────────────────────────────
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# ────────────────────────────────────────────────
#  텔레그램 (환경변수 또는 .env 파일에서만 로드, 코드에는 토큰 저장 금지)
# ────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
ALERT_TIME = "07:00"

# ────────────────────────────────────────────────
#  데이터 저장 경로 (모듈 디렉토리 기준 ./state)
# ────────────────────────────────────────────────
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
os.makedirs(BASE_DIR, exist_ok=True)

ALL_FILE  = os.path.join(BASE_DIR, "all_notices.json")
SENT_FILE = os.path.join(BASE_DIR, "sent_ids.json")
LOG_FILE  = os.path.join(BASE_DIR, "alert_log.txt")

# ────────────────────────────────────────────────
#  HTTP 헤더 (사이트별 헤더는 MONITOR_URLS에서 병합)
# ────────────────────────────────────────────────
BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}

# ────────────────────────────────────────────────
#  키워드
# ────────────────────────────────────────────────
BUS_KEYWORDS = [
    # 기본 버스·노선
    "버스", "시내버스", "마을버스", "광역버스", "공공버스",
    "급행버스", "직행버스", "심야버스", "순환버스",
    "통학버스", "통학차량", "전세버스",
    "노선", "노선입찰", "노선 운행", "노선 개편",
    "운송", "운행", "운수", "대중교통", "교통체계",
    "운송사업자", "운수업체", "운송업체", "버스업체",
    "준공영제", "공공관리제", "재정지원",
    # DRT·수요응답형
    "DRT", "디알티", "수요응답형", "수요응답버스", "수요응답교통", "똑버스",
    "셔틀", "셔틀버스",
    # 자율주행·스마트 모빌리티
    "자율주행", "자율 주행", "자율버스", "자율주행버스",
    "자율운행", "무인운행",
    "모빌리티", "스마트모빌리티", "MaaS",
    # 데이터
    "교통데이터", "운행데이터", "운행기록",
]

TENDER_KEYWORDS = [
    "입찰", "입찰공고", "전자입찰", "재입찰",
    "용역", "위탁", "위탁운행", "임차",
    "경쟁입찰", "제한경쟁", "일반경쟁", "수의계약",
    "사업자 선정", "사업자선정", "업체 선정", "업체선정",
    "모집공고", "운영사 모집", "사업자 모집", "사업공고", "사업 공고", "모집 공고",
    "협상에 의한 계약", "견적제출",
    "시범사업", "실증사업", "파일럿",
]

EXCLUDE_KEYWORDS = [
    "승강장", "정류장 설치", "도로 포장", "가로등",
    "청소", "환경미화", "낙찰결과", "인사발령",
    "취소공고", "유찰공고", "폐지공고",
    # 노이즈 패턴 5개 (D2 확정)
    "설명자료", "Q&A",                          # B. 부속자료
    "ITS", "정산시스템", "감리용역",              # C. IT/감리 용역
    "창업지원", "입주기업",                      # D. 창업지원
    "CS센터", "콜센터 운영",                     # E. CS·운영
    "차량 구매", "차량(7m",                      # G. 차량 구매
]

# 통학버스 강화 키워드 (단독 매칭 — TENDER/POLICY 없이도 알림)
SCHOOL_BUS_KEYWORDS = [
    "통학버스", "통학차량", "통학 차량",
    "스쿨버스",
    "학원버스",
    "어린이통학", "어린이 통학",
    "원아통학", "원아 통학",
    "학생수송", "학생 수송",
    "학생전용", "학생 전용",
    "포춘버스", "포츈버스",  # 포천형 학생전용 통학버스 브랜드
]

# 정책/노선 키워드: 입찰 키워드 없어도 버스 키워드 1개 이상과 함께 등장하면 매칭
POLICY_KEYWORDS = [
    "노선 신설", "노선신설", "노선 변경", "노선변경",
    "노선 개편", "노선개편", "노선 폐지", "노선폐지",
    "신규노선", "신규 노선",
    "준공영제", "공공관리제",
    "재정지원", "광역교통", "보도자료",
]

# ────────────────────────────────────────────────
#  모니터링 사이트 (15곳)
# ────────────────────────────────────────────────
MONITOR_URLS = [
    {
        "name":   "양주시 고시공고",
        "url":    "https://www.yangju.go.kr/www/selectEminwonList.do?key=4075",
        "base":   "https://www.yangju.go.kr/www",
        "ssl":    True,
        "parser": "default",
    },
    {
        "name":   "양주시 입찰공고",
        "url":    "https://www.yangju.go.kr/www/selectBbsNttList.do?bbsNo=13&key=212",
        "base":   "https://www.yangju.go.kr/www",
        "ssl":    True,
        "parser": "default",
    },
    {
        "name":       "대광위 공지사항",
        "url":        "https://www.molit.go.kr/mtc/USR/BORD0201/m_36761/BRD.jsp",
        "base":       "https://www.molit.go.kr",
        "ssl":        True,
        "parser":     "molit",
        "detail_url": "https://www.molit.go.kr/mtc/USR/BORD0201/m_36761/DTL.jsp?id=mta_017&mode=view&idx={idx}",
        "extra_headers": {
            "Referer":         "https://www.molit.go.kr/mtc/",
            "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9",
        },
    },
    {
        "name":       "의정부시 고시공고",
        "url":        "https://www.ui4u.go.kr/portal/saeol/gosiList.do?seCode=01&mId=0301040000",
        "base":       "https://www.ui4u.go.kr/portal/saeol",
        "ssl":        False,
        "parser":     "default",
        "detail_url": "https://www.ui4u.go.kr/portal/saeol/gosiView.do?notAncmtMgtNo={idx}&mId=0301040000",
    },
    {
        "name":   "경기도 고시공고",
        "url":    "https://www.gg.go.kr/bbs/board.do?bsIdx=469&menuId=1547",
        "base":   "https://www.gg.go.kr",
        "ssl":    True,
        "parser": "playwright",
    },
    {
        "name":       "경기교통공사 공지사항",
        "url":        "https://www.gtrans.or.kr/web/lay1/bbs/S1T392C310/A/1/list.do",
        "base":       "https://www.gtrans.or.kr",
        "ssl":        True,
        "parser":     "gtrans",
        "detail_url": "https://www.gtrans.or.kr/web/lay1/bbs/S1T392C310/A/1/view.do?article_seq={seq}",
        "extra_headers": {
            "Referer": "https://www.gtrans.or.kr/",
        },
    },
    {
        "name":       "경기교통공사 입찰공고",
        "url":        "https://www.gtrans.or.kr/web/lay1/bbs/S1T400C540/A/17/list.do",
        "base":       "https://www.gtrans.or.kr",
        "ssl":        True,
        "parser":     "gtrans",
        "detail_url": "https://www.gtrans.or.kr/web/lay1/bbs/S1T400C540/A/17/view.do?article_seq={seq}",
        "extra_headers": {
            "Referer": "https://www.gtrans.or.kr/",
        },
    },
    # ──────── 경기북부 시군 8곳 (Phase C) ────────
    {
        "name":   "동두천시 고시공고",
        "url":    "https://www.ddc.go.kr/ddc/selectGosiList.do?key=340&not_ancmt_se_code=04",
        "base":   "https://www.ddc.go.kr/ddc",
        "ssl":    True,
        "parser": "default",
    },
    {
        "name":   "포천시 새소식",
        "url":    "https://www.pocheon.go.kr/www/selectBbsNttList.do?bbsNo=18&key=3095",
        "base":   "https://www.pocheon.go.kr/www",
        "ssl":    True,
        "parser": "default",
    },
    {
        "name":   "연천군 고시공고",
        "url":    "https://www.yeoncheon.go.kr/www/selectGosiList.do?key=3393&not_ancmt_se_code=01",
        "base":   "https://www.yeoncheon.go.kr/www",
        "ssl":    True,
        "parser": "default",
    },
    {
        "name":   "고양시 고시공고",
        "url":    "https://eminwon.goyang.go.kr/emwp/gov/mogaha/ntis/web/ofr/action/OfrAction.do?jndinm=OfrNotAncmtEJB&context=NTIS&method=selectListOfrNotAncmt&methodnm=selectListOfrNotAncmtHomepage&homepage_pbs_yn=Y&subCheck=Y&ofr_pageSize=10&not_ancmt_se_code=01,04,05&title=%EA%B3%A0%EC%8B%9C%EA%B3%B5%EA%B3%A0&initValue=Y&countYn=Y&epcCheck=Y",
        "base":   "https://eminwon.goyang.go.kr",
        "ssl":    True,
        "parser": "default",
    },
    {
        "name":   "파주시 고시공고",
        "url":    "https://www.paju.go.kr/user/board/BD_board.list.do?bbsCd=1022&q_ctgCd=4063",
        "base":   "https://www.paju.go.kr",
        "ssl":    True,
        "parser": "default",
    },
    {
        "name":   "남양주시 고시공고",
        "url":    "https://www.nyj.go.kr/www/selectEminwonWebList.do?key=2492",
        "base":   "https://www.nyj.go.kr/www",
        "ssl":    True,
        "parser": "default",
    },
    {
        "name":   "구리시 고시공고",
        "url":    "https://www.guri.go.kr/www/sub.do?key=387",
        "base":   "https://www.guri.go.kr/www",
        "ssl":    True,
        "parser": "default",
    },
    {
        "name":   "가평군 고시공고",
        "url":    "https://www.gp.go.kr/portal/selectGosiList.do?key=2148&not_ancmt_se_code=01",
        "base":   "https://www.gp.go.kr/portal",
        "ssl":    True,
        "parser": "default",
    },
]

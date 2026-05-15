"""
텔레그램 발송
- send_telegram(message): 단건 (호환용)
- send_batch(items, now_str): 묶음 발송 (긴급/일반 분류, 4000자 분할)
"""
import time
import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from storage import write_log


TELEGRAM_MSG_LIMIT = 4000  # 텔레그램 4096 한도, 여유 96자


def send_telegram(message: str) -> bool:
    """단건 발송. 실패 시 최대 3회 재시도, 타임아웃 30초."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    for attempt in range(1, 4):
        try:
            res = requests.post(url, data=payload, timeout=30)
            if res.status_code == 200:
                print("  ✅ 텔레그램 전송 성공!")
                return True
            if attempt < 3:
                print(f"  ⚠️  전송 실패 ({res.status_code}) - {attempt}회 재시도 중...")
                time.sleep(5)
            else:
                print(f"  ❌ 전송 실패 ({res.status_code}) - 3회 모두 실패")
                write_log(f"[텔레그램오류] HTTP {res.status_code}")
                return False
        except Exception as e:
            if attempt < 3:
                print(f"  ⚠️  텔레그램 오류 ({attempt}회) 재시도 중... {e}")
                time.sleep(5)
            else:
                print(f"  ❌ 텔레그램 오류 (3회 실패): {e}")
                write_log(f"[텔레그램오류] {e}")
                return False
    return False


def _format_item(idx: int, notice: dict) -> str:
    """공고 1건을 메시지 라인 1개로 직렬화"""
    link = notice.get("link") or "링크 없음"
    title = notice.get("title", "")
    site  = notice.get("site", "")
    date  = (notice.get("date") or "").strip()
    return (
        f"<b>{idx}.</b> {title}\n"
        f"   🏢 {site} | 📅 {date}\n"
        f"   🔗 {link}"
    )


def build_batch_message(items: list, now_str: str) -> str:
    """
    items: [{"notice": dict, "is_urgent": bool}, ...]
    → 1건의 HTML 메시지 문자열 (긴급 / 일반 섹션 분리)
    """
    urgent = [it for it in items if it["is_urgent"]]
    normal = [it for it in items if not it["is_urgent"]]

    lines = [
        f"🔔 <b>[버스/DRT/자율주행 입찰 모니터링]</b>",
        f"⏰ {now_str}",
        "",
    ]
    idx = 0
    if urgent:
        lines.append(f"🚨 <b>긴급 ({len(urgent)}건)</b> — D-7 이내 또는 긴급 키워드")
        for it in urgent:
            idx += 1
            lines.append(_format_item(idx, it["notice"]))
            lines.append("")
    if normal:
        lines.append(f"📋 <b>일반 입찰공고 ({len(normal)}건)</b>")
        for it in normal:
            idx += 1
            lines.append(_format_item(idx, it["notice"]))
            lines.append("")
    return "\n".join(lines).rstrip()


def _split_message(msg: str, limit: int = TELEGRAM_MSG_LIMIT) -> list:
    """줄 단위로 분할 (HTML 태그가 줄 중간에 닫히지 않는 구조 전제)"""
    if len(msg) <= limit:
        return [msg]
    chunks, cur, cur_len = [], [], 0
    for line in msg.split("\n"):
        line_len = len(line) + 1
        if cur and cur_len + line_len > limit:
            chunks.append("\n".join(cur))
            cur, cur_len = [line], line_len
        else:
            cur.append(line)
            cur_len += line_len
    if cur:
        chunks.append("\n".join(cur))
    return chunks


def send_batch(items: list, now_str: str) -> bool:
    """
    items: [{"notice": dict, "is_urgent": bool}, ...]
    → 묶음 메시지 1건(또는 분할 다건) 발송
    return: 모든 청크가 성공이면 True
    """
    if not items:
        return True
    msg = build_batch_message(items, now_str)
    chunks = _split_message(msg)
    all_ok = True
    for i, chunk in enumerate(chunks, 1):
        if len(chunks) > 1:
            print(f"  📤 묶음 {i}/{len(chunks)} 전송 중...")
        if not send_telegram(chunk):
            all_ok = False
    return all_ok

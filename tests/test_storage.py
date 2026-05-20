"""storage.py 단위 테스트"""
import json
import os
import pytest
from unittest.mock import patch
from storage import load_sent_ids, _atomic_write_json, append_all_notices


class TestLoadSentIds:
    def test_dict_format(self, tmp_path):
        f = tmp_path / "sent.json"
        f.write_text(json.dumps({"id1": "2026-01-01 00:00:00"}), encoding="utf-8")
        with patch("storage.SENT_FILE", str(f)):
            result = load_sent_ids()
        assert result == {"id1": "2026-01-01 00:00:00"}

    def test_list_str_format(self, tmp_path):
        """구버전 list[str] 형식 역호환"""
        f = tmp_path / "sent.json"
        f.write_text(json.dumps(["id1", "id2"]), encoding="utf-8")
        with patch("storage.SENT_FILE", str(f)):
            result = load_sent_ids()
        assert result == {"id1": "1970-01-01 00:00:00", "id2": "1970-01-01 00:00:00"}

    def test_list_of_lists_format(self, tmp_path):
        """구버전 list[list] 형식 역호환"""
        f = tmp_path / "sent.json"
        f.write_text(json.dumps([["id1", "ts1"], ["id2", "ts2"]]), encoding="utf-8")
        with patch("storage.SENT_FILE", str(f)):
            result = load_sent_ids()
        assert result == {"id1": "ts1", "id2": "ts2"}

    def test_missing_file(self, tmp_path):
        with patch("storage.SENT_FILE", str(tmp_path / "nonexistent.json")):
            result = load_sent_ids()
        assert result == {}


class TestAtomicWriteJson:
    def test_write_success(self, tmp_path):
        path = str(tmp_path / "test.json")
        data = {"key": "value", "num": 42}
        _atomic_write_json(path, data)
        with open(path, "r", encoding="utf-8") as f:
            assert json.load(f) == data

    def test_exception_cleans_temp(self, tmp_path):
        path = str(tmp_path / "test.json")

        class BadObj:
            def __init__(self):
                pass

        with pytest.raises(TypeError):
            _atomic_write_json(path, BadObj())
        # 원본 파일이 생성되지 않아야 함
        assert not os.path.exists(path)
        # 임시 파일도 남아있지 않아야 함
        remaining = [f for f in os.listdir(str(tmp_path)) if f.endswith(".tmp")]
        assert remaining == []


class TestAppendAllNotices:
    def test_dedup(self, tmp_path):
        all_file = str(tmp_path / "all.json")
        # 초기 데이터 저장
        initial = [{"id": "a", "title": "공고A"}]
        with open(all_file, "w", encoding="utf-8") as f:
            json.dump(initial, f)

        new = [
            {"id": "a", "title": "공고A"},  # 중복
            {"id": "b", "title": "공고B"},  # 신규
        ]
        with patch("storage.ALL_FILE", all_file):
            added = append_all_notices(new)
        assert added == 1

        with open(all_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 2
        ids = {n["id"] for n in data}
        assert ids == {"a", "b"}

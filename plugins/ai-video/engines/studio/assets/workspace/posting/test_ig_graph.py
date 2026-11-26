import json
import os
import tempfile
from urllib.parse import parse_qs

from ig_graph import IG, IGError

TOKEN = "TESTTOKEN"
USER = "123"


def run_tests():
    # 1. username()
    records = []
    responses = [{"username": "myhandle"}]

    def fake_http(method, url, headers, body):
        records.append((method, url, dict(headers), body))
        return (200, responses.pop(0))

    ig = IG(USER, TOKEN, http=fake_http)
    assert ig.username() == "myhandle"
    assert all(TOKEN not in r[1] for r in records)
    assert records[0][2].get("Authorization") == "OAuth " + TOKEN

    # 2. create_reel_resumable
    records2 = []
    responses2 = [{"id": "CID1", "uri": "https://upload.example/uri"}]

    def fake_http2(method, url, headers, body):
        records2.append((method, url, dict(headers), body))
        return (200, responses2.pop(0))

    ig2 = IG(USER, TOKEN, http=fake_http2)
    cid, uri = ig2.create_reel_resumable("cap", "SS_PERFORMANCE")
    assert (cid, uri) == ("CID1", "https://upload.example/uri")
    parsed = parse_qs(records2[0][3].decode())
    assert parsed.get("media_type") == ["REELS"]
    assert parsed.get("upload_type") == ["resumable"]
    tp = json.loads(parsed["trial_params"][0])
    assert tp == {"graduation_strategy": "SS_PERFORMANCE"}

    # 3. create_reel_from_url no trial_params
    records3 = []
    responses3 = [{"id": "CID2"}]

    def fake_http3(method, url, headers, body):
        records3.append((method, url, dict(headers), body))
        return (200, responses3.pop(0))

    ig3 = IG(USER, TOKEN, http=fake_http3)
    assert ig3.create_reel_from_url("http://video", "cap", trial_graduation=None) == "CID2"
    parsed3 = parse_qs(records3[0][3].decode())
    assert "trial_params" not in parsed3

    # 4. weird trial_graduation raises, no request
    records4 = []

    def fake_http4(method, url, headers, body):
        records4.append((method, url, dict(headers), body))
        return (200, {})

    ig4 = IG(USER, TOKEN, http=fake_http4)
    before = len(records4)
    try:
        ig4.create_reel_resumable("cap", "weird")
        raise SystemExit("expected IGError")
    except IGError:
        pass
    assert len(records4) == before

    # 5. wait_finished IN_PROGRESS then FINISHED; ERROR raises
    records5 = []
    responses5 = [
        {"status_code": "IN_PROGRESS", "status": "in progress"},
        {"status_code": "FINISHED", "status": "done"},
    ]

    def fake_http5(method, url, headers, body):
        records5.append((method, url, dict(headers), body))
        return (200, responses5.pop(0))

    ig5 = IG(USER, TOKEN, http=fake_http5)
    ig5.wait_finished("CID", sleep=lambda s: None)

    records5b = []
    responses5b = [{"status_code": "ERROR", "status": "failed"}]

    def fake_http5b(method, url, headers, body):
        records5b.append((method, url, dict(headers), body))
        return (200, responses5b.pop(0))

    ig5b = IG(USER, TOKEN, http=fake_http5b)
    try:
        ig5b.wait_finished("CID", sleep=lambda s: None)
        raise SystemExit("expected IGError")
    except IGError:
        pass

    # 6. 400 with token in message -> IGError str no token
    records6 = []
    responses6 = [{"error": {"message": "bad token TESTTOKEN", "code": 100}}]

    def fake_http6(method, url, headers, body):
        records6.append((method, url, dict(headers), body))
        return (400, responses6.pop(0))

    ig6 = IG(USER, TOKEN, http=fake_http6)
    try:
        ig6.username()
        raise SystemExit("expected IGError")
    except IGError as e:
        assert "TESTTOKEN" not in str(e)

    # 7. upload_file headers
    records7 = []
    responses7 = [{"success": True}]

    def fake_http7(method, url, headers, body):
        records7.append((method, url, dict(headers), body))
        return (200, responses7.pop(0))

    ig7 = IG(USER, TOKEN, http=fake_http7)
    data = b"hello world"
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        ig7.upload_file("https://upload.example/uri", path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    method, url, headers, body = records7[0]
    assert headers.get("offset") == "0"
    assert headers.get("file_size") == str(len(data))

    print("IG GRAPH OK")


if __name__ == "__main__":
    run_tests()

"""Official Instagram Graph API client (stdlib only).

Thin wrapper around Meta's Graph API for publishing Reels. Token is sent only in
the ``Authorization: OAuth ...`` header and is redacted from every error message.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request


class IGError(Exception):
    pass


def _redact(text, token=None):
    s = "" if text is None else str(text)
    if token is not None:
        s = s.replace(str(token), "***")
    return s


class IG:
    def __init__(self, user_id, token, host="graph.facebook.com", version="v23.0", http=None):
        self.user_id = user_id
        self.token = token
        self.host = host
        self.version = version
        if http is None:
            self.http = self._default_http(120)
            self._http_upload = self._default_http(600)
        else:
            self.http = http
            self._http_upload = http

    @staticmethod
    def _default_http(timeout):
        def _http(method, url, headers, body):
            req = urllib.request.Request(url, data=body, headers=dict(headers or {}), method=method)
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    raw = resp.read()
                    status = resp.status
            except urllib.error.HTTPError as e:
                raw = e.read()
                status = e.code
            data = {}
            if raw:
                try:
                    data = json.loads(raw.decode("utf-8"))
                except Exception:
                    try:
                        data = json.loads(raw)
                    except Exception:
                        data = {}
            return status, data
        return _http

    def _redact(self, text):
        return _redact(text, self.token)

    def _base(self):
        return "https://" + self.host

    def _headers(self, extra=None):
        h = {"Authorization": "OAuth " + str(self.token)}
        if extra:
            h.update(extra)
        return h

    def _extract_error(self, data, status):
        if isinstance(data, dict):
            err = data.get("error")
            if isinstance(err, dict):
                msg = err.get("message")
                code = err.get("code", err.get("error_code"))
                if msg and code is not None:
                    return "{} (code {})".format(msg, code)
                if msg is not None:
                    return str(msg)
                if code is not None:
                    return str(code)
            if "message" in data:
                return str(data.get("message"))
        return "HTTP {}".format(status)

    def _raise_for(self, status, data):
        try:
            st = int(status)
        except (TypeError, ValueError):
            st = 0
        if st >= 400:
            raise IGError(self._redact(self._extract_error(data, status)))
        if isinstance(data, dict) and "error" in data:
            raise IGError(self._redact(self._extract_error(data, status)))

    def _trial_params_field(self, trial_graduation):
        if trial_graduation is None:
            return None
        val = str(trial_graduation).upper()
        if val not in ("MANUAL", "SS_PERFORMANCE"):
            raise IGError(self._redact("invalid trial_graduation: {}".format(trial_graduation)))
        return json.dumps({"graduation_strategy": val})

    def username(self):
        url = "{}/{}/{}?fields=username".format(self._base(), self.version, self.user_id)
        status, data = self.http("GET", url, self._headers(), None)
        self._raise_for(status, data)
        return data["username"]

    def quota(self):
        url = "{}/{}/{}/content_publishing_limit?fields=quota_usage,config".format(self._base(), self.version, self.user_id)
        status, data = self.http("GET", url, self._headers(), None)
        self._raise_for(status, data)
        return data

    def create_reel_resumable(self, caption, trial_graduation=None):
        tp = self._trial_params_field(trial_graduation)
        form = {"media_type": "REELS", "upload_type": "resumable", "caption": caption}
        if tp is not None:
            form["trial_params"] = tp
        body = urllib.parse.urlencode(form).encode("utf-8")
        url = "{}/{}/{}/media".format(self._base(), self.version, self.user_id)
        status, data = self.http("POST", url, self._headers({"Content-Type": "application/x-www-form-urlencoded"}), body)
        self._raise_for(status, data)
        return (data["id"], data["uri"])

    def upload_file(self, upload_uri, path):
        with open(path, "rb") as f:
            raw = f.read()
        size = len(raw)
        headers = self._headers({
            "Content-Type": "application/octet-stream",
            "offset": "0",
            "file_size": str(size),
        })
        status, data = self._http_upload("POST", upload_uri, headers, raw)
        if not isinstance(data, dict):
            data = {} if data is None else data
        # non-2xx
        try:
            st = int(status)
        except (TypeError, ValueError):
            st = 0
        if st >= 400:
            raise IGError(self._redact(self._extract_error(data if isinstance(data, dict) else {}, status)))
        if isinstance(data, dict) and "error" in data:
            raise IGError(self._redact(self._extract_error(data, status)))
        if isinstance(data, dict) and data.get("success") is False:
            raise IGError(self._redact(str(data.get("message") or "upload failed")))

    def create_reel_from_url(self, video_url, caption, trial_graduation=None, cover_url=None):
        tp = self._trial_params_field(trial_graduation)
        form = {"media_type": "REELS", "video_url": video_url, "caption": caption}
        if cover_url is not None:
            form["cover_url"] = cover_url
        if tp is not None:
            form["trial_params"] = tp
        body = urllib.parse.urlencode(form).encode("utf-8")
        url = "{}/{}/{}/media".format(self._base(), self.version, self.user_id)
        status, data = self.http("POST", url, self._headers({"Content-Type": "application/x-www-form-urlencoded"}), body)
        self._raise_for(status, data)
        return data["id"]

    def wait_finished(self, container_id, timeout=900, every=10, sleep=time.sleep):
        url = "{}/{}/{}?fields=status_code,status".format(self._base(), self.version, container_id)
        start = time.time()
        polls = 0
        max_polls = (int(timeout // every) + 1) if every and every > 0 else 1
        if max_polls < 1:
            max_polls = 1
        while True:
            status, data = self.http("GET", url, self._headers(), None)
            self._raise_for(status, data)
            code = data.get("status_code") if isinstance(data, dict) else None
            if code == "FINISHED":
                return
            if code in ("ERROR", "EXPIRED"):
                raise IGError(self._redact(str((data.get("status") if isinstance(data, dict) else None) or code)))
            polls += 1
            if time.time() - start >= timeout or polls >= max_polls:
                raise IGError("timeout")
            sleep(every)

    def publish(self, container_id):
        form = {"creation_id": container_id}
        body = urllib.parse.urlencode(form).encode("utf-8")
        url = "{}/{}/{}/media_publish".format(self._base(), self.version, self.user_id)
        status, data = self.http("POST", url, self._headers({"Content-Type": "application/x-www-form-urlencoded"}), body)
        self._raise_for(status, data)
        return data["id"]

    def permalink(self, media_id):
        url = "{}/{}/{}?fields=permalink".format(self._base(), self.version, media_id)
        status, data = self.http("GET", url, self._headers(), None)
        self._raise_for(status, data)
        return (data.get("permalink", "") if isinstance(data, dict) else "")

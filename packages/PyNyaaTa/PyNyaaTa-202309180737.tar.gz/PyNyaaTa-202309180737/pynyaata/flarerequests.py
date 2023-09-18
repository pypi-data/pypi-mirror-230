from io import BytesIO
from urllib import parse
from charset_normalizer import detect
from requests import RequestException, Response, Session, post
from .config import CLOUDPROXY_ENDPOINT


class FlareRequests(Session):
    def request(self, method, url, params=None, data=None, **kwargs):
        if not CLOUDPROXY_ENDPOINT:
            return super().request(method, url, params, data, **kwargs)

        sessions = post(CLOUDPROXY_ENDPOINT, json={"cmd": "sessions.list"}).json()

        if "sessions" in sessions and len(sessions["sessions"]) > 0:
            FLARE_SESSION = sessions["sessions"][0]
        else:
            response = post(CLOUDPROXY_ENDPOINT, json={"cmd": "sessions.create"})
            session = response.json()

            if "session" in session:
                FLARE_SESSION = session["session"]
            else:
                raise RequestException(response)

        if params:
            url += "&" if len(url.split("?")) > 1 else "?"
            url = f"{url}{parse.urlencode(params)}"

        post_data = {
            "cmd": f"request.{method.lower()}",
            "session": FLARE_SESSION,
            "url": url,
        }

        if data:
            post_data["postData"] = parse.urlencode(data)

        try:
            response = post(
                CLOUDPROXY_ENDPOINT,
                json=post_data,
            )

            content = response.json()

            if "solution" in content:
                solution = content["solution"]
                raw = solution["response"].encode()
                encoding = detect(raw)

                resolved = Response()
                resolved.status_code = solution["status"]
                resolved.headers = solution["headers"]
                resolved.raw = BytesIO(raw)
                resolved.url = url
                resolved.encoding = encoding["encoding"]
                resolved.reason = content["status"]
                resolved.cookies = solution["cookies"]

                return resolved

            raise RequestException(response)
        except RequestException:
            session = post(
                CLOUDPROXY_ENDPOINT,
                json={"cmd": "sessions.destroy", "session": FLARE_SESSION},
            )

            raise RequestException(solution)

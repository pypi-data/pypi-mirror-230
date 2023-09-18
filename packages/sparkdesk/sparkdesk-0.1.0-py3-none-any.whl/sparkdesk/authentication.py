import base64
import hmac
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse


class Authentication:
    def __init__(self, api_key: str, api_secret: str, api_version="v2.1"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_version = api_version

    @property
    def _api_url(self):
        return f"wss://spark-api.xf-yun.com/{self.api_version}/chat"

    def get_authorization_url(self):
        parsed_api_url = urlparse(self._api_url)
        date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %Z")

        signature_origin = (
            f"host: {parsed_api_url.netloc}\n"
            f"date: {date}\n"
            f"GET {parsed_api_url.path} HTTP/1.1"
        )
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode(), signature_origin.encode(), digestmod="sha256"
            ).digest()
        ).decode()
        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode()).decode()
        params = {
            "authorization": authorization,
            "date": date,
            "host": parsed_api_url.netloc,
        }

        return f"{self._api_url}?{urlencode(params)}"

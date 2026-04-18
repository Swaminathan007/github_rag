# backend/utils/http_client.py
import requests


class HttpConnection:
    def __init__(self, base_url: str, timeout: int = 5):
        self.base_url = base_url.rstrip("/")
        self.response_content: str = ""
        self.response_code: int = 0
        self.timeout = timeout

    def get(self):
        response = requests.get(self.base_url,timeout=self.timeout)
        response.raise_for_status()
        self.response_code = response.status_code
        self.response_content = response.content

    def post(self, data: dict):
        response = requests.post(self.base_url,json=data,timeout=self.timeout)
        response.raise_for_status()
        self.response_code = response.status_code
        self.response_content = response.json()
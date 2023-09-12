import logging
import requests


class RequestUtils:

    @staticmethod
    def call_endpoint(url, token, method, params=None, json=None):
        headers = dict()
        headers["Authorization"] = f"Bearer {token}"
        # cleaned_hostname = (
        #     self._workspace_url[:-1]
        #     if self._workspace_url.endswith("/")
        #     else self._workspace_url
        # )
        # url = f"{cleaned_hostname}{endpoint}"
        response = requests.request(
            url=url, headers=headers, method=method, params=params, json=json
        )
        try:
            return response.json()
        except Exception as e:
            logging.warn(f"Error processing request {e}")
            return {
                "response": response.text,
                "error": str(e),
                "status_code": response.status_code
            }
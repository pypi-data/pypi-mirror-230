import requests
import structlog
from requests.auth import HTTPBasicAuth

logger = structlog.get_logger(__name__)


class TaranDMAnalytics:
    def __init__(self, endpoint_url: str, username: str, password: str) -> None:
        self.endpoint_url = endpoint_url + ("" if endpoint_url.endswith("/") else "/")
        self.username = username
        self.password = password

        self.validate_url()

    def validate_url(self) -> None:
        url = self.endpoint_url + "info"
        response = requests.get(url=url, auth=HTTPBasicAuth(self.username, self.password))

        if response.status_code == 200:
            logger.info(f"Connection to {self.endpoint_url} was established.")
        elif response.status_code == 401:
            logger.info(f"Connection to {self.endpoint_url} cannot be established. Endpoint error message: "
                        f"{response.text}")

# core/utils.py
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class ExternalAPIClient:
    def __init__(self, api_config):
        self.base_url = api_config.get('BASE_URL')
        self.api_key = api_config.get('API_KEY')
        self.timeout = api_config.get('TIMEOUT', 30)

        if not self.base_url or not self.api_key:
            logger.error("API konfiguratsiyasi to'liq emas!")

    def get(self, endpoint, params=None):
        """GET so'rov yuborish"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"API timeout: {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API xatolik: {endpoint} - {str(e)}")
            return None

    def post(self, endpoint, data=None):
        """POST so'rov yuborish"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API xatolik: {endpoint} - {str(e)}")
            return None


class TestAPIClient(ExternalAPIClient):
    def __init__(self):
        super().__init__(settings.EXTERNAL_API_SETTINGS)

    def get_test_list(self):
        return self.get(f'proctoring-exam-list')

    def verify_candidate(self, imie, test_key):
        return self.get('proctoring-person-exam', {
            'imie': imie,
            'test_key': test_key
        })
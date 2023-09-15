from requests.adapters import HTTPAdapter, Retry, MaxRetryError, RetryError

import logging
import requests


class BaseAPI:
    def __init__(self, token=None, local=False):
        self.token = token
        self.route = None
        self.api_key = None
        self.base_path = 'https://hgzgw4jkd4.execute-api.us-east-1.amazonaws.com/dev/v1' if not local else 'http://127.0.0.1:5000/v1'
        self.session = requests.session()

    @staticmethod
    def _is_success(status_code: int) -> bool:
        """Returns True if the status code is successful (2xx). False otherwise.

        Args:
            status_code (int): the status code of the response

        Returns:
            bool: is the status code successful
        """
        return 200 <= status_code < 300

    @staticmethod
    def _is_unauthorized(status_code: int) -> bool:
        """Returns True if the status code is unauthorized (403). False otherwise.

        Args:
            status_code (int): the status code of the response

        Returns:
            bool: is the status code authorized
        """
        return status_code == 403

    @staticmethod
    def _is_timed_out(status_code: int) -> bool:
        """Returns True if the status code is timed out

        Args:
            status_code (int): the status code of the response

        Returns:
            bool: is the status code timed out
        """
        return status_code == 504

    def _get(self, path: str, body: object = None, detailed: bool = False) -> object:
        """Make a GET request with exponential back off

        Args:
            path (str): Request path to append to base path
            body (dict, optional): JSON body to include with request
            detailed (bool, optional): whether to include detailed information

        Raises:
            AuthenticationError: when requests are not authenticated correctly
            TimeoutError: when requests are being timed out
            APIError: when API is not available

        Returns:
            object: the response object
        """
        return self._request(method="GET", body=body, path=path, detailed=detailed)

    def _post(self, path: str, body: object = None, detailed: bool = False) -> object:
        """Make a POST request with exponential back off

        Args:
            path (str): Request path to append to base path
            body (dict, optional): JSON body to include with request
            detailed (bool, optional): whether to include detailed information

        Raises:
            AuthenticationError: when requests are not authenticated correctly
            TimeoutError: when requests are being timed out
            APIError: when API is not available

        Returns:
            object: the response object
        """
        return self._request(method="POST", body=body, path=path, detailed=detailed)

    def _put(self, path: str, body: object = None, detailed: bool = False) -> object:
        """Make a PUT request with exponential back off

        Args:
            path (str): Request path to append to base path
            body (dict, optional): JSON body to include with request
            detailed (bool, optional): whether to include detailed information

        Raises:
            AuthenticationError: when requests are not authenticated correctly
            TimeoutError: when requests are being timed out
            APIError: when API is not available

        Returns:
            object: the response object
        """
        return self._request(method="PUT", body=body, path=path, detailed=detailed)

    def _request(self, method: str, path: str, body=None, detailed: bool = False):
        """Make a request with exponential back off

                Args:
            method (str): HTTP method ("GET", "POST")
            path (str): Request path to append to base path
            body (dict, optional): JSON body to include with request
            detailed (bool, optional): whether to include detailed information

        Raises:
            AuthenticationError: when requests are not authenticated correctly
            TimeoutError: when requests are being timed out
            APIError: when API is not available

        Returns:
            object: the response object
        """

        headers = dict()

        if self.api_key:
            headers['x-api-key'] = self.api_key

        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"

        self.session.headers.update(headers)

        url = self.base_path + path

        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])

        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        logging.info(f"sending request: {url}")

        try:
            response = self.session.request(method, url, json=body)
        except (MaxRetryError, RetryError) as error:
            raise TimeoutError("Endpoint timed out after 3 tries") from error

        response_json = response.json()

        if self._is_success(response.status_code):
            if detailed:
                return response_json

            return response_json.get("payload") or response_json

        if self._is_unauthorized(response.status_code):
            raise AuthenticationError("Unauthorized", response_json)

        if self._is_timed_out(response.status_code):
            raise APIError("API request failed", response_json)


class APIError(Exception):
    """Wrapper for exceptions generated by the APIs"""

    def __init__(self, message, resp={}):
        self.resp = resp
        try:
            payload = resp['payload']
        except KeyError:
            payload = {}
        try:
            self.msg = payload.get('message', message)
        except AttributeError:
            self.msg = payload
        self.code = resp.get('status')
        self.request_id = resp.get('correlation_id')
        super(APIError, self).__init__(self.msg)


class APITimeoutError(APIError):
    def __init__(self, message, resp=None):
        self.resp = resp
        self.msg = message
        super(APITimeoutError, self).__init__(self.msg)


class AuthenticationError(APIError):
    def __init__(self, message, resp=None):
        self.resp = resp
        self.msg = message
        super(AuthenticationError, self).__init__(self.msg)
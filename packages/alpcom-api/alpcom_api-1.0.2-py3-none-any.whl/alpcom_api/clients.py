from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time

import jwt
import requests

from alpcom_api.cache import TokenCache
from alpcom_api.errors import ApiFormError, ApiError, AuthError


class ALPClient:
    DEFAULT_URL = 'https://www.alp.com/api/v3'
    REQUEST_TIMEOUT = 60

    def __init__(self, url: str = None, **kwargs) -> None:
        super().__init__()

        self._url = url or self.DEFAULT_URL
        self._headers = {}

    def get(self, path: str, data: dict):
        return self._to_result(requests.get(
            self._build_url(path), params=data,
            headers=self._headers, timeout=self.REQUEST_TIMEOUT
        ))

    def _to_result(self, response: requests.Response):
        logging.debug(f"API call to {response.url} -> {response.status_code}")

        if response.ok:
            return self._retrieve_data(response)

        elif response.status_code == 400:
            data = self._retrieve_data(response)
            if isinstance(data, dict) and 'formErrors' in data:
                raise ApiFormError(detail=data.get('formErrors'))
            raise ApiError(data)

        elif response.status_code == 401:
            data = self._retrieve_data(response)
            raise AuthError(data)

        else:
            logging.error(f'API-Gateway service unavailable. '
                          f'URL: {response.url}, Code: {response.status_code}, Text: {response.text}')
            response.raise_for_status()

    @staticmethod
    def _retrieve_data(response: requests.Response):
        content_type = response.headers.get('Content-Type', '')
        logging.debug(f'@@@@@@ Content-Type: {content_type}')
        logging.debug(f'@@@@@@ Content: {response.content}')
        if 'text/plain' in content_type:
            return response.text
        elif 'application/json' in content_type:
            return response.json() if len(response.content) else None
        else:
            logging.debug(f"Unknown Content-Type: {content_type}")

    def _build_url(self, path: str):
        return os.path.join(self._url, path)


class ALPAuthClient(ALPClient):
    def __init__(self, key: str = None,
                 secret: str = None,
                 cache: TokenCache = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)

        self._secret = secret
        self._authenticate(key, secret, cache=cache)

    def _authenticate(self, key: str, secret: str, cache: TokenCache = None) -> None:
        token = None

        if cache is not None:
            token = cache.get()

            if token and self._is_token_expired(token):
                token = None

        if not token:
            token = self.json('auth', {
                'api_key': key,
                'api_secret': secret,
            })

        if cache is not None:
            cache.set(token)

        self._headers['Authorization'] = f'Bearer {token}'

    def json(self, path: str, data: dict, method: str = 'POST'):
        r = requests.Request(
            method=method,
            url=self._build_url(path),
            json=data,
            headers=self._headers,
        ).prepare()

        if r.body:
            r.headers['X-SIGN'] = self._make_sign(r.body)

        return self._to_result(requests.session().send(
            r, timeout=self.REQUEST_TIMEOUT
        ))

    def get_token(self) -> str:
        return self._headers['Authorization'].split(' ')[-1]

    def _make_sign(self, body: bytes):
        return hmac.new(
            key=self._secret.encode(),
            msg=body,
            digestmod=hashlib.sha256
        ).hexdigest()

    @classmethod
    def _is_token_expired(cls, token: str) -> bool:
        payload = jwt.decode(token, options={"verify_signature": False}, algorithms=['HS256'])
        return int(time.time()) > int(payload.get('exp'))

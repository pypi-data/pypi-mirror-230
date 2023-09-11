# Copyright 2023 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

import hashlib
import json
import logging
from pathlib import Path
from typing import (
    List,
    Optional,
)

from oauthlib.oauth2 import WebApplicationClient
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from requests_oauthlib import OAuth2Session

from .keycloak import get_keycloak_oidc_urls
from .oidc import OidcSessionAuth
from .redirect_listener import (
    complete_login,
    get_free_network_port,
)

DEFAULT_AUTH_DIR = Path.home() / ".config" / "qctrl"
LOGGER = logging.getLogger(__name__)
_OIDC_CLIENT_ID = "cli-python"


class CliAuth(OidcSessionAuth):
    """
    Q-CTRL authentication handler for the command line interface.
    """

    _DEFAULT_SCOPE = ["openid", "profile", "email", "offline_access"]

    def __init__(
        self,
        base_url: str,
        client_id: str = _OIDC_CLIENT_ID,
        scope: Optional[List[str]] = None,
        redirect_uri: Optional[str] = None,
        redirect_uri_port: Optional[str] = None,
    ):
        if redirect_uri and not redirect_uri_port:
            raise ValueError("redirect_uri_port is required when redirect_uri is set")

        if redirect_uri_port and not redirect_uri:
            raise ValueError("redirect_uri is required when redirect_uri_port is set")

        self._base_url = base_url
        self._client_id = client_id
        self._scope = scope or self._DEFAULT_SCOPE
        self._redirect_uri_port = redirect_uri_port or get_free_network_port()
        self._redirect_uri = (
            redirect_uri or f"http://localhost:{self._redirect_uri_port}"
        )

        super().__init__()

        try:
            self._get_access_token()
        except InvalidGrantError as exc:
            LOGGER.error("%s", exc, exc_info=True)
            self._authenticate()

    def _get_urls(self):
        return get_keycloak_oidc_urls(self._base_url)

    def _create_session(self):
        client = WebApplicationClient(self._client_id, self._redirect_uri)

        return OAuth2Session(
            client=client,
            scope=self._scope,
            auto_refresh_kwargs={"client_id": self._client_id},
            redirect_uri=self._redirect_uri,
            token=self._get_saved_token(),
            token_updater=self._save_token,
        )

    @property
    def _session_file_path(self):
        file_name = hashlib.md5((self._client_id + self._base_url).encode()).hexdigest()
        return DEFAULT_AUTH_DIR / file_name

    def _save_token(self, token: dict):
        """
        Saves the token to the file.
        """

        try:
            self._session_file_path.parent.mkdir(
                mode=0o700, parents=True, exist_ok=True
            )
            self._session_file_path.touch(mode=0o600, exist_ok=True)
            self._session_file_path.write_text(
                json.dumps(token, indent=2), encoding="utf-8"
            )
        except IOError as exc:
            LOGGER.error("%s", exc, exc_info=True)
            raise IOError("incorrect permissions for credentials file") from exc

    def _get_saved_token(self) -> dict:
        """
        Loads the token from the file.
        """
        token = None

        try:
            with open(self._session_file_path, "r", encoding="utf-8") as file_pointer:
                token = json.load(file_pointer)

        except FileNotFoundError:
            pass

        except IsADirectoryError as exc:
            raise IOError("credentials file cannot be a directory") from exc

        return token

    def _authenticate(self):
        authorization_url, _ = self._oidc_session.authorization_url(
            self._urls.base_authorization_url
        )
        print("")
        print("Authentication URL:")
        print("")
        print(authorization_url)
        print("")
        complete_login(
            self._redirect_uri_port,
            authorization_url,
            self._fetch_token_from_authorization_response,
        )
        print("Successful authentication!")

    def _fetch_token_from_authorization_response(self, authorization_response):
        """
        Fetch token from authorization response and save it if `token_updater`
        is present.
        """
        print("Finalizing authentication...")
        self._oidc_session.fetch_token(
            self._urls.token_url, authorization_response=authorization_response
        )

        self._save_token(self._oidc_session.token)

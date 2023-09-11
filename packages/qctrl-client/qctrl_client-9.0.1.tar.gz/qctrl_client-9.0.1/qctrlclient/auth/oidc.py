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

import os
import time
from abc import abstractmethod
from dataclasses import dataclass
from typing import (
    List,
    Optional,
)

from requests_oauthlib import OAuth2Session

from .base import BaseAuth
from .helpers import get_payload

# OAUTHLIB_INSECURE_TRANSPORT=1 disables the requirement for HTTPS for the
# localhost redirect server and allows "insecure" (HTTP) requests to our OIDC
# server as a side effect.
# As the servers will always validate tokens from clients against our trusted CA
# and our public services only accept HTTPS, it is safe to use this at client side.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@dataclass
class OidcUrls:
    """
    Common URLs used for OIDC authentication
    processes.
    """

    base_url: str
    token_url: Optional[str] = None
    base_authorization_url: Optional[str] = None
    user_info_url: Optional[str] = None


class OidcSessionAuth(BaseAuth):
    """
    Abstract authentication handler which uses OIDC sessions.
    """

    _REFRESH_THRESHOLD = 60  # seconds

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._urls = self._get_urls()
        self._oidc_session = self._create_session()

    @abstractmethod
    def _get_urls(self) -> OidcUrls:
        """
        Returns the OIDC urls to be used by the authentication
        session.
        """

    @abstractmethod
    def _create_session(self) -> OAuth2Session:
        """
        Returns the OAuth2Session to be used for handling
        authentication.
        """

    def _expires_soon(self, access_token: str) -> bool:
        """"""
        payload = get_payload(access_token)
        expires_at = payload.get("exp")
        return expires_at and expires_at - time.time() < self._REFRESH_THRESHOLD

    def _has_refresh_token(self) -> bool:
        """Checks if the session has a refresh token issued."""
        return bool(self._oidc_session.token.get("refresh_token"))

    def _get_access_token(self) -> str:
        # if token already exists
        if self._oidc_session.access_token:
            # if token expires soon
            if self._expires_soon(self._oidc_session.access_token):
                # if refresh token issued, try to refresh
                if self._has_refresh_token():
                    try:
                        self._oidc_session.refresh_token(self._urls.token_url)

                    # unable to refresh, need to re-authenticate
                    except Warning:  # TODO review how this gets thrown
                        self._authenticate()

                # no refresh token issued, re-authenticate
                else:
                    self._authenticate()

        # no token, need to authenticate
        else:
            self._authenticate()

        return self._oidc_session.access_token

    @abstractmethod
    def _authenticate(self):
        """
        Runs the authentication process. When this function completes,
        the OAuth2 session should have a valid access token (assuming
        the credentials provided are correct).
        """

    def _get_access_token_payload(self) -> dict:
        """
        Returns the access token payload for data inspection.
        """
        return get_payload(self._get_access_token())

    def _get_resource_access_roles_for_client(self, payload: dict) -> List[str]:
        """
        Return the user assigned roles related to the current client.
        """
        try:
            resource_access = payload["resource_access"]
            client_roles = resource_access[self._oidc_session.client_id]
            return client_roles["roles"]
        except KeyError:
            return []

    def user_roles(self) -> List[str]:
        """
        Returns True if the user has the given role for the client.
        """
        if not self._oidc_session.client_id:
            raise ValueError("Missing Oauth2 client ID")

        payload = self._get_access_token_payload()
        client_roles = self._get_resource_access_roles_for_client(payload)
        return client_roles

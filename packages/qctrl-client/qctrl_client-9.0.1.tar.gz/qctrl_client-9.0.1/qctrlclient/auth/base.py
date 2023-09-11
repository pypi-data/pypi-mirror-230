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

from abc import abstractmethod
from typing import List

from requests.auth import AuthBase


class BaseAuth(AuthBase):
    """Base class that defines the signature for other authentication classes
    to be used either synchronously with `requests` or asynchronously with
    `aiohttp`.

    Inherited classes must define `encode(self)` method that returns the
    `Authorization` header value.
    """

    def __call__(self, r):
        r.headers["Authorization"] = self._get_authorization_header()
        return r

    def _get_authorization_header(self) -> str:
        return f"Bearer {self.access_token}"

    @property
    def access_token(self) -> str:
        """
        Returns a valid access token to be used in the `Authorization`
        header.
        """
        return self._get_access_token()

    @abstractmethod
    def _get_access_token(self) -> str:
        """To be overridden by subclass."""

    def __repr__(self):
        return AuthBase.__repr__(self)

    @abstractmethod
    def user_roles(self) -> List[str]:
        """
        To be overriden by subclass.
        """

    def has_role(self, role: str) -> bool:
        """
        Returns True if the user has the given role for the client.
        """
        return role in self.user_roles()

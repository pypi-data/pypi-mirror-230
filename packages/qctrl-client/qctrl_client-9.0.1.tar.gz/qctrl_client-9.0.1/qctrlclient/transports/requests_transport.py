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

import json
from typing import (
    Any,
    Dict,
    Optional,
    Type,
)

import requests
from gql.transport import Transport
from gql.transport.exceptions import (
    TransportAlreadyConnected,
    TransportClosed,
    TransportProtocolError,
    TransportServerError,
)
from graphql import (
    DocumentNode,
    ExecutionResult,
    print_ast,
)

from qctrlclient.auth import BaseAuth


class RequestsTransport(Transport):
    """
    Transport class using the `requests` package.
    """

    def __init__(
        self,
        url: str,
        auth: Optional[BaseAuth] = None,
        headers: Optional[Dict[str, str]] = None,
        retries: int = 0,
        json_encoder: Type[json.JSONEncoder] = json.JSONEncoder,
    ):
        self._url = url
        self._auth = auth
        self._headers = headers or {}
        self._retries = retries
        self._json_encoder = json_encoder

        self._session = None

    def connect(self):
        if self._session is None:
            self._session = requests.Session()

            if self._retries > 0:
                adapter = requests.adapters.HTTPAdapter(
                    max_retries=requests.adapters.Retry(
                        total=self._retries,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504],
                        allowed_methods=None,
                    )
                )
                for prefix in "http://", "https://":
                    self._session.mount(prefix, adapter)
        else:
            raise TransportAlreadyConnected("Transport is already connected")

    def _send_request(self, payload: Dict[str, Any]) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        headers.update(self._headers)

        return self._session.post(
            self._url,
            auth=self._auth,
            headers=headers,
            data=json.dumps(payload, cls=self._json_encoder),
        )

    def _build_payload(  # pylint:disable=no-self-use
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        query_str = print_ast(document)
        payload = {"query": query_str}

        if variable_values:
            payload["variables"] = variable_values

        if operation_name:
            payload["operationName"] = operation_name

        return payload

    def _get_result_data(  # pylint:disable=no-self-use
        self, response: requests.Response
    ) -> Dict[str, Any]:
        try:
            response.raise_for_status()
            result = response.json()

        # invalid HTTP response
        except requests.HTTPError as exc:
            status_code = exc.response.status_code
            raise TransportServerError(str(exc), status_code) from exc

        # invalid response body
        except requests.exceptions.JSONDecodeError as exc:
            raise TransportProtocolError(
                f"Invalid response format: {str(exc)}"
            ) from exc

        # invalid response data
        if "errors" not in result and "data" not in result:
            raise TransportProtocolError('No "data" or "errors" keys in response data')

        return result

    def execute(
        self,
        document,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        **__,
    ):  # pylint:disable=arguments-differ
        if not self._session:
            raise TransportClosed("Transport is not connected")

        payload = self._build_payload(document, variable_values, operation_name)
        response = self._send_request(payload)
        result = self._get_result_data(response)

        return ExecutionResult(
            errors=result.get("errors"),
            data=result.get("data"),
            extensions=result.get("extensions"),
        )

    def close(self):
        if self._session:
            self._session.close()
            self._session = None

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

from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Type,
    Union,
)

import gql
from gql.transport import Transport
from gql.transport.exceptions import (
    TransportQueryError,
    TransportServerError,
)
from graphql import (
    DocumentNode,
    print_schema,
)
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from .auth import BaseAuth
from .exceptions import (
    GraphQLClientError,
    GraphQLQueryError,
)
from .transports import RequestsTransport


def _default_handle_query_error(key: str, data: Dict[str, Any]):
    """Handles query level errors.

    Parameters
    ----------
    key : str
        The query name or alias key.
    data : dict
        The query result returned from gql.Client.

    Raises
    ------
    GraphQLQueryError
        If there are any errors.
    """
    raise GraphQLQueryError(data["errors"])


def _prepare_kwargs(
    user_options: Dict[str, Any], **mandatory_kwargs: Any
) -> Dict[str, Any]:
    """Combines mandatory keyword arguments with options
    provided by the user.

    Parameters
    ----------
    user_options : Dict[str,Any]
        Keyword arguments requested by the user.
    mandatory_kwargs : Any
        Keyword arguments that must be included in the
        result.

    Returns
    -------
    Dict[str,Any]

    Raises
    ------
    RuntimeError
        If any keyword arguments requested by the user
        conflict with any mandatory keyword arguments.
    """
    kwargs = mandatory_kwargs.copy()

    for name, value in user_options.items():
        if name in kwargs:
            raise RuntimeError(f"Unable to specify keyword argument: {name}")

        kwargs[name] = value

    return kwargs


def _is_graphql_internal_server_error(exception: Exception) -> bool:
    """Checks if the exception is a GraphQL internal server
    error which should trigger a retry.

    Parameters
    ----------
    exception : Exception
        The exception raised by the client.

    Returns
    -------
    bool
    """

    if isinstance(exception, TransportQueryError):
        return "INTERNAL_SERVER_ERROR" in str(exception)

    return False


class GraphQLClient:  # pylint: disable=too-few-public-methods
    """
    GraphQL Client.
    """

    def __init__(
        self,
        url: str,
        auth: Optional[BaseAuth] = None,
        headers: Optional[Dict[str, Any]] = None,
        schema: Optional[str] = None,
        fetch_schema_from_transport: bool = True,
        transport_cls: Type[Transport] = RequestsTransport,
        transport_options: Optional[Dict[str, Any]] = None,
        client_options: Optional[Dict[str, Any]] = None,
        handle_query_error: Callable = _default_handle_query_error,
    ):
        """
        Parameters
        ----------
        url : str
            The endpoint for the graphql request.
        headers : dict
            The dictionary of http headers.
        auth : BaseAuthHandler, optional
            An instance of an authentication object. (Default value = None)
        schema : list of str, Optional
            The string version of the GQL schema. (Default value = None)
        transport_cls : Optional[Type[Transport]]
            The transport class to be used by the gql.Client instance.
        transport_options : dict
            Custom arguments to the used transport instance. (Default value = None)
        client_options : dict
            Custom arguments to the created gql.Client instance. (Default value = None)
        handle_query_error : Callable
            Hook function called if any query level errors are found. The callable
            should accept two arguments - the query key and the query result. Default
            behaviour is to raise a GraphQLQueryError.
        """

        self._auth = auth
        self._handle_query_error = handle_query_error

        transport_options = transport_options or {}
        transport_kwargs = _prepare_kwargs(
            transport_options,
            url=url,
            headers=headers or {},
            auth=auth,
        )

        transport = transport_cls(**transport_kwargs)

        client_options = client_options or {}
        client_kwargs = _prepare_kwargs(
            client_options,
            schema=schema,
            transport=transport,
            fetch_schema_from_transport=fetch_schema_from_transport,
        )

        self._client = gql.Client(**client_kwargs)

    def check_user_role(self, role: str):
        """
        Attempts to verify role and raises exceptions if not valid.
        """
        if not role:
            raise ValueError("Role is required.")

        if self._auth is None:
            raise RuntimeError("Client is not authenticated.")

        if not self._auth.has_role(role):
            raise GraphQLClientError(
                f"Unauthorized. User doesn't have required role `{role}`."
            )

    def get_access_token(self) -> str:
        """
        Returns an access token.
        """
        if self._auth is None:
            raise RuntimeError("Client is not authenticated.")

        return self._auth.access_token

    @retry(
        retry=(
            retry_if_exception_type(TransportServerError)
            | retry_if_exception(_is_graphql_internal_server_error)
        ),
        wait=wait_fixed(2),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def execute(
        self, query: Union[DocumentNode, str], variable_values: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Executes a GraphQL query/mutation.
        """
        if variable_values is None:
            variable_values = {}

        if isinstance(query, DocumentNode):
            document = query
        else:
            document = gql.gql(query)

        result = self._client.execute(document, variable_values=variable_values)
        self._check_errors(document, result)
        return result

    def _check_errors(
        self,
        document: DocumentNode,
        result: Dict,
    ):
        """Checks for any query-level errors returned from the query request.

        Parameters
        ----------
        document: DocumentNode
            The GraphQL document which was executed.
        result: dict
            The result of the query execution, as returned from
            gql.Client.execute
        """

        # search result for query errors
        for definition_node in document.definitions:
            for node in definition_node.selection_set.selections:
                if node.alias:
                    query_key = node.alias.value
                else:
                    query_key = node.name.value

                if result.get(query_key, {}).get("errors"):
                    self._handle_query_error(query_key, result[query_key])

    def get_schema(self) -> str:
        """
        Get Schema from gql.Client.
        """
        with self._client as session:
            session.fetch_schema()

        if not self._client.schema:
            raise ValueError("Schema cannot be empty")

        return print_schema(self._client.schema)

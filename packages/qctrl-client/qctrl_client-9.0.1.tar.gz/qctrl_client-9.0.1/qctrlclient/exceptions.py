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
    Dict,
    List,
    Union,
)

# represents the `Error` GraphQL type
QueryErrorField = str
QueryErrorMessage = str
QueryError = Dict[str, Union[List[QueryErrorField], QueryErrorMessage]]


class GraphQLClientError(Exception):
    """Base exception for client side GraphQL errors."""


class GraphQLQueryError(GraphQLClientError):
    """Errors that occurred while executing a GraphQL query."""

    _UNKNOWN_ERROR = "Unknown error"
    _EMPTY_ERRORS = "An error occurred while executing the query"

    def __init__(self, errors: List[QueryError]):
        super().__init__(errors)
        self._errors = errors

    def _format_error(self, error: QueryError) -> str:
        message = error.get("message", "")
        fields = error.get("fields") or []

        fields = self._format_error_fields(fields)

        if fields and not message:
            message = self._UNKNOWN_ERROR

        result = f"{message} {fields}"
        return result.strip()

    @staticmethod
    def _format_error_fields(fields: List[QueryErrorField]) -> str:
        fields = [field.strip() for field in fields if field.strip()]
        fields = ", ".join(fields)

        if fields:
            fields = f"(fields: {fields})"

        return fields

    def __str__(self):
        errors = [self._format_error(error) for error in self._errors]
        errors = [error for error in errors if error]

        if not errors:
            return self._EMPTY_ERRORS

        lines = ["The following errors occurred:"]

        for error in errors:
            lines.append(f"- {error}")

        return "\n".join(lines)

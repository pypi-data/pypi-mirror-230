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

from typing import Callable
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_client_execute(mocker) -> Callable:
    """Mocks the method which sends the request for `GraphQLClient`.
    If providing a `return_value`, this structure should be the `data`
    which is returned from the GraphQL request. Example:

    mocked_execute = mock_client_execute(return_value={
        "profile": {
            "profile": {
                "firstName": "Arthur"
            }
        }
    })

    client = GraphQLClient("http://api")

    result = client.execute('''
        query {
            profile {
                profile {
                    firstName
                }
            }
        }
    ''')
    """

    def func(**kwargs) -> MagicMock:
        return mocker.patch("qctrlclient.client.gql.Client.execute", **kwargs)

    return func

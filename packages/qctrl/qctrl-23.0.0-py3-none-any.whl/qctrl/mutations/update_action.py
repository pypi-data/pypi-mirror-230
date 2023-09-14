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
# pylint:disable=missing-module-docstring
from typing import Union

from gql import gql

from qctrl.queries.base import StaticQuery


class UpdateActionMutation(StaticQuery):
    """
    Updates the given Action object.
    """

    query = gql(
        """
        mutation updateActionMutation($modelId: String!, $status: ActionStatusEnum ) {
            updateAction(input: {modelId: $modelId , status: $status}) {
                action {
                    modelId
                    status
                    name
                    progress
                }
                errors {
                    fields
                    message
                }
            }
        }
        """
    )

    def _get_variable_values(
        self, action_id: Union[str, int], status: str
    ):  # pylint:disable=arguments-differ
        return {"modelId": str(action_id), "status": status}

    def _format_response(self, response: str, *_):
        return response["updateAction"]["action"]

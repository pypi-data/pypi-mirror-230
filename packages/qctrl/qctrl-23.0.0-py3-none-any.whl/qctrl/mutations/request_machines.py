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
from gql import gql
from qctrlcommons.exceptions import QctrlException

from qctrl.queries.base import StaticQuery


class RequestMachinesMutation(StaticQuery):
    """
    Request a certain amount of machines to be created for a given tenant, limited
    by the tenant's plan.
    """

    query = gql(
        """
    mutation requestMachines($minimum: Int!, $organizationId: ID!) {
        requestMachines(input: {minimum: $minimum, organizationId: $organizationId}) {
            machineRequested
            errors {
                fields
                message
            }
        }
    }
    """
    )

    def _get_variable_values(
        self, minimum: int, organization_id: str
    ):  # pylint:disable=arguments-differ
        if minimum < 1:
            raise QctrlException(
                "Number of machine(s) requested must be greater than 0."
            )
        return {"minimum": minimum, "organizationId": organization_id}

    def _format_response(self, response: str, *_):
        return response["requestMachines"]["machineRequested"]

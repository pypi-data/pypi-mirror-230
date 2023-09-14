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

from .base import StaticQuery


class TenantOnlineInstancesQuery(StaticQuery):
    """
    Retrieves the number of online instances of a specific tenant.
    """

    query = gql(
        """
        query tenantQuery($organizationId: ID!) {
            tenant(organizationId:$organizationId) {
                tenant {
                    currentInstances {
                        online
                    }
                }
                errors {
                    message
                }
            }
        }
        """
    )

    def _get_variable_values(
        self, organization_id: str
    ):  # pylint:disable=arguments-differ
        return {"organizationId": organization_id}

    def _format_response(self, response: str, *_):
        return response["tenant"]["tenant"]

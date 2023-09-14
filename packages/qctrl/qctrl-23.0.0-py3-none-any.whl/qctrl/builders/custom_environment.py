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
import logging
from functools import (
    lru_cache,
    wraps,
)
from typing import (
    Any,
    List,
    Union,
)

import inflection
import tenacity
from gql import Client
from graphql import GraphQLType
from qctrlcommons.exceptions import QctrlGqlException
from tqdm.auto import tqdm

from ..mutations import UpdateActionMutation
from ..queries import (
    MultiRefreshActionQuery,
    RefreshActionQuery,
    StartActionQuery,
    TenantOnlineInstancesQuery,
)
from .async_result import (
    AsyncResult,
    AsyncResultCollection,
)
from .custom_handlers import (
    ComplexArrayEntryHandler,
    ComplexArrayHandler,
    ComplexArrayInputHandler,
    ComplexDenseArrayHandler,
    ComplexNumberHandler,
    ComplexNumberInputHandler,
    ComplexSparseArrayHandler,
    DateTimeScalarHandler,
    GraphScalarHandler,
    JsonDictScalarHandler,
    UnixTimeScalarHandler,
)
from .graphql_utils import (
    BaseHandler,
    GraphQLEnvironment,
)
from .type_registry import TypeRegistry
from .verbosity import VerbosityEnum
from .wait import Wait

LOGGER = logging.getLogger(__name__)
ACTION_READY_STATES = ["SUCCESS", "FAILURE", "REVOKED"]


def revoke_calculation(func):
    """Decorator for wait_for_completion() function, that revokes
    the user's calculation when the user issues a KeyboardInterrupt."""

    @wraps(func)
    def revoke_action(qctrl_gql_environment, _, *async_results, **kwargs):
        try:
            func(qctrl_gql_environment, _, *async_results, **kwargs)
        except KeyboardInterrupt:
            promise = AsyncResultCollection(*async_results)
            task_failure_flag = False
            # pylint:disable=protected-access
            update_action_mutation = UpdateActionMutation(
                qctrl_gql_environment._gql_client
            )
            for (
                async_result
            ) in promise._async_results:  # pylint:disable=protected-access
                action_name = async_result.result_object.name
                action_id = async_result.result_object.action_id
                action_status = async_result.result_object.status
                if action_status not in ACTION_READY_STATES:
                    try:
                        update_action_mutation(action_id, "REVOKED")
                        print(
                            f'Your task {action_name} (action_id="{action_id}") has '
                            + "been cancelled successfully."
                        )
                    except QctrlGqlException as exc:
                        LOGGER.debug("mutation execution failed: %s", exc)
                        task_failure_flag = True
            if task_failure_flag:
                print(
                    "One or more tasks could not be cancelled."
                    + " Check activity monitor for more details."
                )
            raise

    return revoke_action


class QctrlGraphQLEnvironment(GraphQLEnvironment):
    """
    Custom GraphQLEnvironment class.
    """

    _action_selection_override = {
        "action": r"{ modelId name status errors { exception } progress }"
    }

    def __init__(
        self,
        gql_client: Client,
        type_registry_cls: type = None,
        custom_handlers: List[BaseHandler] = None,
    ):
        self._gql_client = gql_client
        super().__init__(type_registry_cls, custom_handlers)

    @lru_cache(maxsize=128)
    def field_to_attr(self, field_name: str) -> str:
        """Uses inflection to convert a GraphQL
        field name to an attribute name.

        Parameters
        ----------
        field_name : str
            The name of the GraphQL field.

        Returns
        -------
        str
            attribute name
        """
        return inflection.underscore(field_name)

    def build_mutation_query(
        self,
        mutation_name: str,
        input_type: GraphQLType,
        result_type: GraphQLType,
        data: Any,
    ) -> StartActionQuery:
        """Returns the corresponding StartActionQuery object."""
        query = StartActionQuery(
            self._gql_client, self, mutation_name, input_type, result_type, data
        )

        return query

    @revoke_calculation
    def wait_for_completion(
        self,
        refresh_query: Union[RefreshActionQuery, MultiRefreshActionQuery],
        *async_results: AsyncResult,
        verbosity: VerbosityEnum,
    ):
        """Waits until the corresponding actions are completed on the server."""
        promise = AsyncResultCollection(*async_results)
        if promise.is_completed:
            promise.finalize()

        hide_progress_bar = verbosity == VerbosityEnum.QUIET
        with tqdm(total=100, leave=False, disable=hide_progress_bar) as progress_bar:
            self.pull_results(promise, refresh_query, progress_bar, verbosity)
            progress_bar.update(max(0, progress_bar.total - progress_bar.n))
        promise.finalize()

    @tenacity.retry(
        wait=tenacity.wait_fixed(10),
        retry=tenacity.retry_if_result(
            lambda response: response["online"] != response["requested"]
        ),
    )
    def wait_for_machine_instantiation(
        self, organization_id: str, number_of_machines_requested: int
    ):
        """Waits until the requested number of machines are online."""
        number_of_machines_online = TenantOnlineInstancesQuery(self._gql_client)(
            organization_id
        )["currentInstances"]["online"]

        def machines(count: int) -> str:
            if count == 1:
                return "1 machine"
            return f"{count} machines"

        print(
            f"Current environment: {machines(number_of_machines_online)} online, "
            f"{machines(number_of_machines_requested - number_of_machines_online)} pending."
        )
        return {
            "online": number_of_machines_online,
            "requested": number_of_machines_requested,
        }

    def pull_results(
        self,
        promise: AsyncResultCollection,
        refresh_query: Union[RefreshActionQuery, MultiRefreshActionQuery],
        progress_bar: tqdm,
        verbosity: VerbosityEnum,
    ):
        """Pulls the result of the calculation."""
        _wait = Wait()
        while not promise.is_completed:
            promise.update_progress(progress_bar)
            _wait()
            # check completion
            response = refresh_query(*promise.get_action_ids())
            promise.update_data(self, response, progress_bar, verbosity)
        return promise

    def build_refresh_query(self, field_type: GraphQLType) -> RefreshActionQuery:
        """Returns a RefreshActionQuery object for
        refreshing an object populated with response data.
        """
        return RefreshActionQuery(self._gql_client, field_type)


def create_environment(gql_client: Client) -> QctrlGraphQLEnvironment:
    """Creates the custom environment object with
    all custom handlers.
    """
    return QctrlGraphQLEnvironment(
        gql_client=gql_client,
        type_registry_cls=TypeRegistry,
        custom_handlers=[
            ComplexArrayEntryHandler,
            ComplexArrayHandler,
            ComplexArrayInputHandler,
            ComplexDenseArrayHandler,
            ComplexNumberHandler,
            ComplexNumberInputHandler,
            ComplexSparseArrayHandler,
            DateTimeScalarHandler,
            GraphScalarHandler,
            JsonDictScalarHandler,
            UnixTimeScalarHandler,
        ],
    )

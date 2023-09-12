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

from typing import ContextManager

from qctrlcommons.exceptions import QctrlException
from qctrlworkflowclient import LocalRouter

from boulderopal._configuration import get_configuration


def collect_requests() -> ContextManager:
    """
    Create a context manager for executing multiple function calls over available machines.

    Most functions in Boulder Opal (for example, `boulderopal.execute_graph`) can be viewed as a
    single execution request to be scheduled for running on a remote machine.
    This context manager will collect all the requests defined within it, and then schedule
    and run them. Up to five requests can be submitted at once. If more are requested, a runtime
    error will be raised.

    The actual number of tasks that will run in parallel depends on your Boulder Opal plan and
    the number of available machines in your environment when these requests are scheduled.

    Within the context manager, the object returned from each request is a placeholder.
    When exiting, the context manager waits until all computation results are ready, meaning that
    it blocks execution. When all results are received, the placeholders are replaced with them.

    As a consequence, even if you only have a single function inside the context manager,
    but that function contains multiple Boulder Opal API calls, the context manager will still
    bundle those request if possible.

    Therefore, all the requests within the context manager must be independent from one another.
    That is, one request cannot rely on the result from the other one, or unexpected errors might
    be raised at runtime. As an example, `boulderopal.closed_loop.optimize` could send multiple
    calls to the `step` API, where each step relies on the previous step's result, triggering a
    runtime error. Therefore, it's not recommended to use `optimize` with this context manager.

    Returns
    -------
    ContextManager
        A context manager to collect and run computation requests.
    """
    router = get_configuration().get_router()
    if isinstance(router, LocalRouter):
        raise QctrlException("Collecting requests is not supported in local mode.")
    return router.enable_parallel()

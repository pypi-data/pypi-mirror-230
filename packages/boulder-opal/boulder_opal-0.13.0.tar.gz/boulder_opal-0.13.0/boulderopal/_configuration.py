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

from qctrlworkflowclient import (
    ApiRouter,
    CoreClientSettings,
    LocalRouter,
    Product,
    get_authenticated_client_for_product,
    get_default_api_url,
    get_default_cli_auth,
)
from qctrlworkflowclient.defaults import CliAuth
from qctrlworkflowclient.globals import global_value

from ._constants import INVALID_SUBSCRIPTION_ERROR
from ._verbosity import MESSAGE_PRINTER


def get_default_router() -> ApiRouter:
    """
    Return the default router that the Boulder Opal client uses.
    """
    client = get_authenticated_client_for_product(
        product_access_required="boulder-opal-cli-access",
        api_url=get_default_api_url(),
        auth=get_default_cli_auth(),
        invalid_access_error_message=INVALID_SUBSCRIPTION_ERROR,
    )
    settings = get_configuration()

    return ApiRouter(client, settings)


@global_value("BOULDER_OPAL_CONFIGURATION")
def get_configuration() -> CoreClientSettings:
    """
    Return the global Boulder Opal settings.
    """
    return CoreClientSettings(
        router=get_default_router,
        product=Product.BOULDER_OPAL,
        event_listeners=[MESSAGE_PRINTER],
    )


def configure(**kwargs):
    """
    Update the global Boulder Opal settings. See :class:`CoreClientSettings`
    for details on which fields can be updated.
    """
    configuration = get_configuration()
    configuration.update(**kwargs)


def set_api(api_url: str, oidc_url: str):
    """
    Configure Boulder Opal for API routing.

    Parameters
    ----------
    api_url : str
        URL of the GraphQL schema.
    oidc_url : str
        Base URL of the OIDC provider, e.g. Keycloak.
    """
    client = get_authenticated_client_for_product(
        product_access_required="boulder-opal-cli-access",
        api_url=api_url,
        auth=CliAuth(oidc_url),
        invalid_access_error_message=INVALID_SUBSCRIPTION_ERROR,
    )
    settings = get_configuration()

    configure(router=ApiRouter(client, settings))


def set_local(resolver: "BaseResolver"):  # type: ignore
    """
    Configure Boulder Opal for local routing.

    Parameters
    ----------
    resolver : BaseResolver
        A local implementation of a workflow resolver which uses
        a registry that implements all of the available Boulder Opal
        workflows.
    """
    configure(router=LocalRouter(resolver))


def set_organization(organization_slug: str):
    """
    Set the organization for Boulder Opal cloud calls.

    Parameters
    ----------
    organization_slug : str
        Unique slug for the organization.
    """
    configure(organization=organization_slug)

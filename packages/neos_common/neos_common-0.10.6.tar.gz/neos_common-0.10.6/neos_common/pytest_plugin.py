import typing
from unittest import mock

import fastapi
import pytest
from pytest import MonkeyPatch  # noqa: PT013

from neos_common import error
from neos_common.authorization.base import AuthorizationDependency
from neos_common.authorization.token import TokenData
from neos_common.base import ActionBase
from neos_common.client.iam_client import IAMClient


@pytest.fixture()
def _auth_patch_factory(  # noqa: PT005
    monkeypatch: MonkeyPatch,
) -> typing.Callable[[str, "AuthorizationDependency", typing.List[str]], None]:
    """Mock the check of the token.

    Generates :class:`TokenData` with given user.
    """

    def factory(
        user: str,
        authorization_dep: "AuthorizationDependency",
        resources: typing.Union[typing.List[str], None],
    ) -> None:
        async def __call_mock__(  # noqa: N807
            self,  # noqa: ANN001
            request: fastapi.Request,
            keycloak_client: str = "",  # noqa: ARG001
            config: str = "",
            signature_validator: str = "",  # noqa: ARG001
            access_validator: str = "",  # noqa: ARG001
        ) -> TokenData:
            if resources is None and self.action_resources != []:
                resource_kwargs = (
                    self.action_resources[0].resource_extractor(request)
                    if self.action_resources[0].resource_extractor
                    else {"resource_id": None}
                )
                resource = self.action_resources[0].resource.generate_from_config(
                    config,
                    self.action_resources[0].resource_type,
                    **resource_kwargs,
                )
                m = f"The principal <{user}> must have <{self.action_resources[0].action.value}> action for the resource <{resource.urn}>."  # noqa: E501
                raise error.InsufficientPermissionsError(m)
            return TokenData(user, request.headers.get("Authorization", ""), resources=resources or [])

        monkeypatch.setattr(authorization_dep, "__call__", __call_mock__)

    return factory


@pytest.fixture()
def iam_allow_factory(monkeypatch: "MonkeyPatch") -> typing.Callable[[str, typing.List[str]], None]:
    """IAM factory generator when user has permissions."""

    def factory(user: str, resources: typing.List[str]) -> None:
        monkeypatch.setattr(IAMClient, "validate_token", mock.AsyncMock(return_value=(user, resources)))

    return factory


@pytest.fixture()
def iam_deny_factory(monkeypatch: "MonkeyPatch") -> typing.Callable[[], None]:
    """IAM factory generator when user doesn't have permissions."""

    def factory() -> None:
        async def mock_validate_token(
            self,  # noqa: ANN001, ARG001
            principal: str,
            actions: typing.List[ActionBase],
            resources: typing.List[str],
            *,
            return_allowed_resources: bool,  # noqa: ARG001
        ) -> typing.List[str]:
            msg = f"The principal <{principal}> must have <{actions[0].value}> action for the resource <{resources[0]}>."  # noqa: E501
            raise error.InsufficientPermissionsError(msg)

        monkeypatch.setattr(IAMClient, "validate_token", mock_validate_token)

    return factory

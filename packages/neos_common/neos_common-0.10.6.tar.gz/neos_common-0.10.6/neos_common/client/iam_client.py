import logging
import typing
from uuid import UUID

import httpx

from neos_common import error
from neos_common.authorization.signer import KeyPair
from neos_common.base import ActionBase
from neos_common.client.base import NeosClient

logger = logging.getLogger(__name__)


class IAMClient(NeosClient):
    """Identity Access Manager client.

    Access to the resources based on the access statements that stores in access manager.
    """

    @property
    def service_name(self) -> str:
        return "Identity Access Manager"

    @property
    def known_errors(self) -> typing.Set[str]:
        return {"I002"}

    def process_response_with_mapping(self, response: httpx.Response) -> dict:
        try:
            return self.process_response(response)
        except (error.ServiceApiError, error.UnhandledServiceApiError) as exc:
            if exc.code == "A001":
                raise error.AuthorizationRequiredError(exc.debug_message) from exc
            if exc.code == "A002":
                raise error.InvalidAuthorizationError(exc.debug_message) from exc
            if exc.code == "A100":
                raise error.InsufficientPermissionsError(exc.debug_message) from exc
            if exc.code == "A102":
                raise error.InvalidResourceFormatError(exc.debug_message) from exc
            if exc.code == "A103":
                raise error.IdentityAccessManagerError(exc.debug_message) from exc
            if exc.code == "S001":
                raise error.SignatureError(exc.debug_message) from exc
            raise

    def __init__(
        self,
        host: str,
        token: typing.Union[str, None],
        key_pair: typing.Union[KeyPair, None],
    ) -> None:
        assert token is not None or key_pair is not None

        self._token = token
        self._key_pair = key_pair

        self._host = host
        self._principals = None

    @property
    def token(self) -> typing.Union[str, None]:
        return self._token

    @property
    def key_pair(self) -> typing.Union[KeyPair, None]:
        return self._key_pair

    @property
    def validate_token_url(self) -> str:
        return f"{self._host}/validate/token"

    @property
    def validate_signature_url(self) -> str:
        return f"{self._host}/validate/signature"

    async def validate_token(
        self,
        principal: UUID,
        actions: typing.List[ActionBase],
        resources: typing.List[str],
        *,
        return_allowed_resources: bool = False,
    ) -> typing.Tuple[UUID, typing.List[str]]:
        r = await self._get(
            url=self.validate_token_url,
            params={
                "principal_id": principal,
                "action": [action.value for action in actions],
                "resource": resources,
                "return_allowed_resources": return_allowed_resources,
            },
        )

        data = self.process_response_with_mapping(r)
        logger.info(data)
        return data["principal_id"], data["resources"]

    async def validate_signature(
        self,
        access_key: str,
        auth_schema: str,
        scope: str,
        challenge: str,
        signed_challenge: str,
        actions: typing.List[ActionBase],
        resources: typing.List[str],
        *,
        return_allowed_resources: bool = False,
    ) -> typing.Tuple[UUID, typing.List[str]]:
        r = await self._get(
            url=self.validate_signature_url,
            params={
                "access_key_id": access_key,
                "auth_schema": auth_schema,
                "scope": scope,
                "challenge": challenge,
                "signed_challenge": signed_challenge,
                "action": [action.value for action in actions],
                "resource": resources,
                "return_allowed_resources": return_allowed_resources,
            },
        )

        data = self.process_response_with_mapping(r)

        return data["principal_id"], data["resources"]

from typing import Optional, Union, List
from jose import jwt
from fastapi import HTTPException
from fastapi.security import SecurityScopes
from fastapi.security.api_key import APIKeyHeader
from starlette.requests import Request
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from djdantic import context
from asgiref.sync import sync_to_async
from djdantic.schemas import Error, Access, AccessToken, AccessScope
from sentry_tools import set_user, set_extra
from ..exceptions import AuthError


class JWTToken(APIKeyHeader):
    def __init__(
        self,
        *,
        name: str = 'Authorization',
        scheme_name: Optional[str] = None,
        auto_error: bool = True,
        key: Optional[str] = None,
        issuer: Optional[str] = None,
        algorithm: Union[str, List[str]] = 'ES512',
    ):
        self.key = key or settings.JWT_PUBLIC_KEY
        self.issuer = issuer or settings.JWT_ISSUER
        self.algorithms = [algorithm] if isinstance(algorithm, str) else algorithm

        super().__init__(name=name, scheme_name=scheme_name, auto_error=auto_error)

    def decode_token(self, token, audience=None):
        return jwt.decode(
            token=token,
            key=self.key,
            algorithms=self.algorithms,
            issuer=self.issuer,
            audience=audience,
            options={
                'verify_aud': bool(audience),
            },
        )

    def _set_scopes(self, access: Access, scopes: SecurityScopes):
        if not scopes.scopes:
            return

        audiences = access.token.has_audiences(scopes.scopes)
        if not audiences:
            raise HTTPException(
                status_code=403,
                detail=Error(
                    type='JWTClaimsError',
                    code='required_audience_missing',
                    message='The required scope is not included in the given token.',
                    detail=scopes.scopes,
                ),
            )

        aud_scopes = [AccessScope.from_str(audience) for audience in audiences]
        access.scopes = aud_scopes
        access.scope = aud_scopes[0]
        set_extra('access.scopes', aud_scopes)

    async def _create_access(self, token: str):
        if not token:
            raise AuthError

        access = Access(
            token=AccessToken(**self.decode_token(token.removeprefix("Bearer").strip())),
        )
        set_extra('access.token.aud', access.token.aud)

        return access

    async def get_access(self, token, scopes: Optional[SecurityScopes] = None):
        access = await self._create_access(token)

        set_user(
            {
                'id': access.user_id,
                'tenant_id': access.tenant_id,
            }
        )

        if scopes:
            self._set_scopes(access, scopes)

        context.access.set(access)

        return access

    async def __call__(self, request: Request, scopes: SecurityScopes) -> Optional[Access]:
        try:
            token = await super().__call__(request)

        except HTTPException as error:
            if error.status_code == 403:
                raise AuthError from error

            raise

        if not token:
            return

        return await self.get_access(token, scopes)


class JWTTokenDjangoPermissions(JWTToken):
    async def get_user(self, access: Access):
        try:
            return await get_user_model().objects.aget(id=access.user_id)

        except ObjectDoesNotExist as error:
            raise AuthError from error

    async def _create_access(self, token):
        access = await super()._create_access(token)
        user = await self.get_user(access)
        access.token.aud = list(await sync_to_async(user.get_all_permissions)())
        return access

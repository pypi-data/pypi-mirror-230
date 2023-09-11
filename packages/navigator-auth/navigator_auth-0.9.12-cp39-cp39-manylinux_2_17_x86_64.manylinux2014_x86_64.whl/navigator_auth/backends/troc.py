"""TROC Backend.

Troc Authentication using RNC algorithm.
"""
from typing import Optional
from collections.abc import Awaitable, Callable
from aiohttp import web
import orjson
from navigator_session import get_session, AUTH_SESSION_OBJECT
from navigator_auth.libs.cipher import Cipher
from navigator_auth.exceptions import (
    AuthException,
    AuthExpired,
    FailedAuth,
    Forbidden,
    InvalidAuth,
    UserNotFound,
)
from navigator_auth.conf import (
    AUTH_CREDENTIALS_REQUIRED,
    PARTNER_KEY,
    CYPHER_TYPE,
    AUTH_SUCCESSFUL_CALLBACKS
)
from .abstract import BaseAuthBackend
from .basic import BasicUser


class TrocToken(BaseAuthBackend):
    """TROC authentication Header."""

    user_attribute: str = "user"
    username_attribute: str = "email"
    _ident: BasicUser = BasicUser
    _description: str = "Partnership Token authentication"
    _service_name: str = "troctoken"
    _success_callbacks: Optional[list[str]] = AUTH_SUCCESSFUL_CALLBACKS
    _callbacks: Optional[list[Callable]] = None

    def __init__(
        self,
        user_attribute: str = None,
        userid_attribute: str = None,
        password_attribute: str = None,
        **kwargs,
    ):
        super().__init__(
            user_attribute,
            userid_attribute,
            password_attribute,
            **kwargs,
        )
        # forcing to use Email as Username Attribute
        self.username_attribute = "email"
        self.cypher: Cipher = None

    async def on_startup(self, app: web.Application):
        """Used to initialize Backend requirements."""
        self.cypher = Cipher(PARTNER_KEY, type=CYPHER_TYPE)
        ## Using Startup for detecting and loading functions.
        if self._success_callbacks:
            self._user_model = self._idp.user_model
            self.get_successful_callbacks()

    async def on_cleanup(self, app: web.Application):
        """Used to cleanup and shutdown any db connection."""

    async def validate_user(self, login: str = None):
        # get the user based on Model
        try:
            user = await self._idp.get_user(login)
            return user
        except UserNotFound as err:
            raise UserNotFound(f"User {login} doesn't exists") from err
        except Exception as err:
            self.logger.exception(err)
            raise

    async def get_payload(self, request: web.Request):
        try:
            if "Authorization" in request.headers:
                token = await super(TrocToken, self).get_payload(request)
            else:
                try:
                    token = request.query.get("auth", None)
                except Exception as e:  # pylint: disable=W0703
                    print(e)
                    return None
        except Exception as err:  # pylint: disable=W0703
            self.logger.exception(
                f"TrocAuth: Error getting payload: {err}"
            )
            raise
        return token

    async def authenticate(self, request):
        """Authenticate, refresh or return the user credentials."""
        try:
            token = await self.get_payload(request)
            print('TOKEN TROC: > ', token)
        except Exception as err:
            raise AuthException(
                str(err),
                status=400
            ) from err
        if not token:
            raise InvalidAuth("Token: Missing Token", status=401)
        else:
            # getting user information
            # TODO: making the validation of token and expiration
            try:
                data = orjson.loads(self.cypher.decode(token))
                self.logger.debug(
                    f"TrocToken: Decoded User data: {data!r}"
                )
            except Exception as err:
                raise InvalidAuth(f"Invalid Token: {err!s}", status=401) from err
            # making validation
            try:
                username = data[self.username_attribute]
            except KeyError as err:
                raise InvalidAuth(
                    f"Missing Email attribute: {err!s}", status=401
                ) from err
            try:
                user = await self.validate_user(login=username)
            except UserNotFound as err:
                raise UserNotFound(str(err)) from err
            except Exception as err:
                raise AuthException(err, status=500) from err
            try:
                userdata = self.get_userdata(user)
                try:
                    # merging both session objects
                    userdata[AUTH_SESSION_OBJECT] = {
                        **userdata[AUTH_SESSION_OBJECT],
                        **data,
                    }
                except Exception as err:  # pylint: disable=W0703
                    self.logger.exception(err)
                uid = user[self.username_attribute]
                username = user[self.username_attribute]
                userdata[self.session_key_property] = uid
                usr = await self.create_user(userdata[AUTH_SESSION_OBJECT])
                usr.id = uid
                usr.set(self.username_attribute, username)
                payload = {
                    self.user_property: user[self.userid_attribute],
                    self.username_attribute: username,
                    "user_id": user[self.userid_attribute],
                }
                token, exp, scheme = self._idp.create_token(data=payload)
                usr.access_token = token
                usr.token_type = scheme
                usr.expires_in = exp
                userdata['expires_in'] = exp
                userdata['token_type'] = scheme
                ### check if any callbacks exists:
                if user and self._callbacks:
                    # construir e invocar callbacks para actualizar data de usuario
                    args = {
                        "username_attribute": self.username_attribute,
                        "userid_attribute": self.userid_attribute,
                        "userdata": userdata
                    }
                    await self.auth_successful_callback(request, user, **args)
                # saving user-data into request:
                await self.remember(request, uid, userdata, usr)
                return {"token": token, **userdata}
            except Exception as err:  # pylint: disable=W0703
                self.logger.exception(f"TROC Auth: Authentication Error: {err}")
                return False

    async def check_credentials(self, request):
        """Authentication and create a session."""
        return True

    @web.middleware
    async def auth_middleware(
        self,
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
    ) -> web.StreamResponse:
        """
        Partner Auth Middleware.
        Description: Basic Authentication for Partner Token Auth.
        """
        # avoid check system routes
        if await self.verify_exceptions(request):
            return await handler(request)
        self.logger.debug(f"MIDDLEWARE: {self.__class__.__name__}")
        try:
            token = await self.get_payload(request)
            _, payload = self._idp.decode_token(code=token)
            # _, payload = decode_token(request)
            if payload:
                ## check if user has a session:
                # load session information
                session = await get_session(
                    request, payload, new=False, ignore_cookie=True
                )
                if not session and AUTH_CREDENTIALS_REQUIRED is True:
                    raise self.Unauthorized(
                        reason="There is no Session or Authentication is missing"
                    )
                try:
                    request.user = await self.get_session_user(session)
                    request["authenticated"] = True
                except UnboundLocalError:
                    pass
                except Exception as ex:  # pylint: disable=W0703
                    self.logger.error(f"Missing User Object from Session: {ex}")
            else:
                if AUTH_CREDENTIALS_REQUIRED is True:
                    raise self.Unauthorized(
                        reason="There is no Session or Authentication is missing"
                    )
        except Forbidden as err:
            self.logger.error("TROC Auth: Access Denied")
            raise self.ForbiddenAccess(reason=err.message)
        except AuthExpired as err:
            self.logger.error("TROC Auth: Auth Credentials were expired")
            raise self.Unauthorized(reason=err.message)
        except FailedAuth as err:
            raise self.ForbiddenAccess(reason=err.message)
        except AuthException as err:
            self.logger.error("Auth:Invalid Signature or Authentication Failed")
            raise self.ForbiddenAccess(reason=err.message)
        return await handler(request)

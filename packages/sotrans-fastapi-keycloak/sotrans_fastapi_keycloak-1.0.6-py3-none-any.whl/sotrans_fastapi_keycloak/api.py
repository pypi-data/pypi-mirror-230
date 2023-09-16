import collections
import functools
import json
import fastapi
import requests

from json import JSONDecodeError
from collections.abc import Callable
from typing import Any, Union
from urllib.parse import urlencode
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from jose.exceptions import JWTClaimsError
from pydantic import BaseModel
from requests import Response

from sotrans_fastapi_keycloak.exceptions import (
    ConfigureTOTPException,
    KeycloakError,
    MandatoryActionException,
    UpdatePasswordException,
    UpdateProfileException,
    UpdateUserLocaleException,
    UserNotFound,
    VerifyEmailException,
)
from sotrans_fastapi_keycloak.model import (
    HTTPMethod,
    KeycloakGroupModel,
    KeycloakIdentityProviderModel,
    KeycloakRoleModel,
    KeycloakTokenModel,
    KeycloakUserModel,
    OIDCUserModel,
)
from sotrans_fastapi_keycloak.role import Role


def is_response_valid(response: Response) -> bool:
    """Check if response status code in valid range function

    :param response: response to check
    :return: whether response is valid or not
    """
    return 100 <= response.status_code < 300


def raise_from_response(response: Response):
    """Raise error from response function

    :param response: response, to get data from
    """
    try:
        raise KeycloakError(status_code=response.status_code, reason=response.json())
    except JSONDecodeError:
        raise KeycloakError(
            status_code=response.status_code,
            reason=response.content.decode("utf-8"),
        )


def result_or_error(
    response_model: type[BaseModel] = None, is_list: bool = False
) -> list[BaseModel] or BaseModel or KeycloakError:
    """Decorator used to ease the handling of responses from Keycloak.

    Args:
        response_model (type[BaseModel]): Object that should be returned based on the payload
        is_list (bool): True if the return value should be a list of the response model provided

    Returns:
        BaseModel or list[BaseModel]: Based on the given signature and response circumstances

    Raises:
        KeycloakError: If the resulting response is not a successful HTTP-Code (>299)

    Notes:
        - Keycloak sometimes returns empty payloads but describes the error in its content (byte encoded)
          which is why this function checks for JSONDecode exceptions.
        - Keycloak often does not expose the real error for security measures. You will most likely encounter:
          {'error': 'unknown_error'} as a result. If so, please check the logs of your Keycloak instance to get error
          details, the RestAPI doesn't provide any.
    """

    def inner(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            def create_list(json_data: list[dict]):
                return [response_model.model_validate(entry) for entry in json_data]

            def create_object(json_data: dict):
                return response_model.model_validate(json_data)

            result: Response = f(*args, **kwargs)  # The actual call

            if (
                type(result) != Response
            ):  # If the object given is not a response object, directly return it.
                return result

            if is_response_valid(result):  # Successful
                if response_model is None:  # No model given
                    try:
                        return result.json()
                    except JSONDecodeError:
                        return fastapi.Response(status_code=result.status_code)
                else:  # Response model given
                    if is_list:
                        return create_list(result.json())
                    else:
                        return create_object(result.json())
            else:  # Not Successful, forward status code and error
                raise_from_response(result)

        return wrapper

    return inner


def  get_keycloak_user_model(model: BaseModel) -> dict[str, Any]:
    """Dump pydantic user model to keycloak representation (i.e. move all custom fields to attributes)

    Args:
        model: model to dump

    Returns: dict model representation
    """
    return (
        model.model_dump_keycloak()
        if hasattr(model, "model_dump_keycloak")
        else model.model_dump(exclude_unset=True)
    )

def  get_keycloak_user_model_json(model: BaseModel) -> str:
    """Dump pydantic user model to keycloak representation (i.e. move all custom fields to attributes)

    Args:
        model: model to dump

    Returns: str model representation
    """
    return (
        model.model_dump_json_keycloak()
        if hasattr(model, "model_dump_json_keycloak")
        else model.model_dump_json(exclude_unset=True)
    )


class FastAPIKeycloak:
    """Instance to wrap the Keycloak API with FastAPI

    Attributes: _admin_token (KeycloakToken): A KeycloakToken instance, containing the access token that is used for
    any admin related request

    Example:
        ```python
        app = FastAPI()
        idp = KeycloakFastAPI(
            server_url="https://auth.some-domain.com/auth",
            client_id="some-test-client",
            client_secret="some-secret",
            admin_client_secret="some-admin-cli-secret",
            realm="Test",
            callback_uri=f"http://localhost:8081/callback"
        )
        idp.add_swagger_config(app)
        ```
    """

    _admin_token: str

    def __init__(
        self,
        server_url: str,
        client_id: str,
        client_secret: str,
        realm: str,
        admin_client_secret: str,
        callback_uri: str,
        admin_client_id: str = "admin-cli",
        timeout: int = 10,
        user_type: type[BaseModel] = KeycloakUserModel,
        oidc_user_type: type[BaseModel] = OIDCUserModel,
        roles: dict[str, Role] | None = None,
    ):
        """FastAPIKeycloak constructor

        Args:
            server_url (str): The URL of the Keycloak server, with `/auth` suffix
            client_id (str): The id of the client used for users
            client_secret (str): The client secret
            realm (str): The realm (name)
            admin_client_id (str): The id for the admin client, defaults to 'admin-cli'
            admin_client_secret (str): Secret for the `admin-cli` client
            callback_uri (str): Callback URL of the instance, used for auth flows. Must match at least one
                `Valid Redirect URIs` of Keycloak and should point to an endpoint that utilizes the authorization_code flow.
            timeout (int): Timeout in seconds to wait for the server
            user_type (type): UserModel type, which is used in user management methods
            oidc_user_type (type): OIDCUserModel type, which specifies schema for user info, get from token
        """
        self._user_model = user_type
        self._oidc_user_type = oidc_user_type

        self.roles = roles or {}

        self.server_url = server_url
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.admin_client_id = admin_client_id
        self.admin_client_secret = admin_client_secret
        self.callback_uri = callback_uri
        self.timeout = timeout
        self._get_admin_token()  # Requests an admin access token on startup

    @property
    def admin_token(self):
        """Holds an AccessToken for the `admin-cli` client

        Returns:
            KeycloakTokenModel: A token, valid to perform admin actions

        Notes:
            - This might result in an infinite recursion if something unforeseen goes wrong
        """
        if self.token_is_valid(token=self._admin_token):
            return self._admin_token
        self._get_admin_token()
        return self.admin_token

    @admin_token.setter
    def admin_token(self, value: str):
        """Setter for the admin_token

        Args:
            value (str): An access Token

        Returns:
            None: Inplace method, updates the _admin_token
        """
        decoded_token = self._decode_token(token=value)
        if (
            not decoded_token.get("resource_access")
            or not decoded_token.get("resource_access").get("realm-management")
            or not decoded_token.get("resource_access").get("account")
        ):
            raise AssertionError(
                """The access required was not contained in the access token for the `admin-cli`.
                Possibly a Keycloak misconfiguration. Check if the admin-cli client has `Full Scope Allowed`
                and that the `Service Account Roles` contain all roles from `account` and `realm_management`"""
            )
        self._admin_token = value

    def add_swagger_config(self, app: FastAPI):
        """Adds the client id and secret securely to the swagger ui.
        Enabling Swagger ui users to perform actions they usually need the client credentials, without exposing them.

        Args:
            app (FastAPI): Optional FastAPI app to add the config to swagger

        Returns:
            None: Inplace method
        """
        app.swagger_ui_init_oauth = {
            "usePkceWithAuthorizationCodeGrant": True,
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
        }

    @functools.cached_property
    def user_auth_scheme(self) -> OAuth2PasswordBearer:
        """Returns the auth scheme to register the endpoints with swagger

        Returns:
            OAuth2PasswordBearer: Auth scheme for swagger
        """
        return OAuth2PasswordBearer(tokenUrl=self.token_uri)

    def get_current_user(
        self, required_role_names: list[str] = None, extra_fields: list[str] = None
    ) -> Callable[[str], BaseModel]:
        """Returns the current user based on an access token in the HTTP-header. Optionally verifies roles are possessed
        by the user

        Args:
            required_role_names list[str]: list of role names required for this endpoint
            extra_fields list[str]: The names of the additional fields you need that are encoded in JWT

        Returns:
            Callable[[str], OIDCUser]: Dependency method which returns the decoded JWT content

        Raises:
            ExpiredSignatureError: If the token is expired (exp > datetime.now())
            JWTError: If decoding fails or the signature is invalid
            JWTClaimsError: If any claim is invalid
            HTTPException: If any role required is not contained within the roles of the users
        """

        def current_user(token: str = Depends(self.user_auth_scheme)) -> BaseModel:
            """Decodes and verifies a JWT to get the current user

            Args:
                token OAuth2PasswordBearer: Access token in `Authorization` HTTP-header

            Returns:
                self._oidc_user_type: Decoded JWT content

            Raises:
                ExpiredSignatureError: If the token is expired (exp > datetime.now())
                JWTError: If decoding fails or the signature is invalid
                JWTClaimsError: If any claim is invalid
                HTTPException: If any role required is not contained within the roles of the users
            """
            decoded_token = self._decode_token(token=token, audience="account")
            user = self._oidc_user_type.model_validate(decoded_token)

            if required_role_names and not self.check_roles(
                user.roles, required_role_names
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Roles {required_role_names} is required to perform this action",
                )

            if extra_fields:
                for field in extra_fields:
                    user.extra_fields[field] = decoded_token.get(field, None)

            return user

        return current_user

    @functools.cached_property
    def open_id_configuration(self) -> dict:
        """Returns Keycloak Open ID Connect configuration

        Returns:
            dict: Open ID Configuration
        """
        response = requests.get(
            url=f"{self.realm_uri}/.well-known/openid-configuration",
            timeout=self.timeout,
        )
        if not is_response_valid(response):
            raise KeycloakError(
                status_code=response.status_code,
                reason="Cant get OpenID configuration. Probably passed wrong server_url "
                f"'{self.server_url}' or realm '{self.realm}'.",
            )
        return response.json()

    def proxy(
        self,
        relative_path: str,
        method: HTTPMethod,
        additional_headers: dict = None,
        payload: dict = None,
    ) -> Response:
        """Proxies a request to Keycloak and automatically adds the required Authorization header. Should not be
        exposed under any circumstances. Grants full API admin access.

        Args:

            relative_path (str): The relative path of the request.
            Requests will be sent to: `[server_url]/[relative_path]`
            method (HTTPMethod): The HTTP-verb to be used
            additional_headers (dict): Optional headers besides the Authorization to add to the request
            payload (dict): Optional payload to send

        Returns:
            Response: Proxied response

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        if additional_headers is not None:
            headers = {**headers, **additional_headers}

        return requests.request(
            method=method.name,
            url=f"{self.server_url}{relative_path}",
            data=json.dumps(payload),
            headers=headers,
            timeout=self.timeout,
        )

    def _get_admin_token(self) -> None:
        """Exchanges client credentials (admin-cli) for an access token.

        Returns:
            None: Inplace method that updated the class attribute `_admin_token`

        Raises:
            KeycloakError: If fetching an admin access token fails,
            or the response does not contain an access_token at all

        Notes:
            - Is executed on startup and may be executed again if the token validation fails
        """
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": self.admin_client_id,
            "client_secret": self.admin_client_secret,
            "grant_type": "client_credentials",
        }
        response = requests.post(
            url=self.token_uri, headers=headers, data=data, timeout=self.timeout
        )
        if not is_response_valid(response):
            raise_from_response(response)

        try:
            self.admin_token = response.json()["access_token"]
        except JSONDecodeError as e:
            raise KeycloakError(
                reason=response.content.decode("utf-8"),
                status_code=response.status_code,
            ) from e
        except KeyError as e:
            raise KeycloakError(
                reason=f"The response did not contain an access_token: {response.json()}",
                status_code=403,
            ) from e

    @functools.cached_property
    def public_key(self) -> str:
        """Returns the Keycloak public key

        Returns:
            str: Public key for JWT decoding
        """
        response = requests.get(url=self.realm_uri, timeout=self.timeout)
        public_key = response.json()["public_key"]
        return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"

    def _perform_user_roles_operation(
        self, roles: list[str], user_id: str, method: HTTPMethod
    ):
        keycloak_roles = self.get_roles(roles)
        if len(keycloak_roles) == 0:
            raise HTTPException(
                status_code=404, detail=f"None of the roles {roles} is not found"
            )

        result = self._admin_request(
            url=f"{self.users_uri}/{user_id}/role-mappings/realm",
            data=[role.__dict__ for role in keycloak_roles],
            method=method,
        )
        if result.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        return result

    @result_or_error()
    def add_user_roles(self, roles: list[str], user_id: str) -> fastapi.Response:
        """Adds roles to a specific user

        Args:
            roles list[str]: Roles to add (name)
            user_id str: ID of the user the roles should be added to

        Returns:
            fastapi.Response: successfully operation response

        Raises:
            HTTPException(404): If user with specified id not found
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._perform_user_roles_operation(roles, user_id, HTTPMethod.POST)

    @result_or_error()
    def remove_user_roles(self, roles: list[str], user_id: str) -> fastapi.Response:
        """Removes roles from a specific user

        Args:
            roles list[str]: Roles to remove (name)
            user_id str: ID of the user the roles should be removed from

        Returns:
            fastapi.Response: successfully operation response

        Raises:
            HTTPException(404): If user with specified id not found
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._perform_user_roles_operation(roles, user_id, HTTPMethod.DELETE)

    @result_or_error(response_model=KeycloakRoleModel, is_list=True)
    def get_roles(self, role_names: list[str]) -> list[Any] | None:
        """Returns full entries of Roles based on role names

        Args:
            role_names list[str]: Roles that should be looked up (names)

        Returns:
             list[KeycloakRoleModel]: Full entries stored at Keycloak. Or None if the list of requested roles is None

        Notes:
            - The Keycloak RestAPI will only identify RoleRepresentations that
              use name AND id which is the only reason for existence of this function

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        if role_names is None:
            return
        roles = self.get_all_roles()
        return list(filter(lambda role: role.name in role_names, roles))

    @result_or_error(response_model=KeycloakRoleModel, is_list=True)
    def get_user_roles(self, user_id: str) -> list[KeycloakRoleModel]:
        """Gets all roles of a user

        Args:
            user_id (str): ID of the user of interest

        Returns:
            list[KeycloakRoleModel]: All roles possessed by the user

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.users_uri}/{user_id}/role-mappings/realm", method=HTTPMethod.GET
        )

    @result_or_error(response_model=KeycloakRoleModel)
    def create_role(self, role_name: str) -> KeycloakRoleModel:
        """Create a role on the realm

        Args:
            role_name (str): Name of the new role

        Returns:
            KeycloakRoleModel: If creation succeeded, else it will return the error

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        response = self._admin_request(
            url=self.roles_uri, data={"name": role_name}, method=HTTPMethod.POST
        )
        if response.status_code == 201:
            return self.get_roles(role_names=[role_name])[0]
        else:
            return response

    @result_or_error(response_model=KeycloakRoleModel, is_list=True)
    def get_all_roles(self, skip: int = 0, limit: int = 0) -> list[KeycloakRoleModel]:
        """Get all roles of the Keycloak realm

        Args:
            skip: paging offset
            limit: maximum results count

        Returns:
            list[KeycloakRoleModel]: All roles of the realm

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.roles_uri}?first={skip}&max={limit}", method=HTTPMethod.GET
        )

    @result_or_error()
    def delete_role(self, role_name: str) -> dict:
        """Deletes a role on the realm

        Args:
            role_name (str): The role (name) to delete

        Returns:
            dict: Proxied response payload

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.roles_uri}/{role_name}",
            method=HTTPMethod.DELETE,
        )

    def check_roles(
        self, available_role_names: list[str], required_role_names: list[str]
    ) -> bool:
        # O(n)
        required_roles = [
            self.roles.get(role_name, Role()) for role_name in required_role_names
        ]
        # O(m)
        user_roles = [
            self.roles.get(role_name, Role()) for role_name in available_role_names
        ]

        # O(n * m * k), can be slightly optimized using checking firstly LCA of all roles.
        # but, considering the fact that n, m ~ 1-2 and roles tree is very simple, not needed
        for role in required_roles:
            if not any([user_role.check_access(role) for user_role in user_roles]):
                return False
        return True

    @result_or_error(response_model=KeycloakGroupModel, is_list=True)
    def get_all_groups(
        self, skip: int = 0, limit: int = 20
    ) -> list[KeycloakGroupModel]:
        """Get all base groups of the Keycloak realm

        Args:
            skip: paging offset
            limit: maximum results count

        Returns:
            list[KeycloakGroupModel]: All base groups of the realm

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.groups_uri}?first={skip}&max={limit}", method=HTTPMethod.GET
        )

    @result_or_error(response_model=KeycloakGroupModel, is_list=True)
    def get_groups(self, group_names: list[str]) -> list[Any] | None:
        """Returns full entries of base Groups based on group names

        Args:
            group_names (list[str]): Groups that should be looked up (names)

        Returns:
            list[KeycloakGroupModel]: Full entries stored at Keycloak. Or None if the list of requested groups is None

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        if group_names is None:
            return
        groups = self.get_all_groups()
        return list(filter(lambda group: group.name in group_names, groups))

    def get_subgroups(self, group: KeycloakGroupModel, path: str):
        """Utility function to iterate through nested group structures

        Args:
            group (KeycloakGroupModel): Group Representation
            path (str): Subgroup path

        Returns:
            KeycloakGroupModel: Keycloak group representation or none if not exists
        """
        for subgroup in group.subGroups:
            if subgroup.path == path:
                return subgroup
            elif subgroup.subGroups:
                for subgroup in group.subGroups:
                    if subgroups := self.get_subgroups(subgroup, path):
                        return subgroups
        # Went through the tree without hits
        return None

    @result_or_error(response_model=KeycloakGroupModel)
    def get_group_by_path(
        self, path: str, search_in_subgroups=True
    ) -> KeycloakGroupModel or None:
        """Return Group based on path

        Args:
            path (str): Path that should be looked up
            search_in_subgroups (bool): Whether to search in subgroups

        Returns:
            KeycloakGroupModel: Full entries stored at Keycloak. Or None if the path not found

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        groups = self.get_all_groups()

        for group in groups:
            if group.path == path:
                return group
            elif search_in_subgroups and group.subGroups:
                for group in group.subGroups:
                    if group.path == path:
                        return group
                    res = self.get_subgroups(group, path)
                    if res is not None:
                        return res

    @result_or_error(response_model=KeycloakGroupModel)
    def get_group(self, group_id: str) -> KeycloakGroupModel or None:
        """Return Group based on group id

        Args:
            group_id (str): Group id to be found

        Returns:
             KeycloakGroupModel: Keycloak object by id. Or None if the id is invalid

        Notes:
            - The Keycloak RestAPI will only identify GroupRepresentations that
              use name AND id which is the only reason for existence of this function

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.groups_uri}/{group_id}",
            method=HTTPMethod.GET,
        )

    @result_or_error(response_model=KeycloakGroupModel)
    def create_group(
        self, group_name: str, parent: Union[KeycloakGroupModel, str] = None
    ) -> KeycloakGroupModel:
        """Create a group on the realm

        Args:
            group_name (str): Name of the new group
            parent (Union[KeycloakGroupModel, str]): Can contain an instance or object id

        Returns:
            KeycloakGroupModel: If creation succeeded, else it will return the error

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """

        # If it's an object id get an instance of the object
        if isinstance(parent, str):
            parent = self.get_group(parent)

        if parent is not None:
            groups_uri = f"{self.groups_uri}/{parent.id}/children"
            path = f"{parent.path}/{group_name}"
        else:
            groups_uri = self.groups_uri
            path = f"/{group_name}"

        response = self._admin_request(
            url=groups_uri, data={"name": group_name}, method=HTTPMethod.POST
        )
        if response.status_code == 201:
            return self.get_group_by_path(path=path, search_in_subgroups=True)
        else:
            return response

    @result_or_error()
    def delete_group(self, group_id: str) -> dict:
        """Deletes a group on the realm

        Args:
            group_id (str): The group (id) to delete

        Returns:
            dict: Proxied response payload

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.groups_uri}/{group_id}",
            method=HTTPMethod.DELETE,
        )

    @result_or_error()
    def add_user_group(self, user_id: str, group_id: str) -> dict:
        """Add group to a specific user

        Args:
            user_id (str): ID of the user the group should be added to
            group_id (str): Group to add (id)

        Returns:
            dict: Proxied response payload

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.users_uri}/{user_id}/groups/{group_id}", method=HTTPMethod.PUT
        )

    @result_or_error(response_model=KeycloakGroupModel, is_list=True)
    def get_user_groups(self, user_id: str) -> list[KeycloakGroupModel]:
        """Gets all groups of a user

        Args:
            user_id (str): ID of the user of interest

        Returns:
            list[KeycloakGroupModel]: All groups possessed by the user

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.users_uri}/{user_id}/groups",
            method=HTTPMethod.GET,
        )

    @result_or_error()
    def remove_user_group(self, user_id: str, group_id: str) -> dict:
        """Remove group from a specific user

        Args:
            user_id str: ID of the user the groups should be removed from
            group_id str: Group to remove (id)

        Returns:
            dict: Proxied response payload

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.users_uri}/{user_id}/groups/{group_id}",
            method=HTTPMethod.DELETE,
        )

    def create_user(
        self,
        model: BaseModel,
        enabled: bool = True,
        initial_roles: list[str] = None,
        send_email_verification: bool = True,
        attributes: dict[str, Any] = None,
    ):
        """

        Args:
            model (AnyUserCreateModel): User creation info
            initial_roles (list[str]): The roles the user should possess. Defaults to `None`
            enabled (bool): True if the user should be able to be used. Defaults to `True`
            send_email_verification (bool): If true, the email verification will be added as a required
                                            action and the email triggered - if the user was created successfully.
                                            Defaults to `True`
            attributes (dict): attributes of new user

        Returns:
            self._user_model: If the creation succeeded

        Notes:
            - Also triggers the email verification email

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """

        @result_or_error(response_model=self._user_model)
        def impl():
            if model.password is None:
                raise TypeError("User Model should contain password")

            data = {
                "enabled": enabled,
                "credentials": [
                    {"temporary": False, "type": "password", "value": model.password}
                ],
                "requiredActions": [
                    "VERIFY_EMAIL" if send_email_verification else None
                ],
                "attributes": attributes,
            }
            model.password = None
            data.update(get_keycloak_user_model(model))

            response = self._admin_request(
                url=self.users_uri, data=data, method=HTTPMethod.POST
            )
            if response.status_code != 201:
                return response
            user = self.get_user(
                query=f"username={model.username if hasattr(model, 'username') else model.email}"
            )
            if send_email_verification:
                self.send_email_verification(user.id)
            if initial_roles:
                self.add_user_roles(initial_roles, user.id)
                user = self.get_user(user_id=user.id)
            return user

        return impl()

    @result_or_error()
    def change_password(
        self, user_id: str, new_password: str, temporary: bool = False
    ) -> dict:
        """Exchanges a users' password.

        Args:
            temporary (bool): If True, the password must be changed on the first login
            user_id (str): The user ID of interest
            new_password (str): The new password

        Returns:
            dict: Proxied response payload

        Notes:
            - Possibly should be extended by an old password check

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        credentials = {
            "temporary": temporary,
            "type": "password",
            "value": new_password,
        }
        return self._admin_request(
            url=f"{self.users_uri}/{user_id}/reset-password",
            data=credentials,
            method=HTTPMethod.PUT,
        )

    @result_or_error()
    def send_email_verification(self, user_id: str) -> dict:
        """Sends the email to verify the email address

        Args:
            user_id (str): The user ID of interest

        Returns:
            dict: Proxied response payload

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.users_uri}/{user_id}/send-verify-email",
            method=HTTPMethod.PUT,
        )

    def get_user(self, user_id: str = None, query: str = ""):
        """Queries the keycloak API for a specific user either based on its ID or any **native** attribute

        Args:
            user_id (str): The user ID of interest
            query: Query string. e.g. `email=testuser@codespecialist.com` or `username=code_specialist`

        Returns:
            User: If the user was found

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """

        @result_or_error(response_model=self._user_model)
        def impl():
            if user_id is None:
                response = self._admin_request(
                    url=f"{self.users_uri}?{query}", method=HTTPMethod.GET
                )
                if not response.json():
                    raise UserNotFound(
                        status_code=status.HTTP_404_NOT_FOUND,
                        reason=f"User query with filters of [{query}] did no match any users",
                    )
                return self._user_model(**response.json()[0])
            else:
                response = self._admin_request(
                    url=f"{self.users_uri}/{user_id}", method=HTTPMethod.GET
                )
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    raise UserNotFound(
                        status_code=status.HTTP_404_NOT_FOUND,
                        reason=f"User with user_id[{user_id}] was not found",
                    )
                json_dict = response.json()
                print(json_dict)
                return self._user_model(**json_dict)

        return impl()

    def update_user(self, user_id: str, user: BaseModel):
        """Updates a user. Requires the whole object.

        Args:
            user_id (str): id of updating user
            user (AnyUserUpdateModel): The (new) user info object

        Returns:
            User: The updated user

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)

        Notes: - You may alter any aspect of the user object, also the requiredActions for instance. There is no
        explicit function for updating those as it is a user update in essence
        """

        @result_or_error(response_model=self._user_model)
        def impl():
            def update(d, u):
                for k, v in u.items():
                    if isinstance(v, collections.abc.Mapping):
                        d[k] = update(d.get(k, {}), v)
                    else:
                        d[k] = v
                return d

            # merge old and new user data to fix Keycloak bugs
            user_data = get_keycloak_user_model(self.get_user(user_id))
            updated_user_data = get_keycloak_user_model(user)
            update(user_data, updated_user_data)
            response = self._admin_request(
                url=f"{self.users_uri}/{user_id}", data=user_data, method=HTTPMethod.PUT
            )
            if response.status_code == 204:  # Update successful
                return self.get_user(user_id=user_id)
            return response

        return impl()

    @result_or_error()
    def delete_user(self, user_id: str) -> dict:
        """Deletes a user

        Args:
            user_id (str): The user ID of interest

        Returns:
            dict: Proxied response payload

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(
            url=f"{self.users_uri}/{user_id}", method=HTTPMethod.DELETE
        )

    def get_all_users(
        self, skip: int = 0, limit: int = 20, query: str | None = None
    ) -> list[KeycloakUserModel]:
        """Returns all users of the realm

        Args:
            skip: paging offset
            limit: maximum results count
            query: users find query

        Returns:
            list[UserT]: All Keycloak users of the realm

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """

        @result_or_error(response_model=self._user_model, is_list=True)
        def impl():
            url = f"{self.users_uri}?first={skip}&max={limit}"
            if query is not None:
                url += f"&q={query}"
            return self._admin_request(url=url, method=HTTPMethod.GET)

        return impl()

    def get_identity_providers(self) -> list[KeycloakIdentityProviderModel]:
        """Returns all configured identity Providers

        Returns:
            list[KeycloakIdentityProviderModel]: All configured identity providers

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        return self._admin_request(url=self.providers_uri, method=HTTPMethod.GET).json()

    @result_or_error(response_model=KeycloakTokenModel)
    def user_login(self, username: str, password: str) -> KeycloakTokenModel:
        """Models the password OAuth2 flow. Exchanges username and password for an access token. Will raise detailed
        errors if login fails due to requiredActions

        Args:
            username (str): Username used for login
            password (str): Password of the user

        Returns:
            KeycloakTokenModel: If the exchange succeeds

        Raises:
            HTTPException: If the credentials did not match any user
            MandatoryActionException: If the login is not possible due to mandatory actions
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299, != 400, != 401)
            UpdateUserLocaleException: If the credentials we're correct but the has requiredActions of which the first
            one is to update his locale
            ConfigureTOTPException: If the credentials we're correct but the has requiredActions of which the first one
            is to configure TOTP
            VerifyEmailException: If the credentials we're correct but the has requiredActions of which the first one
            is to verify his email
            UpdatePasswordException: If the credentials we're correct but the has requiredActions of which the first one
            is to update his password
            UpdateProfileException: If the credentials we're correct but the has requiredActions of which the first one
            is to update his profile

        Notes:
            - To avoid calling this multiple times, you may want to check all requiredActions of the user if it fails
            due to a (sub)instance of an MandatoryActionException
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": username,
            "password": password,
            "grant_type": "password",
        }
        response = requests.post(
            url=self.token_uri, headers=headers, data=data, timeout=self.timeout
        )
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid user credentials")
        if response.status_code == 400:
            user = self.get_user(query=f"username={username}")
            if len(user.requiredActions) > 0:
                reason = user.requiredActions[0]
                exception = {
                    "update_user_locale": UpdateUserLocaleException(),
                    "CONFIGURE_TOTP": ConfigureTOTPException(),
                    "VERIFY_EMAIL": VerifyEmailException(),
                    "UPDATE_PASSWORD": UpdatePasswordException(),
                    "UPDATE_PROFILE": UpdateProfileException(),
                }.get(
                    reason,  # Try to return the matching exception
                    # On custom or unknown actions return a MandatoryActionException by default
                    MandatoryActionException(
                        detail=f"This user can't login until the following action has been "
                        f"resolved: {reason}"
                    ),
                )
                raise exception
        return response

    @result_or_error(response_model=KeycloakTokenModel)
    def exchange_authorization_code(
        self, session_state: str, code: str
    ) -> KeycloakTokenModel:
        """Models the authorization code OAuth2 flow. Opening the URL provided by `login_uri` will result in a
        callback to the configured callback URL. The callback will also create a session_state and code query
        parameter that can be exchanged for an access token.

        Args:
            session_state (str): Salt to reduce the risk of successful attacks
            code (str): The authorization code

        Returns:
            KeycloakTokenModel: If the exchange succeeds

        Raises:
            KeycloakError: If the resulting response is not a successful HTTP-Code (>299)
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "session_state": session_state,
            "grant_type": "authorization_code",
            "redirect_uri": self.callback_uri,
        }
        return requests.post(
            url=self.token_uri, headers=headers, data=data, timeout=self.timeout
        )

    def _admin_request(
        self,
        url: str,
        method: HTTPMethod,
        data: Any = None,
        json_str: str = None,
        content_type: str = "application/json",
    ) -> Response:
        """Private method that is the basis for any requests requiring admin access to the api. Will append the
        necessary `Authorization` header

        Args:
            url (str): The URL to be called
            method (HTTPMethod): The HTTP verb to be used
            data (dict): The payload of the request
            json_str (str): The payload of the request in str json form
            content_type (str): The content type of the request

        Returns:
            Response: Response of Keycloak
        """
        headers = {
            "Content-Type": content_type,
            "Authorization": f"Bearer {self.admin_token}",
        }
        if json_str:
            return requests.request(
                method=method.name,
                url=url,
                data=json_str,
                headers=headers,
                timeout=self.timeout,
            )
        if isinstance(data, BaseModel):
            return requests.request(
                method=method.name,
                url=url,
                data=data.model_dump_json(),
                headers=headers,
                timeout=self.timeout,
            )
        else:
            return requests.request(
                method=method.name,
                url=url,
                data=json.dumps(data),
                headers=headers,
                timeout=self.timeout,
            )

    @functools.cached_property
    def login_uri(self):
        """The URL for users to login on the realm. Also adds the client id and the callback."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.callback_uri,
        }
        return f"{self.authorization_uri}?{urlencode(params)}"

    @functools.cached_property
    def authorization_uri(self):
        """The authorization endpoint URL"""
        return self.open_id_configuration.get("authorization_endpoint")

    @functools.cached_property
    def token_uri(self):
        """The token endpoint URL"""
        return self.open_id_configuration.get("token_endpoint")

    @functools.cached_property
    def logout_uri(self):
        """The logout endpoint URL"""
        return self.open_id_configuration.get("end_session_endpoint")

    @functools.cached_property
    def realm_uri(self):
        """The realm's endpoint URL"""
        return f"{self.server_url}/realms/{self.realm}"

    @functools.cached_property
    def users_uri(self):
        """The users endpoint URL"""
        return self.admin_uri(resource="users")

    @functools.cached_property
    def roles_uri(self):
        """The roles endpoint URL"""
        return self.admin_uri(resource="roles")

    @functools.cached_property
    def groups_uri(self):
        """The groups endpoint URL"""
        return self.admin_uri(resource="groups")

    @functools.cached_property
    def _admin_uri(self):
        """The base endpoint for any admin related action"""
        return f"{self.server_url}/admin/realms/{self.realm}"

    @functools.cached_property
    def _open_id(self):
        """The base endpoint for any openid connect config info"""
        return f"{self.realm_uri}/protocol/openid-connect"

    @functools.cached_property
    def providers_uri(self):
        """The endpoint that returns all configured identity providers"""
        return self.admin_uri(resource="identity-provider/instances")

    def admin_uri(self, resource: str):
        """Returns a admin resource URL"""
        return f"{self._admin_uri}/{resource}"

    def open_id(self, resource: str):
        """Returns a openid connect resource URL"""
        return f"{self._open_id}/{resource}"

    def token_is_valid(self, token: str, audience: str = None) -> bool:
        """Validates an access token, optionally also its audience

        Args:
            token (str): The token to be verified
            audience (str): Optional audience. Will be checked if provided

        Returns:
            bool: True if the token is valid
        """
        try:
            self._decode_token(token=token, audience=audience)
            return True
        except (ExpiredSignatureError, JWTError, JWTClaimsError):
            return False

    def _decode_token(
        self, token: str, options: dict = None, audience: str = None
    ) -> dict:
        """Decodes a token, verifies the signature by using Keycloak public key. Optionally verifying the audience

        Args:
            token (str):
            options (dict):
            audience (str): Name of the audience, must match the audience given in the token

        Returns:
            dict: Decoded JWT

        Raises:
            ExpiredSignatureError: If the token is expired (exp > datetime.now())
            JWTError: If decoding fails or the signature is invalid
            JWTClaimsError: If any claim is invalid
        """
        if options is None:
            options = {
                "verify_signature": True,
                "verify_aud": audience is not None,
                "verify_exp": True,
            }
        return jwt.decode(
            token=token, key=self.public_key, options=options, audience=audience
        )

    def __str__(self):
        """String representation"""
        return "FastAPI Keycloak Integration"

    def __repr__(self):
        """Debug representation"""
        return f"{self.__str__()} <class {self.__class__} >"

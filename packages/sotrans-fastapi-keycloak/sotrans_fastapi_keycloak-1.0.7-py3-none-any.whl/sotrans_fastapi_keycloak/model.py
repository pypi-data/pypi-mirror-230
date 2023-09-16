import json
from enum import Enum
from typing import Any, get_args, Union, get_origin
from uuid import UUID

from pydantic import BaseModel, SecretStr, Field
from pydantic.fields import FieldInfo

from sotrans_fastapi_keycloak._uuid import PydanticUUID
from sotrans_fastapi_keycloak.exceptions import KeycloakError


class HTTPMethod(Enum):
    """Represents the basic HTTP verbs

    Values:
        - GET: get
        - POST: post
        - DELETE: delete
        - PUT: put
    """

    GET = "get"
    POST = "post"
    DELETE = "delete"
    PUT = "put"

class UserIdModel(BaseModel):
    id: PydanticUUID


class KeycloakUserBaseModel(UserIdModel):
    """Represents a common set of fields in all keycloak configurations"""

    createdTimestamp: int
    enabled: bool
    totp: bool
    emailVerified: bool
    disableableCredentialTypes: list[str]
    requiredActions: list[str]
    realmRoles: list[str] | None = None
    notBefore: int
    access: dict
    attributes: dict | None = None


class KeycloakUserInfoModel(BaseModel):
    """Represents an update Keycloak user object in default configuration"""

    username: str | None = None
    email: str | None = None
    firstName: str | None = None
    lastName: str | None = None


class KeycloakUserCreateModel(BaseModel):
    """Represents a creation Keycloak user object in default configuration"""

    username: str
    email: str
    password: str
    firstName: str
    lastName: str


class KeycloakUserModel(KeycloakUserBaseModel, KeycloakUserInfoModel):
    """Represents a full Keycloak user object in default configuration"""

    pass

class OIDCUserBaseModel(BaseModel):
    """Represents a user object of Keycloak, parsed from access token

    Notes: Check the Keycloak documentation at https://www.keycloak.org/docs-api/15.0/rest-api/index.html for
    details. This is a mere proxy object.
    """

    azp: str | None = None
    iat: int
    sub: PydanticUUID
    exp: int
    scope: str | None = None
    email_verified: bool
    preferred_username: str | None = None
    realm_access: dict | None = None
    resource_access: dict | None = None
    extra_fields: dict = Field(default_factory=dict)

    @property
    def roles(self) -> list[str]:
        """Returns the roles of the user

        Returns:
            list[str]: If the realm access dict contains roles
        """
        if not self.realm_access and not self.resource_access:
            raise KeycloakError(
                status_code=404,
                reason="The 'realm_access' and 'resource_access' sections of the provided access token are missing.",
            )
        roles = []
        if self.realm_access:
            if "roles" in self.realm_access:
                roles += self.realm_access["roles"]
        if self.azp and self.resource_access:
            if self.azp in self.resource_access:
                if "roles" in self.resource_access[self.azp]:
                    roles += self.resource_access[self.azp]["roles"]
        if not roles:
            raise KeycloakError(
                status_code=404,
                reason="The 'realm_access' and 'resource_access' sections of the provided access token did not "
                "contain any 'roles'",
            )
        return roles

    def __str__(self) -> str:
        """String representation of an OIDCUser"""
        return self.preferred_username


class OIDCUserInfoModel(BaseModel):
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    email: str | None = None


class OIDCUserModel(OIDCUserBaseModel, OIDCUserInfoModel):
    pass


class UsernamePasswordModel(BaseModel):
    """Represents a request body that contains username and password

    Attributes:
        username (str): Username
        password (str): Password, masked by swagger
    """

    username: str
    password: SecretStr


class KeycloakIdentityProviderModel(BaseModel):
    """Keycloak representation of an identity provider

    Attributes:
        alias (str):
        internalId (str):
        providerId (str):
        enabled (bool):
        updateProfileFirstLoginMode (str):
        trustEmail (bool):
        storeToken (bool):
        addReadTokenRoleOnCreate (bool):
        authenticateByDefault (bool):
        linkOnly (bool):
        firstBrokerLoginFlowAlias (str):
        config (dict):

    Notes: Check the Keycloak documentation at https://www.keycloak.org/docs-api/15.0/rest-api/index.html for
    details. This is a mere proxy object.
    """

    alias: str
    internalId: str
    providerId: str
    enabled: bool
    updateProfileFirstLoginMode: str
    trustEmail: bool
    storeToken: bool
    addReadTokenRoleOnCreate: bool
    authenticateByDefault: bool
    linkOnly: bool
    firstBrokerLoginFlowAlias: str
    config: dict


class KeycloakTokenModel(BaseModel):
    """Keycloak representation of a token object

    Attributes:
        access_token (str): An access token
        refresh_token (str): A refresh token, default None
    """

    access_token: str
    refresh_token: str | None = None

    def __str__(self):
        """String representation of KeycloakToken"""
        return f"Bearer {self.access_token}"


class KeycloakRoleModel(BaseModel):
    """Keycloak representation of a role

    Attributes:
        id (str):
        name (str):
        composite (bool):
        clientRole (bool):
        containerId (str):

    Notes: Check the Keycloak documentation at https://www.keycloak.org/docs-api/15.0/rest-api/index.html for
    details. This is a mere proxy object.
    """

    id: str
    name: str
    composite: bool
    clientRole: bool
    containerId: str


class KeycloakGroupModel(BaseModel):
    """Keycloak representation of a group

    Attributes:
        id (str):
        name (str):
        path (str | None = None):
        realmRoles (str | None = None):
    """

    id: str
    name: str
    path: str | None = None
    realmRoles: list[str] | None = None
    subGroups: list["KeycloakGroupModel"] | None = None


KeycloakGroupModel.model_rebuild()


def _annotation_is_type(annotation, type_to_check, check_if_in_union=True) -> bool:
    """Check if annotation is specified type or typing.Union, which contains this type function.

    Notes: this function don't compare generic arguments, but only origin types.

    Args:
        annotation: annotation to check if it matches to type
        type_to_check: type
        check_if_in_union: flag, that specifies whether to check if annotation
                is typing.Union, that contains type_to_check

    Returns: whether annotation matches type to check
    """

    def check_without_union(_annotation):
        if _annotation == type_to_check or get_origin(_annotation) == type_to_check:
            return True

    if check_without_union(annotation):
        return True

    if check_if_in_union and get_origin(annotation) == Union:
        for arg in get_args(annotation):
            if check_without_union(arg):
                return True

    return False


def user_model_attributes_validator(cls: type[BaseModel], data: Any) -> Any:
    """Validator for custom KeycloakUserModel, which have fields, that are stored in attributes
    and managed by User Profile. Simply moves fields (that specified in model) in data dict from attributes
    to main body.

    Args:
        cls: custom user model type
        data: data to validate

    Returns: data with proper fields
    """
    if (
        not isinstance(data, dict)
        or "attributes" not in data
        or not isinstance(data["attributes"], dict)
    ):
        return data

    attributes = data["attributes"]
    for attribute, value in attributes.copy().items():
        if attribute in cls.model_fields:
            attributes.pop(attribute)

            # keycloak always return attributes as array, even if it is not multivalued,
            # so just take first element
            if (
                not _annotation_is_type(attribute, list)
                and isinstance(value, list)
                and len(value) <= 1
            ):
                data[attribute] = value[0] if len(value) > 0 else None
            else:
                data[attribute] = value
    return data


class KeycloakUserAttribute:
    """Metaclass for marking model field as keycloak attribute"""

    pass


def user_model_attributes_serializer(model: BaseModel) -> dict[str, Any]:
    """Serializer for KeycloakUserModel.

    Args:
        model: model to serialize

    Returns: serialized model
    """

    def is_attribute(_field_name):
        return any(
            [
                isinstance(meta, KeycloakUserAttribute)
                for meta in model.model_fields[_field_name].metadata
            ]
        )

    result = {}
    for field_name, field in model:

        if field_name not in model.__pydantic_fields_set__:
            if model.model_fields[field_name].default:
                field = model.model_fields[field_name].default
            else:
                continue
        if is_attribute(field_name):
            if "attributes" not in result:
                result["attributes"] = {}
            result["attributes"][field_name] = [field]
        else:
            if isinstance(field, UUID):
                result[field_name] = str(field)
            else:
                result[field_name] = field
    return result
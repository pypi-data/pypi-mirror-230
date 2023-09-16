"""Keycloak API Client for integrating authentication and authorization with FastAPI"""

__version__ = "1.0.6"

from sotrans_fastapi_keycloak.api import FastAPIKeycloak
from sotrans_fastapi_keycloak.model import (
    HTTPMethod,
    KeycloakError,
    KeycloakGroupModel,
    KeycloakIdentityProviderModel,
    KeycloakRoleModel,
    KeycloakTokenModel,
    KeycloakUserModel,
    KeycloakUserCreateModel,
    KeycloakUserInfoModel,
    KeycloakUserBaseModel,
    OIDCUserModel,
    UsernamePasswordModel,
)

__all__ = [
    FastAPIKeycloak.__name__,
    OIDCUserModel.__name__,
    UsernamePasswordModel.__name__,
    HTTPMethod.__name__,
    KeycloakError.__name__,
    KeycloakUserModel.__name__,
    KeycloakTokenModel.__name__,
    KeycloakRoleModel.__name__,
    KeycloakIdentityProviderModel.__name__,
    KeycloakGroupModel.__name__,
]

from typing import Any, Annotated

from pydantic import BaseModel, model_validator, model_serializer
from sotrans_fastapi_keycloak.model import (
    KeycloakUserBaseModel,
    OIDCUserBaseModel,
    user_model_attributes_validator,
    user_model_attributes_serializer,
    KeycloakUserAttribute,
)

KeycloakUserOptionalStrAttribute = Annotated[str | None, KeycloakUserAttribute()]
KeycloakUserStrAttribute = Annotated[str, KeycloakUserAttribute()]


class SotransKeycloakUserBaseModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def validate(cls: type[BaseModel], value: Any) -> Any:
        return user_model_attributes_validator(cls, value)

    def model_dump_keycloak(self):
        return user_model_attributes_serializer(self)


class SotransKeycloakUserInfoModel(SotransKeycloakUserBaseModel):
    """Represents a Keycloak user info object in SOTRANS configuration"""

    email: str | None = None
    name: KeycloakUserOptionalStrAttribute = None
    surname: KeycloakUserOptionalStrAttribute = None
    patronymic: KeycloakUserOptionalStrAttribute = None
    phone: KeycloakUserOptionalStrAttribute = None
    job_title: KeycloakUserOptionalStrAttribute = None
    status: KeycloakUserOptionalStrAttribute = None
    photo: KeycloakUserOptionalStrAttribute = None
    subsidiary_id: KeycloakUserOptionalStrAttribute = None
    organization_id: KeycloakUserOptionalStrAttribute = None
    note: KeycloakUserOptionalStrAttribute = None


class SotransKeycloakUserUpdateModel(SotransKeycloakUserBaseModel):
    """Represents a Keycloak user info object in SOTRANS configuration"""

    email: str | None = None
    name: KeycloakUserOptionalStrAttribute = None
    surname: KeycloakUserOptionalStrAttribute = None
    patronymic: KeycloakUserOptionalStrAttribute = None
    phone: KeycloakUserOptionalStrAttribute = None
    job_title: KeycloakUserOptionalStrAttribute = None
    status: KeycloakUserOptionalStrAttribute = None
    photo: KeycloakUserOptionalStrAttribute = None
    subsidiary_id: KeycloakUserOptionalStrAttribute = None
    note: KeycloakUserOptionalStrAttribute = None


class SotransKeycloakUserPublicUpdateModel(SotransKeycloakUserBaseModel):
    """Represents an update Keycloak user object in SOTRANS configuration"""

    email: str | None = None
    name: KeycloakUserOptionalStrAttribute = None
    surname: KeycloakUserOptionalStrAttribute = None
    patronymic: KeycloakUserOptionalStrAttribute = None
    phone: KeycloakUserOptionalStrAttribute = None
    photo: KeycloakUserOptionalStrAttribute = None


class SotransKeycloakUserCreateModel(SotransKeycloakUserBaseModel):
    """Represents a creation Keycloak user object in SOTRANS configuration"""

    name: KeycloakUserStrAttribute
    surname: KeycloakUserStrAttribute
    patronymic: KeycloakUserStrAttribute
    phone: KeycloakUserStrAttribute
    organisation_id: KeycloakUserStrAttribute | None = None
    email: str
    password: str


class SotransKeycloakUserModel(KeycloakUserBaseModel, SotransKeycloakUserInfoModel):
    """Represents a full Keycloak user object in SOTRANS configuration"""

    pass


class SotransOIDCUserModel(OIDCUserBaseModel, SotransKeycloakUserInfoModel):
    pass

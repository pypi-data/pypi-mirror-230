from sotrans_fastapi_keycloak.role import Role


class Roles:
    carrier_logistician: str = "carrier_logistician"
    carrier_director: str = "carrier_director"
    company_logistician: str = "company_logistician"
    company_manager: str = "company_manager"
    company_director: str = "company_director"
    admin: str = "admin"


sotrans_roles: dict[str, Role] = {}
sotrans_roles[Roles.carrier_logistician] = Role()
sotrans_roles[Roles.carrier_director] = Role(
    ancestors=[sotrans_roles[Roles.carrier_logistician]]
)

sotrans_roles[Roles.company_logistician] = Role()
sotrans_roles[Roles.company_manager] = Role(
    ancestors=[sotrans_roles[Roles.company_logistician]]
)
sotrans_roles[Roles.company_director] = Role(
    ancestors=[
        sotrans_roles[Roles.company_manager],
        sotrans_roles[Roles.carrier_director],
    ]
)

sotrans_roles[Roles.admin] = Role(ancestors=[sotrans_roles[Roles.company_director]])

class Role:
    def __init__(
        self,
        ancestors: list["Role"] | None = None,
        allowed_sections: list[str] | None = None,
    ):
        """Role class constructor

        Args:
            ancestors: ancestor roles with lower access level
            allowed_sections: list of allowed web app sections distinctive for this role
        """
        if ancestors is None:
            ancestors = []
        if allowed_sections is None:
            allowed_sections = []

        self.ancestors = ancestors
        self._allowed_sections = allowed_sections
        self._combined_allowed_sections = self._combine_allowed_resources()

    @property
    def allowed_sections(self):
        return self._combined_allowed_sections

    def _combine_allowed_resources(self) -> list[str]:
        """
        Combine all allowed resources from all ancestors and allowed resources of current Role.

        :return: list of all unique allowed resources
        """
        combined_allowed_resources = [*self._allowed_sections]
        for ancestor in self.ancestors:
            combined_allowed_resources.extend(ancestor._allowed_sections)
        return list(set(combined_allowed_resources))

    def check_access(self, required_role: "Role") -> bool:
        """Check if current role satisfies access level of required role

        Args:
            required_role: role, to check if access level of current role is equal or better in hierarchy tree

        Returns: result of checking access level
        """
        return Role._check_access(required_role, self)

    @staticmethod
    def _check_access(required_role: "Role", current_role: "Role") -> bool:
        if current_role is required_role:
            return True
        for current_role_ancestor in current_role.ancestors:
            if Role._check_access(required_role, current_role_ancestor):
                return True
        return False

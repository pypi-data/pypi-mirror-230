#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for a RegScale SystemRoles """
from typing import List, Optional, Any
from urllib.parse import urljoin

from pydantic import BaseModel, validator

from regscale.core.app.api import Api
from regscale.core.app.application import Application


class SystemRoles(BaseModel):
    """Class for a RegScale SystemRoles"""

    id: Optional[int]
    uuid: Optional[str]
    roleName: str
    fedrampRoleId: Optional[str]
    assignedUser: Optional[str] = ""
    assignedUserId: Optional[str] = None
    externalUserId: Optional[str] = ""
    roleType: str
    accessLevel: str
    sensitivityLevel: str
    privilegeDescription: str
    functions: str = ""
    securityPlanId: int
    isPublic: str = "true"

    @validator("functions", pre=True, always=True)
    def validate_functions(cls, value):
        if isinstance(value, list):
            if len(value) > 1:
                value = ",".join(value)
            else:
                value = value[0]
            return value
        if isinstance(value, str):
            return value

    @staticmethod
    def from_dict(obj: Any) -> "SystemRoles":
        """Create a SystemRoles object from a dictionary
        :param dict obj: The dictionary to convert to a SystemRoles object
        :return: A SystemRoles object
        :rtype: SystemRoles
        """
        if "id" in obj:
            del obj["id"]
        return SystemRoles(**obj)

    def __eq__(self, other: "SystemRoles") -> bool:
        """
        Compare two SystemRoles objects
        :param SystemRoles other: The SystemRoles object to compare to
        :return: True if the SystemRoles objects are equal
        :rtype: bool
        """
        return self.dict() == other.dict() if isinstance(other, SystemRoles) else False

    def __hash__(self):
        """Hash a SystemRoles object.
        :return: The hash of the SystemRoles object.
        """
        return hash(
            (
                self.roleName,
                self.roleType,
                self.accessLevel,
                self.sensitivityLevel,
                self.privilegeDescription,
                tuple(self.functions),
                self.securityPlanId,
                self.isPublic,
                self.assignedUserId,
                self.fedrampRoleId,
            )
        )

    def insert_systemrole(self, app: Application) -> Optional[dict]:
        """Insert a SystemRoles object into the database.
        :param Application app: The application object.
        :return: The dict of the SystemRoles object.
        :rtype: dict
        """
        # Convert the object to a dictionary
        api = Api(app)
        url = urljoin(app.config.get("domain"), "/api/systemRoles/")
        data = self.dict()
        if isinstance(self.functions, list):
            data["functions"] = ",".join(self.functions)
        data["createdById"] = api.config.get("userId")
        # Make the API call
        response = api.post(url, json=data)
        return response.json() if response.ok else None

    @classmethod
    def get_or_create(
        cls, app: Application, role_name: str, ssp_id: int, **kwargs
    ) -> dict:
        """Get or create a SystemRoles object for a given SSP ID.
        :param Application app: The application object.
        :param str role_name: The name of the role.
        :param int ssp_id: The SSP ID.
        :param dict kwargs: Additional keyword arguments.
        :return: The SystemRoles dict object.
        :rtype: dict
        """
        # Check if a role with the same name already exists
        all_roles = cls.get_all_by_ssp_id(app, ssp_id)

        if existing_role := next(
            (
                role
                for role in all_roles
                if role.get("roleName").lower() == role_name.lower()
            ),
            None,
        ):
            return existing_role

        # If it doesn't exist, create a new one
        new_role = cls(roleName=role_name, **kwargs)
        return new_role.insert_systemrole(app=app)

    @staticmethod
    def get_all_by_ssp_id(app: Application, ssp_id: int):
        """Get a list of SystemRoles objects for a given SSP ID.
        :param Application app: The application object.
        :param int ssp_id: The SSP ID.
        :return: A list of SystemRoles objects.
        :rtype: List[SystemRoles]
        """
        api = Api(app)
        url = urljoin(
            app.config.get("domain"), f"/api/systemRoles/getAllByParent/{ssp_id}"
        )
        response = api.get(url)
        # TODO don't raise
        if response.ok:
            # Parse the response to a list of SystemRoles objects
            return [SystemRoles(**_) for _ in response.json()]
        else:
            response.raise_for_status()

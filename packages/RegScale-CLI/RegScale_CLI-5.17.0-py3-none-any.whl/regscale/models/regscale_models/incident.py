#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" standard python imports """
from typing import Optional

from pydantic import validator
from pydantic import BaseModel

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import camel_case, snake_case


class Incident(BaseModel):
    """RegScale Incident

    :param BaseModel: Pydantic BaseModel
    :raises ValueError: Validation Error
    :return: RegScale Incident
    """

    id: Optional[int]
    attack_vector: Optional[str]
    category: str  # Required
    compromise_date: Optional[str]
    cost: Optional[float]
    date_detected: str
    date_resolved: Optional[str]
    description: Optional[str]
    detection_method: Optional[str]
    ioc: Optional[str]
    impact: Optional[str]
    parent_id: Optional[int]
    phase: str  # Required
    response_actions: Optional[str]
    source_cause: Optional[str]
    title: str  # Required
    incident_poc_id: str  # Required
    created_by_id: Optional[str]
    date_created: Optional[str]
    date_last_updated: Optional[str]
    last_updated_by_id: Optional[str]
    parent_module: Optional[str]
    tenants_id: Optional[int]
    facility_id: Optional[int]
    post_incident: Optional[str]
    uuid: Optional[str]
    is_public: bool = True
    org_id: Optional[int]
    containment_steps: Optional[str]
    eradication_steps: Optional[str]
    recovery_steps: Optional[str]
    severity: Optional[str]

    @validator("category")
    def check_category(value):
        """Validate Category

        :param value: An incident category
        :raises ValueError: Validation Error for Incident Category
        :return: An incident category
        """
        categories = [
            "CAT 0 - Exercise/Network Defense Testing",
            "CAT 1 - Unauthorized Access",
            "CAT 2 - Denial of Service (DoS)",
            "CAT 3 - Malicious Code",
            "CAT 4 - Improper Usage",
            "CAT 5 - Scans/Probes/Attempted Access",
            "CAT 6 - Investigation",
        ]
        if value not in categories:
            cats = "\n".join(categories)
            raise ValueError(f"Category must be one of the following:\n{cats}")
        return value

    @validator("phase")
    def check_phases(value):
        """Validate Phases

        :param value: An incident phase
        :raises ValueError: Validation Error for Incident Phase
        :return: An incident phase
        """
        phases = [
            "Analysis",
            "Closed",
            "Containment",
            "Detection",
            "Eradication",
            "Recovery",
        ]
        if value not in phases:
            phas = "\n".join(phases)
            raise ValueError(f"Phase must be one of the following:\n{phas}")
        return value

    @staticmethod
    def post_incident(incident: "Incident"):
        """Post Incident

        :param incident: An instance of Incident
        :return: RegScale incident
        """
        app = Application()
        config = app.config
        api = Api(app)
        url = config["domain"] + "/api/incidents"
        incident.id = 0  # ID must be 0 for POST
        incident_d = incident.to_dict()
        del incident_d["dateCreated"]
        response = api.post(url=url, json=incident_d)
        return response

    @staticmethod
    def get_incident(incident_id: int):
        """Get Incident

        :param incident_id: A Incident ID
        :return: RegScale incident
        """
        app = Application()
        config = app.config
        api = Api(app)
        url = config["domain"] + "/api/incidents/" + str(incident_id)
        response = api.get(url=url)
        dat = response.json()
        convert = {
            snake_case(camel_case(key)).lower().replace("pocid", "poc_id"): value
            for (key, value) in dat.items()
        }
        return Incident(**convert)

    def to_dict(self):
        """RegScale friendly dict

        :return: RegScale friendly dict for posting to API
        """
        dat = self.dict()
        return {camel_case(key): value for (key, value) in dat.items()}

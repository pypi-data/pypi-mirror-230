#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclasses for a Tenable integration """
from enum import Enum

# standard python imports
from pydantic import BaseModel, Field
from typing import Any, Optional, List


class Family(BaseModel):
    id: str
    name: str
    type: str

    @classmethod
    def from_dict(cls, obj: Any) -> "Family":
        return cls(**obj)


class Repository(BaseModel):
    id: str
    name: str
    description: str
    dataFormat: str

    @classmethod
    def from_dict(cls, obj: Any) -> "Repository":
        return cls(**obj)


class Severity(BaseModel):
    id: str
    name: str
    description: str

    @classmethod
    def from_dict(cls, obj: Any) -> "Severity":
        return cls(**obj)


class TenableAsset(BaseModel):
    pluginID: str
    severity: Severity
    hasBeenMitigated: str
    acceptRisk: str
    recastRisk: str
    ip: str
    uuid: str
    port: str
    protocol: str
    pluginName: str
    firstSeen: str
    lastSeen: str
    exploitAvailable: str
    exploitEase: str
    exploitFrameworks: str
    synopsis: str
    description: str
    solution: str
    seeAlso: str
    riskFactor: str
    stigSeverity: str
    vprScore: str
    vprContext: str
    baseScore: str
    temporalScore: str
    cvssVector: str
    cvssV3BaseScore: str
    cvssV3TemporalScore: str
    cvssV3Vector: str
    cpe: str
    vulnPubDate: str
    patchPubDate: str
    pluginPubDate: str
    pluginModDate: str
    checkType: str
    version: str
    cve: str
    bid: str
    xref: str
    pluginText: str
    dnsName: str
    macAddress: str
    netbiosName: str
    operatingSystem: str
    ips: str
    recastRiskRuleComment: str
    acceptRiskRuleComment: str
    hostUniqueness: str
    acrScore: str
    keyDrivers: str
    uniqueness: str
    family: Family
    repository: Repository
    pluginInfo: str
    count: int = 0

    @classmethod
    def from_dict(cls, obj: Any) -> "TenableAsset":
        obj["severity"] = Severity.from_dict(obj.get("severity"))
        obj["family"] = Family.from_dict(obj.get("family"))
        obj["repository"] = Repository.from_dict(obj.get("repository"))
        return cls(**obj)

    # 'uniqueness': 'repositoryID,ip,dnsName'
    def __hash__(self):
        """
        Enable object to be hashable
        :return: Hashed TenableAsset
        """
        return hash(str(self))

    def __eq__(self, other):
        """
        Update items in TenableAsset class
        :param other:
        :return: Updated TenableAsset
        """
        return (
            self.dnsName == other.dnsName
            and self.macAddress == other.macAddress
            and self.ip == other.ip
            and self.repository.name == other.respository.name
        )


class Reference(BaseModel):
    framework: str
    control: str


class AssetCheck(BaseModel):
    asset_uuid: str
    first_seen: str
    last_seen: str
    audit_file: str
    check_id: str
    check_name: str
    check_info: Optional[str]
    expected_value: Optional[str]
    actual_value: Optional[str]
    status: str
    reference: Optional[List[Reference]] = []
    see_also: str
    solution: Optional[str]
    plugin_id: int
    state: str
    description: str


class ExportStatus(Enum):
    PROCESSING = "PROCESSING"
    FINISHED = "FINISHED"
    READY = "READY"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"

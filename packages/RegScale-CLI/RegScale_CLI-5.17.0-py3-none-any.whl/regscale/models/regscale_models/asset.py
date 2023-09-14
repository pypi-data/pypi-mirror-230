#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclass for a RegScale Asset """

# standard python imports
from typing import Any, List, Optional
from urllib.parse import urljoin
from pydantic import BaseModel
from requests import JSONDecodeError, Response

from regscale.core.app.api import Api
from regscale.core.app.application import Application


class Asset(BaseModel):
    """Asset Model"""

    name: str  # Required
    parentId: int  # Required
    parentModule: str  # Required
    isPublic: bool = True
    ram: int = None
    diskStorage: int = None
    cpu: int = None
    assetCategory: str = None
    osVersion: Optional[str] = None
    otherTrackingNumber: Optional[str] = None
    serialNumber: Optional[str] = None
    ipAddress: Optional[str] = None
    macAddress: Optional[str] = None
    manufacturer: Optional[str] = None
    managementType: Optional[str] = None
    model: Optional[str] = None
    assetOwnerId: Optional[str] = None
    operatingSystem: Optional[str] = None
    assetType: Optional[str] = None
    cmmcAssetType: Optional[str] = None
    description: Optional[str] = None
    endOfLifeDate: Optional[str] = None
    purchaseDate: Optional[str] = None
    status: Optional[str] = None
    tenableId: Optional[str] = None
    netBIOS: Optional[str] = None
    qualysId: Optional[str] = None
    wizId: Optional[str] = None
    wizInfo: Optional[str] = None
    facilityId: Optional[int] = None
    orgId: Optional[int] = None
    id: Optional[int] = None
    createdById: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    fqdn: Optional[str] = None
    notes: Optional[str] = None
    securityPlanId: Optional[int] = 0
    iPv6Address: Optional[str] = None
    oSVersion: Optional[str] = None
    softwareName: Optional[str] = None

    @staticmethod
    def from_dict(obj: dict) -> "Asset":
        """
        Create Asset object from dict
        :param obj: dictionary
        :return: Asset class
        :rtype: Asset
        """
        return Asset(**obj)

    # 'uniqueness': 'ip, macaddress'
    # Enable object to be hashable
    def __hash__(self):
        """
        Enable object to be hashable
        :return: Hashed TenableAsset
        """
        return hash(
            (
                self.name,
                self.ipAddress,
                self.macAddress.lower() if self.macAddress else None,
                self.assetCategory,
                self.assetType,
                self.fqdn,
                self.parentId,
                self.parentModule,
                self.description,
                self.notes,
            )
        )

    def __getitem__(self, key: any) -> any:
        """
        Get attribute from Pipeline
        :param any key:
        :return: value of provided key
        :rtype: any
        """
        return getattr(self, key)

    def __setitem__(self, key: any, value: any) -> None:
        """
        Set attribute in Pipeline with provided key
        :param any key: Key to change to provided value
        :param any value: New value for provided Key
        :return: None
        """
        return setattr(self, key, value)

    def __eq__(self, other) -> "Asset":
        """
        Update items in TenableAsset class
        :param other:
        :return: Updated Asset
        :rtype: Asset
        """
        return (
            self.name == other.name
            and self.ipAddress == other.ipAddress
            and self.macAddress == other.macAddress
            and self.wizId == other.wizId
            and self.description == other.description
            and self.notes == other.notes
        )

    @staticmethod
    def insert_asset(
        app: Application,
        obj: Any,
    ) -> Response:
        """
        Create an asset in RegScale via API
        :param app: Application Instance
        :param obj: Asset Object
        :return: Response from RegScale after inserting the provided asset object
        :rtype: Response
        """
        url = urljoin(app.config["domain"], "/api/assets")
        if isinstance(obj, Asset):
            obj = obj.dict()
        api = Api(app)
        res = api.post(url=url, json=obj)
        return res

    @staticmethod
    def update_asset(
        app: Application,
        obj: Any,
    ) -> Response:
        """
        Create an asset in RegScale via API
        :param app: Application Instance
        :param obj: Asset Object
        :return: Response from RegScale after inserting the provided asset object
        :rtype: Response
        """
        url = urljoin(app.config["domain"], f"/api/assets/{obj['id']}")
        if isinstance(obj, Asset):
            obj = obj.dict()
        api = Api(app)
        res = api.put(url=url, json=obj)
        return res

    @staticmethod
    def find_assets_by_parent(
        app: Application,
        parent_id: int,
        parent_module: str,
    ) -> List["Asset"]:
        """
        Find all assets by parent id and parent module
        :param app: Application Instance
        :param parent_id: Parent Id
        :param parent_module: Parent Module
        :return: List of Assets
        :rtype: List[Asset]
        """
        api = Api(app)
        try:
            res = api.get(
                url=app.config["domain"]
                + f"/api/assets/getAllByParent/{parent_id}/{parent_module}"
            )
            existing_assets = res.json()
        except JSONDecodeError:
            existing_assets = []
        existing_assets = [Asset.from_dict(asset) for asset in existing_assets]
        return existing_assets

    @staticmethod
    def fetch_asset_by_id(id: int) -> "Asset" or None:
        """
        Find all assets by parent id and parent module
        :param id: Id of the asset
        :return: Assets
        :rtype: Asset | None
        """
        app = Application()
        api = Api(app)
        url = urljoin(app.config["domain"], f"/api/assets/{id}")
        try:
            res = api.get(url=url)
            if res.ok:
                return res.json()
        except JSONDecodeError:
            return None

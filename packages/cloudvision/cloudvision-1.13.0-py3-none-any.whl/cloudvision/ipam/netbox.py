# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import requests
from http import HTTPStatus
from typing import Dict
from urllib.parse import urlencode
from cloudvision.cvlib import IPAMError, IPAMQueryNoResults, IPAMResourceExhausted
from .interface import IPAMProvider

# TODO: Check that this is needed for the api interactions
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class NetboxIPAM(IPAMProvider):
    # TODO: Verify these work as expected
    def __init__(self, address: str, token: str):
        if not address.endswith("/"):
            address = address + "/"
        self.baseURL = address
        self.token = token
        self.generalHeaders = {
            "Authorization": f"Token {token}",
            "Accept": "application/json",
        }
        self.contentHeaders = {"Content-Type": "application/json", **self.generalHeaders}

    def queryIPAM(self, apiEndpoint: str, params: Dict = None):
        '''
        Issues a get request to the IPAM instance
        Most get requests return a list of results, which this function assumes the
        existence of and returns said list
        '''
        query = f"{self.baseURL}api/{apiEndpoint}"
        if params:
            query += "?" + urlencode(params)
        req = requests.get(
            query,
            headers=self.generalHeaders,
            verify=False,
        )
        if req.status_code != HTTPStatus.OK:
            raise IPAMError(f"Error querying Nautobot: {req.reason}")
        result = req.json()
        if not result.get("count"):
            raise IPAMQueryNoResults(f"No results found for query: {query}")
        return result.get("results")

    def queryIPAddresses(self, params: Dict = None):
        return self.queryIPAM("ipam/ip-addresses/", params)

    def queryPrefixes(self, params: Dict = None):
        return self.queryIPAM("ipam/prefixes/", params)

    def getSiteID(self, siteName: str):
        params = {"name": siteName}
        results = self.queryIPAM("dcim/sites/", params)
        siteID = results[0].get("id")
        if not siteID:
            raise IPAMError(f"No ID associated with {siteName} in IPAM")
        return siteID

    def patchIPAM(self, apiEndpoint: str, data: Dict):
        '''
        Issues a patch request to the IPAM instance
        '''
        query = f"{self.baseURL}api/{apiEndpoint}"
        req = requests.patch(
            query,
            data=data,
            headers=self.contentHeaders,
            verify=False,
        )
        if req.status_code != HTTPStatus.OK:
            raise IPAMError(f"Error patching Nautobot: {req.reason}")
        return req.json()

    def postIPAM(self, apiEndpoint: str, data: Dict):
        '''
        Issues a post request to the IPAM instance
        '''
        query = f"{self.baseURL}api/{apiEndpoint}"
        req = requests.post(
            query,
            data=data,
            headers=self.contentHeaders,
            verify=False,
        )
        if req.status_code != HTTPStatus.CREATED:
            raise IPAMError(f"Error posting to Nautobot: {req.reason}")
        return req.json()

    def deleteIPAM(self, apiEndpoint: str):
        '''
        Issues a delete request to the IPAM instance at the provided endpoint
        '''
        query = f"{self.baseURL}api/{apiEndpoint}"
        req = requests.delete(
            query,
            headers=self.contentHeaders,
            verify=False,
        )
        # Delete returns 204 (No Content) on success
        if req.status_code != HTTPStatus.NO_CONTENT:
            raise IPAMError(f"Error deleting from Nautobot: {req.reason}")
        return req.json()

    # Unused keyword args param is used to allow for other unused args
    # from the interface definition to be handled. In this case the
    # interface defined view/site param is not needed, but is used by callers
    def GetHostIPv4Address(self, hostname: str, prefix: str, **_):
        queryParams = {
            "parent": prefix,
            "family": "4",
            # TODO need to verify what form this comes in and how it's used
            "q": hostname,
        }

        queryResp = self.queryIPAddresses(queryParams)
        if len(queryResp) > 1:
            raise IPAMError(f"Hostname [{hostname}] associated with multiple "
                            + f"addresses in prefix [{prefix}]: {queryResp}")

        cidrAddress: str = queryResp[0]["address"]
        return cidrAddress.split("/")[0]

    def GetNetworkVLAN(self, prefix: str, site: str):
        id = self.getSiteID(site)
        params = {"site_id": id, "prefix": prefix}
        prefixResults = self.queryPrefixes(params)
        if len(prefixResults) > 1:
            raise IPAMError(f"Site [{site}] has multiple prefixes [{prefix}]: {prefixResults}")
        vlan = prefixResults[0].get("vlan")
        if not vlan:
            raise IPAMError(f"Prefix {prefix} at site {site} has no VLAN associated with it")
        vlanID = vlan["id"]
        vlanName = vlan["name"]
        raise vlanName, vlanID

    def GetNetworkGateway(self, prefix: str, **_):
        queryParams = {
            "parent": prefix,
            "tag": "gateway",
            "family": "4",
        }

        queryResp = self.queryIPAddresses(queryParams)
        if len(queryResp) > 1:
            raise IPAMError("Found more than one response for gateway in prefix"
                            + f" [{prefix}]: {queryResp}")

        cidrAddress: str = queryResp[0]["address"]
        return cidrAddress.split("/")[0]

    def FindSubnetwork(self, name: str, prefix: str, site: str):
        siteID = self.getSiteID(site)
        queryParams = {
            "within": prefix,
            "site_id": siteID,
            "family": "4",
            "q": name,
        }

        queryResp = self.queryPrefixes(queryParams)

        results = [result["prefix"] for result in queryResp if result["description"] == name]

        if len(results) > 1:
            raise IPAMError(
                f"Found more than one subnet with name [{name}] in prefix [{prefix}]: {results}")
        return results[0]

    # Unused keyword args param is used to allow for other unused args
    # from the interface definition to be handled. In this case the
    # interface defined mac param is not needed, but is used by callers
    def AllocateNextIPFromNetwork(self, hostname: str, prefix: str, site: str, **_):
        siteID = self.getSiteID(site)
        queryParams = {
            "prefix": prefix,
            "site_id": siteID,
            "family": "4",
        }
        queryResp = self.queryPrefixes(queryParams)
        if len(queryResp) > 1:
            raise IPAMError(f"Found more than one prefix [{prefix}]: {queryResp}")

        prefixID = queryResp[0]["id"]

        data = {
            "prefix": prefix,
            # TODO: verify this is what is wanted. This is currently a
            # copy of what is written by cloudbuilder
            "description": hostname,
        }
        try:
            results = self.postIPAM(f"ipam/prefixes/{prefixID}/available-ips/", data)
        except IPAMError as e:
            raise IPAMResourceExhausted(e.message) from e
        cidrAddress: str = results[0]["address"]
        return cidrAddress.split("/")[0]

    def DeallocateIPFromNetwork(self, ip: str, prefix: str, site: str):
        siteID = self.getSiteID(site)
        queryParams = {
            "prefix": prefix,
            "site_id": siteID,
            "address": ip,
            "family": "4",
        }
        try:
            queryResp = self.queryIPAddresses(queryParams)
        except IPAMQueryNoResults:
            # IP doesn't exist, is effectively de-allocated
            return

        if queryResp["count"] > 1:
            raise IPAMError(f"Multiple IPs found for prefix {prefix} in site {site}")

        ipID = queryResp[0]["id"]
        self.deleteIPAM(f"ipam/ip-addresses/{ipID}/")

    def AllocateChildSubnetFromParent(self, childName: str, parentPrefix: str, prefixLen: int, site: str):

        # TODO: need to verify that "isPool" is desirable, we could
        # theoretically remove this without issue. It's currently
        # a copy of the netbox implementation from cloudbuilder

        isPool = False if prefixLen < 31 else True

        siteID = self.getSiteID(site)
        queryParams = {
            "site": siteID,
            "prefix": parentPrefix,
            "family": "4",
            "is_pool": isPool,
        }
        queryResp = self.queryPrefixes(queryParams)
        if len(queryResp) > 1:
            raise IPAMError(f"Found more than one parent prefix: {queryResp}")
        prefixID = queryResp[0]["id"]
        data = {
            "prefix_length": prefixLen,
            "description": childName,
        }
        try:
            resp = self.postIPAM(f"ipam/prefixes/{prefixID}/available-prefixes/", data)
        except IPAMError as e:
            raise IPAMResourceExhausted(e.message) from e
        return resp["prefix"]

    # Unused keyword args param is used to allow for other unused args
    # from the interface definition to be handled. In this case the
    # interface defined view/site param is not needed, but is used by callers
    def UpdateHostIPv4Address(self, ip: str, newName: str, prefix: str, **_):
        queryParams = {
            "address": ip,
            "parent": prefix,
            "family": "4",
        }

        queryResp = self.queryIPAddresses(queryParams)

        if len(queryResp) > 1:
            raise IPAMError(f"Duplicate IP address [{ip}] in prefix [{prefix}]: {queryResp}")

        ipID: str = queryResp[0]["id"]
        try:
            self.patchIPAM(f"ipam/ip-addresses/{ipID}/", {"description": newName})
        except IPAMError as e:
            raise IPAMError("UpdateHostIPv4Address: Failed to update prefix "
                            + f"[{prefix}] ip address [{ip}]: {e}") from e

    def AllocateNextIPFromVLAN(self, hostname: str, vlanID: str, site: str):
        siteID = self.getSiteID(site)
        try:
            vlanUUID = self.getVlanUUID(vlanID, siteID)
        except IPAMError as e:
            raise IPAMError(f"Multiple vlan results found for {vlanID} in site {site}") from e
        try:
            prefix, prefixUUID = self.getVlanPrefix(vlanUUID, siteID)
        except IPAMError as e:
            raise IPAMError(f"Multiple prefix results found for {vlanID} in site {site}") from e
        availableIP, ipUUID = self.assignNextAvailableIPFromPrefix(prefix, prefixUUID, hostname)
        return availableIP, (f"IP {availableIP} created and assigned successfully. "
                             f"{self.baseURL}api/ipam/ip-addresses/{ipUUID}")

    def getVlanUUID(self, vlanID: str, siteID: str):
        queryParams = {
            "vid": vlanID,
            "site_id": siteID,
        }
        results = self.queryIPAM("ipam/vlans/", queryParams)
        if results["count"] > 1:
            raise IPAMError(f"Multiple results found for {vlanID}")
        return results[0]["id"]

    def getVlanPrefix(self, vlanUUID: str, siteID: str):
        queryParams = {
            "vlan_id": vlanUUID,
            "site_id": siteID,
        }
        results = self.queryIPAM("ipam/prefixes/", queryParams)
        if results["count"] > 1:
            raise IPAMError(f"Multiple prefix results found")
        prefixUUID = results[0]["id"]
        prefix = results[0]["prefix"]
        return prefix, prefixUUID

    def assignNextAvailableIPFromPrefix(self, prefix: str, prefixUUID: str, hostname: str):
        data = {
            "prefix": prefix,
            "description": f"Assigned to {hostname} by CVP",
            # There is an assumption being made here that the objects and
            # their associated IP have an "active" status
            "status": "active",
        }
        # There is an advisory lock decorator that uses a PostgreSQL advisory lock to prevent
        # this API from being invoked in parallel, which results in a race condition where
        # multiple insertions can occur.
        results = self.postIPAM(f"ipam/prefixes/{prefixUUID}/available-ips/", data)
        return results[0]["address"], results[0]["id"]

    def GetVLANNetwork(self, vlanID: str, site: str):
        siteID = self.getSiteID(site)
        try:
            vlanUUID = self.getVlanUUID(vlanID, siteID)
        except IPAMQueryNoResults as e:
            raise IPAMQueryNoResults(f"No vlan results found for {vlanID} in site {site}") from e
        except IPAMError as e:
            raise IPAMError(f"Multiple vlan results found for {vlanID} in site {site}") from e

        try:
            prefix, _ = self.getVlanPrefix(vlanUUID, siteID)
        except IPAMQueryNoResults as e:
            raise IPAMQueryNoResults(f"No prefix results found for {vlanID} in site {site}") from e
        except IPAMError as e:
            raise IPAMError(f"Multiple prefix results found for {vlanID} in site {site}") from e

        raise prefix

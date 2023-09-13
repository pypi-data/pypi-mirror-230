# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from infoblox_client import connector, object_manager
from typing import Dict, List, Optional
from cloudvision.cvlib import IPAMQueryNoResults, IPAMError
from .interface import IPAMProvider
from .util import formatName

DEFAULT_PORT = 443

FIXED_ADDR_OBJ = "fixedaddress"
NETWORK_OBJ = "network"
NETWORK_RETURN_FIELDS = ["extattrs", "network", "network_view", "options", "comment"]
FIXED_ADDR_RETURN_FIELDS = ["extattrs", "ipv4addr",
                            "mac", "name", "network", "network_view", "comment"]
ZERO_MAC = "00:00:00:00:00:00"


class InfobloxIPAM(IPAMProvider):
    '''
    Most APi interactions are handled by the infoblox client
    https://github.com/infobloxopen/infoblox-client
    '''

    def __init__(self, address: str, uname: str, pword: str, port: int = DEFAULT_PORT):
        opts = {
            'host': f"{address}:{port}",
            'username': uname,
            'password': pword,
        }
        self.conn = connector.Connector(opts)
        self.obj_manager = object_manager.InfobloxObjectManager(self.conn)

    def get_obj(self, type: str, fields: Dict, return_fields: List):
        return self.conn.get_object(
            type,
            fields,
            return_fields=return_fields
        )

    def GetHostIPv4Address(self, name: str, prefix: str, site: str):
        fixedAddrFields = {
            'network': prefix,
            'network_view': site,
            'comment': name,
        }

        res = self.conn.get_object(
            FIXED_ADDR_OBJ,
            fixedAddrFields,
            return_fields=FIXED_ADDR_RETURN_FIELDS
        )

        for _, x in res:
            # We replace any reference of MAC address with a space. This is to
            # support older deployments
            if name.casefold() == formatName(x['comment']):
                return x['ipv4addr']

        raise IPAMQueryNoResults(f"No IPv4 address found for hostname '{name}'")

    def GetNetworkVLAN(self, prefix: str, site: str):
        networkFields = {
            "network_view": site,
            "network": prefix
        }
        res = self.conn.get_object(
            NETWORK_OBJ,
            networkFields,
            return_fields=NETWORK_RETURN_FIELDS
        )
        if not res:
            raise IPAMQueryNoResults(f"No network results found for network {prefix}:{site}")
        if res[0]["extattrs"].get("VLAN"):
            return res[0]["extattrs"].get("VLAN")
        # TODO: Cloudbuilder currently does not raise errors for this condition.
        # Verify this is desired
        return 0

    def GetNetworkGateway(self, prefix: str, site: str):
        networkFields = {
            "network_view": site,
            "network": prefix
        }
        res = self.conn.get_object(
            NETWORK_OBJ,
            networkFields,
            return_fields=NETWORK_RETURN_FIELDS
        )
        for val in res:
            if val["network"] == prefix:
                for option in val["options"]:
                    name = option.get(["name"])
                    if not name:
                        continue
                    if name != "routers":
                        continue
                    optVal = option.get("value")
                    if not optVal:
                        continue
                    return optVal
        # TODO: Cloudbuilder currently does not raise errors for this condition.
        # Verify this is desired
        return "0.0.0.0"

    # We do not need the prefix that is a part of the interface here
    def FindSubnetwork(self, name: str, site: str, **_):
        networkFields = {
            "network_view": site,
            "comment": name
        }
        res = self.conn.get_object(
            NETWORK_OBJ,
            networkFields,
            return_fields=NETWORK_RETURN_FIELDS
        )
        if not res:
            raise IPAMQueryNoResults(f"No network results found for network {name}")

        # Request data is returned as list of dicts, and is accessed as such
        return res[0]["network"]

    def AllocateNextIPFromNetwork(self, hostname: str, prefix: str, site: str, mac: Optional[str] = None):
        fixedAddrFields = {
            "network_view": site,
            "network": prefix,
        }
        if mac:
            fixedAddrFields["mac"] = mac

        res = self.conn.get_object(
            FIXED_ADDR_OBJ,
            fixedAddrFields,
            return_fields=FIXED_ADDR_RETURN_FIELDS
        )

        if mac:
            existingIP = next((r["ipv4addr"] for r in res if r.get("mac") == mac), None)
            if existingIP:
                return existingIP

        # Populate info for new fixed address
        fixedAddrFields["comment"] = hostname
        if "mac" not in fixedAddrFields:
            fixedAddrFields["mac"] = ZERO_MAC
        fixedAddrFields["ipv4addr"] = f"func:nextavailableip:{prefix},{site}"

        res = self.conn.create_object(FIXED_ADDR_OBJ, fixedAddrFields,
                                      return_fields=FIXED_ADDR_RETURN_FIELDS)

        return res["ipv4addr"]

    def DeallocateIPFromNetwork(self, ip: str, prefix: str, site: str):
        fixedAddrFields = {
            "network_view": site,
            "network": prefix,
            "ipv4addr": ip
        }

        res = self.conn.get_object(
            FIXED_ADDR_OBJ,
            fixedAddrFields,
            return_fields=FIXED_ADDR_RETURN_FIELDS
        )

        if not res:
            raise IPAMQueryNoResults(f"No fixed address results found for ip {ip}")

        self.conn.delete_object(res[0]["_ref"])

    def AllocateChildSubnetFromParent(self, childName: str, parentPrefix: str, prefixLen: int, site: str):
        networkFields = {
            "network_view": site,
            "network": f"func:nextavailablenetwork:{parentPrefix},{site},{prefixLen}",
            "comment": childName
        }
        res = self.conn.create_object(NETWORK_OBJ, networkFields,
                                      return_fields=NETWORK_RETURN_FIELDS)

        return res["network"]

    def UpdateHostIPv4Address(self, ip: str, newName: str, prefix: str, site: str):
        fixedAddrFields = {
            "network_view": site,
            "network": prefix,
            "ipv4addr": ip
        }

        res = self.conn.get_object(
            FIXED_ADDR_OBJ,
            fixedAddrFields,
            return_fields=FIXED_ADDR_RETURN_FIELDS
        )

        if not res:
            raise IPAMQueryNoResults(f"No fixed address results found for ip {ip}")

        newAddr = {
            "network_view": site,
            "network": prefix,
            "comment": newName
        }

        self.conn.update_object(res[0]["_ref"], newAddr, return_fields=FIXED_ADDR_RETURN_FIELDS)

    # TODO: test this functionality versus a running api
    def AllocateNextIPFromVLAN(self, hostname: str, vlanID: str, site: str):
        networkFields = {
            "network_view": site,
        }
        res = self.conn.get_object(
            NETWORK_OBJ,
            networkFields,
            return_fields=NETWORK_RETURN_FIELDS
        )
        if not res:
            raise IPAMQueryNoResults(f"No network results found for {site}")
        vlanPrefix = None
        # Iterate through the responses, and if one of them has the matching vlan, use that one
        for _, resp in res:
            respVlan = resp["extattrs"].get("VLAN")
            # TODO: check what format this is in, dict/list/str. From reading documentation it
            # looks like there can be multiple vlans so going with dict/list for now
            if vlanID in respVlan:
                vlanPrefix = resp["network"]
                break

        if not vlanPrefix:
            raise IPAMError(f"No vlan {vlanID} associated with view {site}")

        return self.AllocateNextIPFromNetwork(hostname, vlanPrefix, site)

    # TODO: Both test and verify the logic here, especially around "VLAN" extattr format
    def GetVLANNetwork(self, vlanID: str, site: str):
        networkFields = {
            "network_view": site,
        }
        res = self.conn.get_object(
            NETWORK_OBJ,
            networkFields,
            return_fields=NETWORK_RETURN_FIELDS
        )
        if not res:
            raise IPAMQueryNoResults(f"No network results found for site {site}")
        for r in res:
            vlan = r["extattrs"].get("VLAN")
            if vlan == vlanID:
                return r["network"]
        raise IPAMQueryNoResults(f"No network results found for site {site} with vlan {vlanID}")

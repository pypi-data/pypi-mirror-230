# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from enum import Enum
from typing import Dict

from cloudvision.cvlib import IPAMError

# from .bluecat import BluecatIPAM
# from .cvp import CvpIPAM
from .infoblox import InfobloxIPAM
from .nautobot import NautobotIPAM
from .netbox import NetboxIPAM


# Standardised args for instantiating IPAM when we have a dict of args,
# as is likely when using this in a Script execution context
ARG_IPAM_TYPE = "ipam_type"
ARG_ADDR = "address"
ARG_TOKEN = "token"
ARG_UNAME = "username"
ARG_PW = "password"
ARG_PORT = "port"


class IPAMType(Enum):
    '''
    Enum class used to store the various supported IPAM providers
    '''
    Unknown = 0
    Bluecat = 1
    Cvp = 2
    Infoblox = 3
    Nautobot = 4
    Netbox = 5


IPAM_STRS_TO_TYPE = {
    "Bluecat": IPAMType.Bluecat,
    "Cvp": IPAMType.Cvp,
    "Infoblox": IPAMType.Infoblox,
    "Nautobot": IPAMType.Nautobot,
    "Netbox": IPAMType.Netbox,
}


def stringToIPAMType(type: str):
    provider = IPAM_STRS_TO_TYPE.get(type)
    if not provider:
        return IPAMType.Unknown
    return provider


def instantiateIPAMFromArgs(args: Dict[str, str]):
    '''
    Takes a dict of args and attempts to instantiate an IPAM with the relevant args using the
    list of standardised arguments specified for IPAM instantiation.
    The list of standardised arguments are used as different IPAM providers have
    differing authentication methods for their API interactions

    All calls are expecting an "ipam_type" field defined in the arg dict to determine what IPAM
    provider is needed


    Infoblox require;
    - "address";    the address of the IPAM api
    - "username" & 
    - "password";   authentication information so that connection with the
                    IPAM can be established and api interactions to occur


    Nautobot and Netbox require;
    - "address";    the address of the IPAM api
    - "token";      authentication token for the api

    raises: 
        IPAMError;  If the args required to instantiate the IPAM are missing 
    '''
    ipam_type = args.get(ARG_IPAM_TYPE)
    if not ipam_type:
        supportedTypes = [k for k in IPAM_STRS_TO_TYPE.keys()]
        raise IPAMError((f"'{ARG_IPAM_TYPE}' unspecified in arguments\n"
                         f"'{ARG_IPAM_TYPE}' needs to be one of {supportedTypes}"))

    match stringToIPAMType(ipam_type):
        case IPAMType.Bluecat:
            # return BluecatIPAM()
            raise IPAMError(f"Bluecat IPAM type is not implemented")

        case IPAMType.Cvp:
            # return CvpIPAM()
            raise IPAMError(f"Cvp IPAM type is not implemented")

        case IPAMType.Infoblox:
            # Validate required arguments are present
            addr = args.get(ARG_ADDR)
            uname = args.get(ARG_UNAME)
            pword = args.get(ARG_PW)
            if not (addr and uname and pword):
                raise IPAMError(("Missing required arguments for 'Infoblox' instantiation\n"
                                 f"Arguments {ARG_ADDR}, {ARG_UNAME} and {ARG_PW}"
                                 " are required"))
            # Handle optional args
            port = args.get(ARG_PORT)
            if port:
                port = int(port)
                return InfobloxIPAM(address=addr, uname=uname, pword=pword, port=port)
            return InfobloxIPAM(address=addr, uname=uname, pword=pword)

        case IPAMType.Nautobot:
            # Validate required arguments are present
            addr = args.get(ARG_ADDR)
            tok = args.get(ARG_TOKEN)
            if not (addr and tok):
                raise IPAMError(("Missing required arguments for 'Nautobot' instantiation\n"
                                 f"Arguments {ARG_ADDR} and {ARG_TOKEN} are required"))
            return NautobotIPAM(address=addr, token=tok)

        case IPAMType.Netbox:
            # Validate required arguments are present
            addr = args.get(ARG_ADDR)
            tok = args.get(ARG_TOKEN)
            if not (addr and tok):
                raise IPAMError(("Missing required arguments for 'Netbox' instantiation\n"
                                 f"Arguments {ARG_ADDR} and {ARG_TOKEN} are required"))
            return NetboxIPAM(address=addr, token=tok)

        case IPAMType.Unknown:
            raise IPAMError(f"Unsupported IPAM type {ipam_type}")

# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import abc


class IPAMProvider(metaclass=abc.ABCMeta):
    """
    IPAM provider interface that all implemented IPAM providers must follow.
    Note that only the callable functions need to be matched, not their args.
    However, the params outlined will be passed in name and order as defined below, so
    implementations need to be able to handle them to avoid exceptions occurring


    Raises:
        NotImplementedError: When a subclass does not implement all required 

    """
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, 'GetHostIPv4Address')
            and callable(subclass.GetHostIPv4Address)
            and hasattr(subclass, 'GetNetworkVLAN')
            and callable(subclass.GetNetworkVLAN)
            and hasattr(subclass, 'GetNetworkGateway')
            and callable(subclass.GetNetworkGateway)
            and hasattr(subclass, 'FindSubnetwork')
            and callable(subclass.FindSubnetwork)
            and hasattr(subclass, 'AllocateNextIPFromNetwork')
            and callable(subclass.AllocateNextIPFromNetwork)
            and hasattr(subclass, 'DeallocateIPFromNetwork')
            and callable(subclass.DeallocateIPFromNetwork)
            and hasattr(subclass, 'AllocateChildSubnetFromParent')
            and callable(subclass.AllocateChildSubnetFromParent)
            and hasattr(subclass, 'UpdateHostIPv4Address')
            and callable(subclass.UpdateHostIPv4Address)
            and hasattr(subclass, 'AllocateNextIPFromVLAN')
            and callable(subclass.AllocateNextIPFromVLAN)
            and hasattr(subclass, 'GetVLANNetwork')
            and callable(subclass.GetVLANNetwork)
            or NotImplemented)

    # Connecting to the IPAM should be done in the class initialisation if tokens,
    # connections, etc. need to be instantiated/retrieved

    @abc.abstractmethod
    def GetHostIPv4Address(self, name: str, prefix: str, site: str):
        raise NotImplementedError

    # TODO: As yet unused in any autofills nor any use cases identified, decide if required/desired in interface
    @abc.abstractmethod
    def GetNetworkVLAN(self, prefix: str, site: str):
        raise NotImplementedError

    # TODO: As yet unused in any autofills nor any use cases identified, decide if required/desired in interface
    @abc.abstractmethod
    def GetNetworkGateway(self, prefix: str, site: str):
        raise NotImplementedError

    # TODO: As yet unused in any autofills nor any use cases identified, decide if required/desired in interface
    @abc.abstractmethod
    def FindSubnetwork(self, name: str, prefix: str, site: str):
        raise NotImplementedError

    @abc.abstractmethod
    def AllocateNextIPFromNetwork(self, hostname: str, prefix: str, site: str, mac: str):
        raise NotImplementedError

    @abc.abstractmethod
    def DeallocateIPFromNetwork(self, ip: str, prefix: str, site: str):
        raise NotImplementedError

    # TODO: As yet unused in any autofills nor any use cases identified, decide if required/desired in interface
    @abc.abstractmethod
    def AllocateChildSubnetFromParent(self, childName: str, parentPrefix: str, prefixLen: int, site: str):
        raise NotImplementedError

    # TODO: As yet unused in any autofills nor any use cases identified (that shouldn't be errors),
    # decide if required/desired in interface
    @abc.abstractmethod
    def UpdateHostIPv4Address(self, ip: str, newName: str, prefix: str, site: str):
        raise NotImplementedError

    # New interface
    @abc.abstractmethod
    def AllocateNextIPFromVLAN(self, hostname: str, vlanID: str, site: str):
        raise NotImplementedError

    @abc.abstractmethod
    def GetVLANNetwork(self, vlanID: str, site: str):
        raise NotImplementedError

    # ASN related functions should only be implemented on CVP IPAM as that is the only provider
    # that supports it

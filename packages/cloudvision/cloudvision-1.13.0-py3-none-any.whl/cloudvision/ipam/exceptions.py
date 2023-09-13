# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cloudvision.cvlib import AutofillActionException


class IPAMError(AutofillActionException):
    """
    Exception raised when an issue occurs when interfacing with an IPAM
    """

    def __init__(self, message: str = "cloudvision has encountered an error with an IPAM"):
        super().__init__(message)


class IPAMQueryNoResults(IPAMError):
    """
    Exception raised when an IPAM query returns no results
    """

    def __init__(self, message: str = "cloudvision has found no results in IPAM"):
        super().__init__(message)


class IPAMResourceExhausted(IPAMError):
    """
    Exception raised when an issue occurs when requesting a resource from an IPAM
    """

    def __init__(self, message: str = "IPAM resource exhausted"):
        super().__init__(message)

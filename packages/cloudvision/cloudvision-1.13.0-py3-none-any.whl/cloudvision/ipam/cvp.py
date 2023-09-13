# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from .interface import IPAMProvider


class CvpIPAM(IPAMProvider):
    def AllocateNextIPFromNetwork(self, hostname: str, prefix: str, site: str, mac: str):
        pass

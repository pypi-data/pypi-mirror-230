# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import re
from typing import List, Tuple


# MAC regular expression. Beginning and ending spaces are important.
macRe = "^(\S+)\s+(([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2}))\s*(\S+)?"


def formatName(name: str):
    '''
    formatName modifies the name to what we expect in the compare.
    This should handle cases by removing the MAC address from the following formatted strings:
    o hostname <MAC> Ethernet1
    o hostname <MAC>
    '''
    match = re.search(macRe, name)
    # If no match, then return the name as is
    if not match:
        return name

    # If the ending match element is not empty, then lets use that.
    if len(match.groups()) >= 6 and match.groups()[5] != "":
        return match.groups()[1] + " " + match.groups()[5]
    # ending match element is empty...just return the first
    return match.groups()[1]


def formatCVPSubnetName(name: str):
    '''
    formatCVPSubnetName replaces
    '-' -> '_'
    '|' -> ':'
    '/' -> '.'
    '''
    replName = name
    replacements: List[Tuple] = [
        ("-", "_"),
        ("|", ":"),
        ("/", ".")
    ]
    for old, new in replacements:
        replName = replName.replace(old, new)
    return replName

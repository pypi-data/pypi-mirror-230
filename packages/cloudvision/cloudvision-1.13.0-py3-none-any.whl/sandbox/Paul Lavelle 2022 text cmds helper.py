import json
import requests
ACCESS_TOKEN = "access_token"
HEADERS = {"Accept": "application/json"}


def runDeviceCmds(ctx, commandsList, fmt="json"):
    device = ctx.device
    # From the DI service documentation about the HOST field:
    # Host can be either IP address or hostname
    deviceInteractionHost = device.ip if device.ip else device.hostName
    request = {
        "host": deviceInteractionHost,
        "deviceID": device.id,
        "cmds": commandsList,
        "connTimeout": ctx.connections.connectionTimeout,
        "timeout": ctx.connections.cliTimeout,
        "format": fmt,
        "stopOnError": False
    }
    data = json.dumps(request)
    accessToken = ctx.user.token
    cookies = {ACCESS_TOKEN: accessToken}
    try:
        runCmdURL = f"https://{ctx.connections.serviceAddr}/{ctx.connections.commandEndpoint}"
        response = requests.post(runCmdURL, data=data, headers=HEADERS,
                                 cookies=cookies, verify=False)
    except requests.ConnectionError as e:
        raise e
    if response.status_code != 200:
        response.raise_for_status()
    resp = response.json()
    # Check that some other issue did not occur. It has been seen that a statuscode 200 was
    # received for the response, but when the response contents are jsonified and returned,
    # they can be a simple dictionary with two entries, 'errorCode' and 'errorMessage',
    # instead of the usual list of dictionaries for each command response.
    # This is not caused by the commands that the user provided, but is an issue with
    # the request that was sent to the command endpoint
    # If that occurs, raise a DeviceCommandsFailedException
    # An example of this is {'errorCode': '341604', 'errorMessage': 'Invalid request'}
    if all(key in resp for key in ["errorCode", "errorMessage"]):
        errCode = resp["errorCode"]
        errMsg = resp["errorMessage"]
        raise UserWarning((f"Commands failed to run on device \"{device.id}\","
                           f" returned {errCode}:\"{errMsg}\""), errCode, errMsg)
    return resp



#------------------------------------------#
# Called like so
cmds = [
    "enable",
    "show version",
    "show hostname",
]
cmdResponse = runDeviceCmds(ctx, cmds, fmt="text")
resp = cmdResponse[1]["response"]["output"]
ctx.alog(f"{resp}")


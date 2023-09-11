"""Initialize modules."""
from typing import Dict
from uun_iot.UuAppClient import UuAppClient
from .Heartbeat import Heartbeat
from .BaseHealthCheck import BaseHealthCheck

def init(config: Dict, uuclient: UuAppClient):

    def cmd_heartbeat(dto_in):
        uucmd = config["uuApp"]['uuCmdList']['gatewayHeartbeat']
        resp, (ok, err) = uuclient.post(uucmd, dto_in)
        if not ok:
            return False
        return resp

    gateway_config = config["gateway"]

    return [Heartbeat(cmd_heartbeat)]


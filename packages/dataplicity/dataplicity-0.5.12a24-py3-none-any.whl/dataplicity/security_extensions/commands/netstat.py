from sys import stdout
import hashlib
import base64

from .base import CommandBase

USE_SS, USE_NETSTAT = False, False
try:
    from sh import ss
    USE_SS = True
except:
    from sh import netstat
    USE_NETSTAT = True


class Netstat(CommandBase):
    """_summary_
        $ netstat -an 
        Active Internet connections (servers and established)
        Proto Recv-Q Send-Q Local Address           Foreign Address         State      
        tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN     
        tcp        0      0 127.0.0.1:631           0.0.0.0:*               LISTEN     
        tcp        0      0 0.0.0.0:9080            0.0.0.0:*               LISTEN     
        tcp        0      0 127.0.0.1:9050          0.0.0.0:*               LISTEN     
        tcp        0      0 127.0.0.1:41663         0.0.0.0:*               LISTEN     
        tcp        0      0 0.0.0.0:9000            0.0.0.0:*               LISTEN     
        tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN     
        tcp        0      0 0.0.0.0:8080            0.0.0.0:*               LISTEN
        [...]

    Args:
        object (_type_): _description_

    Returns:
        _type_: _description_
    """

    enabled_attrs = [
        "protocol",
        "state",
        "peer_address",
        "peer_port"
    ]
    kind = "netstat"

    @staticmethod
    def _get_cmd():
        if USE_SS:
            return ss("-an", _iter=True)
        elif USE_NETSTAT:
            return netstat("-an", _iter=True)
    def parse_params(self, data):
        data = data.split()
        peer = data[5]
        peer_address = peer if ":" not in peer else peer.split(":")[0]
        peer_port = "*" if ":" not in peer else peer.split(":")[1]
        
        return {
            "protocol": data[0],
            "state": data[1],
            "peer_address": peer_address,
            "peer_port": peer_port,
            }



    def should_skip_first_row(self):
        # 'ss' has an option for headerless -H
        # but 'netstat' doesn't include it.
        return True

    def should_skip_row(self, row):
        return row.protocol == u"nl"


if __name__ == "__main__":
    netstat_list = Netstat().execute()
    stdout.write("Netstat list: \n")
    for row in netstat_list:
        stdout.write("\t" + str(row) + "\n")
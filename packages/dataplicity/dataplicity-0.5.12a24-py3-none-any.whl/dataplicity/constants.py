from __future__ import print_function
from __future__ import unicode_literals

from os import environ


def get_environ_int(name, default):
    """Get an integer from the environment.

    Args:
        name (str): environment variable name
        default (int): Default if env var doesn't exist or not an integer

    Returns:
        int: Integer value of env var.
    """
    try:
        value = int(environ.get(name, default))
    except ValueError:
        return default
    return value


CONF_PATH = "/etc/dataplicity/dataplicity.conf"
SERVER_URL = environ.get("DATAPLICITY_API_URL", "https://api.dataplicity.com")
M2M_URL = environ.get("DATAPLICITY_M2M_URL", "wss://m2m.dataplicity.com/m2m/")
M2M_FEATURES = {"scan", "downloads"}
SERIAL_LOCATION = "/opt/dataplicity/tuxtunnel/serial"
AUTH_LOCATION = "/opt/dataplicity/tuxtunnel/auth"
DEVICE_TOKEN_LOCATION = "/opt/dataplicity/tuxtunnel/device_token"
REMOTE_DIRECTORY_LOCATION = "/home/dataplicity/remote"
DEVICE_CLASS_LOCATION = "/opt/dataplicity/tuxtunnel/device_class"
IDS_EVENTS_PATH = "/tmp/"
IDS_EVENTS_FILENAME = "__dataplicity_ids.events"

# Client will reconnect if the server hasn't responded in this time
MAX_TIME_SINCE_LAST_PACKET = 100.0  # seconds or None

# Number of bytes to read at a time, when copying date over the network
# TODO: Replace this with a sensible chunk size once we identify the
# issue with ssh over Porthole
CHUNK_SIZE = 1024 * 1024

# Maximum number of services (port forward/commands/file etc)
LIMIT_SERVICES = get_environ_int("DATAPLICITY_LIMIT_SERVICES", 500)

# Maximum number of terminals (separate pool from services)
LIMIT_TERMINALS = get_environ_int("DATAPLICITY_LIMIT_TERMINALS", 100)

# Server busy HTTP response
SERVER_BUSY = b"""HTTP/1.1 503 Device Busy\r\n\r\n
<h1>503 - Server busy</h1>

<p>The device is under heavy load and could not return a response.</p>

<p>Try increasing <tt>DATAPLICITY_LIMIT_SERVICES</tt></p>
"""

# how many events before forcing a push
IDS_MAX_EVENTS = 50

# how many seconds before forcing a push
IDS_EVENT_PUSH_TIMEOUT = 300

# in case there's an event seen for the first time
IDS_URGENT_EVENT_PUSH_TIMEOUT = 5

IDS_RETRY_WAIT_SECONDS = 5

IDS_RETRY_MAX_ATTEMPTS = 25

# IDS detects events very 0.1 seconds; but, all events that happened
# in between IDS_MIN_EVENT_INTERVAL would be simplified:
# for example [1, 2, 3, 10, 12, 15, 30, 32, 60]
# would become [1, 30, 60]
IDS_MIN_EVENT_INTERVAL = 60
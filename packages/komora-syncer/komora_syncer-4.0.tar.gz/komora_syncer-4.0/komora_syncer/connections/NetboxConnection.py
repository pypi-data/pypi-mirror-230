import logging
import pynetbox
from komora_syncer.config import get_config

logger = logging.getLogger(__name__)


class NetboxConnection:
    netbox_url = get_config()['netbox']['NETBOX_INSTANCE_URL']
    api_token = get_config()['netbox']['NETBOX_API_TOKEN']
    connection = None

    def __new__(cls):
        raise TypeError("This is a static class")

    @staticmethod
    def open():
        """
        Opens a connection to the NetBox instance using the configured URL and API token.
        """
        try:
            NetboxConnection.connection = pynetbox.api(
                NetboxConnection.netbox_url, token=NetboxConnection.api_token
            )
        except Exception:
            logger.exception("Could not establish connection to NetBox instance")
            raise

    @staticmethod
    def get_connection():
        """
        Returns the connection to the NetBox instance, opening it if necessary.
        """
        if NetboxConnection.connection is None:
            try:
                NetboxConnection.open()
            except Exception:
                logger.exception("Could not open connection to NetBox instance")
                return None

        return NetboxConnection.connection
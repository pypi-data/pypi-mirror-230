import json
import logging
import requests

from komora_syncer.config import get_config
from komora_syncer.connections.NetboxConnection import NetboxConnection
from komora_syncer.models.netbox.NetboxBase import NetboxBase
from komora_syncer.models.netbox.NetboxCache import NetboxCache

logger = logging.getLogger(__name__)


class NbDevice(NetboxBase):
    def __init__(self, komora_obj):
        super().__init__()
        self.name = komora_obj.name
        self.komora_id = komora_obj.id
        self.site_name = komora_obj.siteName
        self.komora_url = f"{get_config()['komora']['KOMORA_URL']}/app/device/{self.komora_id}"
        self.api_object = None

    def find(self):
        # 1. lookup Device by KOMORA_ID
        device_cache = NetboxCache.get_device_cache()

        if not self.komora_id:
            return None

        try:
            if self.komora_id in device_cache:
                netbox_device = device_cache[self.komora_id]
            else:
                netbox_device = self.nb.dcim.devices.get(cf_komora_id=self.komora_id)

            if netbox_device is not None:
                self.api_object = netbox_device
                return self.api_object
        except Exception as e:
            logger.exception(f"Unable to get Device by komora_id: {self.komora_id}. Error: {e}")

        # 2. Lookup device by name, if komora id is not presented
        # - log a problem, when the name exists, but komora_id was not found
        try:
            self.site_name = self.site_name if self.site_name else "SKLAD"

            netbox_site = self.nb.dcim.sites.get(name__ie=self.site_name)
            netbox_device = self.nb.dcim.devices.get(name__ie=self.name, site_id=netbox_site.id)

            if netbox_device is not None:
                logger.warning(f"komora_id: {str(self.komora_id)} was not found, but Device {self.name} at site {self.site_name} already exists")
                self.api_object = netbox_device
                return self.api_object
        except Exception as e:
            logger.exception(f"Unable to get Device by name: {self.name}. Error: {e}")

        return self.api_object

    def update(self, nb_device):
        try:
            if nb_device.update(self.params):
                self.api_object = nb_device
                logger.info(f"Device: {self.name} updated successfully")
        except Exception as e:
            logger.exception(f"Unable to update device {self.name}. Error: {e}")

    def synchronize(self):
        device = self.find()

        if device:
            self.update(device)
        else:
            logger.info(f"Device {self.name} - komora_id: {self.komora_id} not found in netbox")

    @property
    def params(self):
        params = {}

        if self.api_object:
            if isinstance(self.api_object.custom_fields, dict):
                params['custom_fields'] = self.api_object.custom_fields
                params['custom_fields']['komora_id'] = self.komora_id
                params['custom_fields']['komora_url'] = self.komora_url
        else:
            params['custom_fields'] = {"komora_id": self.komora_id, "komora_url": self.komora_url}

        return params

    @staticmethod
    def get_nb_devices_data():
        filter_device_roles = NetboxConnection.get_connection().dcim.device_roles.filter(name=["Passive component", "unknown", "DWDM"])
        filter_device_role_ids = json.dumps([str(role.id) for role in filter_device_roles])
        query = NbDevice.get_query(filter_device_role_ids)

        try:
            url = get_config()['netbox']['NETBOX_GRAPHQL_URL']
            session = requests.Session()
            req = session.post(url, json={'query': query}, headers={'Authorization': f"Token {get_config()['netbox']['NETBOX_API_TOKEN']}"})
            json_data = json.loads(req.text)
            return json_data
        except Exception as e:
            logger.exception("Unable to get Netbox devices data. Error: {e}")
            raise

    @staticmethod
    def get_query(filter_device_role_ids):
        query = f"""
          {{
            device_list(role_id__n: {filter_device_role_ids}, status: "active") {{
              id,
              name,
              primary_ip4 {{
                id,
                address
              }},
              comments,
              serial,
              custom_fields,
              location {{
                id,
                name,
                custom_fields
              }},
              tenant {{
                id,
                name,
                custom_fields
              }}
              site {{
                id,
                name,
                custom_fields,
                tenant{{
                  id,
                  name,
                  custom_fields
                }}
              }},
              interfaces {{
                id,
                name,
                description
              }}
            }}
          }}
        """
        return query
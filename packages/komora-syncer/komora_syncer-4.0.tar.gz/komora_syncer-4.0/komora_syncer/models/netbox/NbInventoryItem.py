import logging

from komora_syncer.config import get_config
from komora_syncer.connections.NetboxConnection import NetboxConnection
from komora_syncer.models.netbox.NetboxBase import NetboxBase

logger = logging.getLogger(__name__)


class NbInventoryItem(NetboxBase):
    def __init__(self, komora_obj):
        NetboxBase.__init__(self)
        self.inventory_number = komora_obj.inventarizationNumber
        self.komora_id = komora_obj.id
        self.komora_site_id = komora_obj.siteId
        self.komora_location_id = komora_obj.locationId
        self.komora_device_id = komora_obj.deviceId
        self.komora_url = f"{get_config()['komora']['KOMORA_URL']}/app/inventarization/{self.inventory_number}/{self.komora_device_id}"
        self.netbox_url = komora_obj.netboxUrl
        self.api_object = None

    def find(self):
        if not self.komora_id:
            return self.api_object

        netbox_inventory_item = self._find_by_komora_id()
        if netbox_inventory_item:
            self.api_object = netbox_inventory_item
            return self.api_object

        netbox_inventory_item = self._find_by_inventory_number()
        if netbox_inventory_item:
            self.api_object = netbox_inventory_item
            return self.api_object

        logger.warning("Unable to find Inventory Item")
        return self.api_object

    def _find_by_komora_id(self):
        return NetboxConnection.get_connection().dcim.inventory_items.get(
            cf_komora_id=self.komora_id)

    def _find_by_inventory_number(self):
        return NetboxConnection.get_connection().dcim.inventory_items.get(
            cf_asset_numbers=self.inventory_number)

    def update(self, nb_inventory_item):
        try:
            if nb_inventory_item.update(self.params):
                self.api_object = nb_inventory_item
                logger.info(
                    f"Inventory: {self.inventory_number} updated successfuly")
        except Exception as e:
            logger.exception(
                f"Unable to update Inventory Item: {self.inventory_number}")

    def synchronize(self):
        inventory_item = self.find()

        if inventory_item:
            self.update(inventory_item)
        else:
            logger.info(
                f"Inventory Item: {self.inventory_number} not found in Netbox.")

    @property
    def params(self):
        params = {}

        if self.api_object:
            if isinstance(self.api_object.custom_fields, dict):
                params['custom_fields'] = self.api_object.custom_fields
                params['custom_fields']['komora_id'] = self.komora_id
                params['custom_fields']['komora_url'] = self.komora_url
        else:
            params['custom_fields'] = {
                "komora_id": self.komora_id, "komora_url": self.komora_url}

        return params

    def get_nb_inventory_items_data():
        # TODO: WORKAROUND
        SITES_CACHE = {
            site.id: site for site in NetboxConnection.get_connection().dcim.sites.all()}
        DEVICES_CACHE = {dev.id: {
            "device": dev, "site": SITES_CACHE[dev.site.id], "location": dev.location} for dev in NetboxConnection.get_connection().dcim.devices.all()}

        def inventory_to_json(inventory):
            device_id = inventory.device.id
            device = DEVICES_CACHE[device_id]['device']
            site = DEVICES_CACHE[device_id]['site']
            location = DEVICES_CACHE[device_id]['location']

            # print(inventory)
            inventory_dict = {}
            inventory_dict['serial'] = inventory.serial
            # inventory_dict['last_probed'] = inventory.custom_fields.get(
            #    'inventory_monitor_probed', False)
            inventory_dict['last_probed'] = inventory.custom_fields.get(
                'inventory_monitor_last_probe', "")
            inventory_dict['asset_numbers'] = inventory.custom_fields.get(
                'asset_numbers', "").split(';')
            inventory_dict['inventarizationNumber'] = inventory_dict['asset_numbers'][0]
            inventory_dict['active'] = inventory.custom_fields.get(
                'inventory_monitor_active', False)
            inventory_dict['device_name'] = device.name
            inventory_dict['name'] = inventory.name
            inventory_dict['site_name'] = site.name if site else ""
            inventory_dict['site_physical_address'] = site.physical_address if site else ""
            inventory_dict['site_longitude'] = site.longitude if site else ""
            inventory_dict['site_latitude'] = site.latitude if site else ""
            inventory_dict['site_location'] = location.name if location else ""
            if site and site['custom_fields'].get('komora_id', ""):
                inventory_dict['site_id'] = site['custom_fields'].get(
                    'komora_id', "")
            if device and device['custom_fields'].get('komora_id', ""):
                inventory_dict['device_id'] = device['custom_fields'].get(
                    'komora_id', "")
            if location and location.custom_fields.get('komora_id', ""):
                inventory_dict['location_id'] = location.custom_fields.get(
                    'komora_id', "")

            inventory_dict['netbox_id'] = inventory.id
            return inventory_dict

        # "asset_number": [items]
        result = {}

        for inv in NetboxConnection.get_connection().dcim.inventory_items.filter(cf_abra_discovered=True):
            inv_dict = inventory_to_json(inv)
            asset_numbers = []

            # if multiple asset_numbers found
            if ';' in inv.custom_fields.get('asset_numbers'):
                for asset_number in inv.custom_fields.get('asset_numbers').split(';'):
                    asset_numbers.append(asset_number)
            elif inv.custom_fields.get('asset_numbers') is not None:
                asset_numbers.append(inv.custom_fields.get('asset_numbers'))
            else:
                print("something went wrong", inv, inv.id)

            for asset_nmr in asset_numbers:
                # add inventory_item or init it
                if result.get(asset_nmr):
                    result[asset_nmr].append(inv_dict)
                else:
                    result[asset_nmr] = [inv_dict]

        return result

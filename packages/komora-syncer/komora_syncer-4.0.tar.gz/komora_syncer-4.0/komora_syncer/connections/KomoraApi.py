import json
import logging
import time

import requests

from komora_syncer.config import get_config
from komora_syncer.connections.KomoraConnection import KomoraConnection
from komora_syncer.helpers.utils import build_tenant_name
from komora_syncer.models.komora.contact import Contact
from komora_syncer.models.komora.device import Device
from komora_syncer.models.komora.district import District
from komora_syncer.models.komora.inventory import Inventory
from komora_syncer.models.komora.municipality import Municipality
from komora_syncer.models.komora.organization import Organization
from komora_syncer.models.komora.region import Region
from komora_syncer.models.komora.site import Site

# Log Warnings and higher errors from imported modules
logging.getLogger(requests.__name__).setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class KomoraApi:
    cache = {
        'sites': [],
        'regions': [],
        'districts': [],
        'municipalities': [],
        'organizations': [],
        'contacts': [],
        'devices': [],
        'inventories': [],
    }

    def __new__(self):
        raise TypeError("This is a static class")

    @staticmethod
    def store_cache(object_type, objects):
        KomoraApi.cache[object_type] = objects

    @staticmethod
    def get_object_instance(object_type, komora_data):
        object_map = {
            'sites': Site,
            'regions': Region,
            'districts': District,
            'municipalities': Municipality,
            'organizations': Organization,
            'devices': Device,
            'contacts': Contact,
            'inventories': Inventory,
        }
        if object_type not in object_map:
            raise ValueError(f"Unknown object type: {object_type}")
        return object_map[object_type](**komora_data)

    @staticmethod
    def check_cache(object_type):
        return KomoraApi.cache.get(object_type, [])

    @staticmethod
    def get_objects(object_type, api, filter_params=''):
        data = []

        try:
            logger.info(f"Polling {object_type} from Komora")
            for obj in KomoraConnection.get_records(api, filter_params=filter_params):
                data.append(KomoraApi.get_object_instance(object_type, obj))
        except Exception:
            logger.exception(f"Unable to poll {object_type} from Komora")
            raise

        return data

    @staticmethod
    def get_sites():
        sites = KomoraApi.check_cache('sites')
        if not sites:
            sites = KomoraApi.get_objects('sites', 'Site', '')
            KomoraApi.store_cache('sites', sites)
        return sites

    @staticmethod
    def get_organizations():
        organizations = KomoraApi.check_cache('organizations')
        if not organizations:
            organizations = KomoraApi.get_objects(
                'organizations', 'Organization', '')
            # Filter out duplicated CID and Name
            unique_cids_names = set()
            filtered_organizations = []
            for organization in organizations:
                cid_name = build_tenant_name(
                    organization.clientId, organization.name)
                if cid_name not in unique_cids_names:
                    unique_cids_names.add(cid_name)
                    filtered_organizations.append(organization)
                else:
                    logger.critical(f"Duplicated CID and Name: {cid_name}")
            KomoraApi.store_cache('organizations', filtered_organizations)
            organizations = filtered_organizations
        return organizations

    @staticmethod
    def get_regions():
        regions = KomoraApi.check_cache('regions')
        if not regions:
            regions = KomoraApi.get_objects('regions', 'Ruian/region')
            KomoraApi.store_cache('regions', regions)
        return regions

    @staticmethod
    def get_districts():
        districts = KomoraApi.check_cache('districts')
        if not districts:
            districts = KomoraApi.get_objects('districts', 'Ruian/district')
            KomoraApi.store_cache('districts', districts)
        return districts

    @staticmethod
    def get_municipalities():
        municipalities = KomoraApi.check_cache('municipalities')
        if not municipalities:
            municipalities = KomoraApi.get_objects(
                'municipalities', 'Ruian/municipality')
            KomoraApi.store_cache('municipalities', municipalities)
        return municipalities

    @staticmethod
    def get_devices():
        devices = KomoraApi.check_cache('devices')
        if not devices:
            filter_params = 'Filters.IsActive=true'
            devices = KomoraApi.get_objects('devices', 'Device', filter_params)
            KomoraApi.store_cache('devices', devices)
        return devices

    @staticmethod
    def post_devices(nb_devices):
        # Save nb_devices to file
        time_str = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{time_str}_devices.json"
        filepath = get_config()['common']['DEVICES_DATA_PATH']
        file = filepath + filename

        with open(file, 'w') as outfile:
            json.dump(nb_devices, outfile)

        url = KomoraConnection.checkout_url("ServiceRecord/SendDeviceData")

        try:
            logger.info("Posting devices to Komora")
            requests.post(url, files={'dataFile': open(file, 'rb')})
        except requests.exceptions.RequestException:
            logger.exception("Unable to post devices to Komora")
            raise

    @staticmethod
    def get_contacts():
        contacts = KomoraApi.check_cache('contacts')
        if not contacts:
            contacts = KomoraApi.get_objects('contacts', 'Contact')
            KomoraApi.store_cache('contacts', contacts)
        return contacts

    @staticmethod
    def get_inventories():
        inventories = KomoraApi.check_cache('inventories')
        if inventories:
            return inventories

        inventories = KomoraApi.get_objects('inventories', 'Inventarization')
        KomoraApi.store_cache('inventories', inventories)
        return inventories

    @staticmethod
    def post_inventories(nb_inventories):
        api = "ServiceRecord/sendInventarizationData"
        url = KomoraConnection.checkout_url(api)

        time_str = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{time_str}_inventarization.json"
        filepath = get_config()['common']['INVENTARIZATION_DATA_PATH']
        file = filepath + filename

        with open(file, 'w') as outfile:
            json.dump(nb_inventories, outfile)

        try:
            logger.info("Posting inventories to Komora")
            with open(file, 'rb') as data_file:
                requests.post(url, files={'dataFile': data_file})
        except Exception as e:
            logger.exception("Unable to post inventories to Komora")
            raise e
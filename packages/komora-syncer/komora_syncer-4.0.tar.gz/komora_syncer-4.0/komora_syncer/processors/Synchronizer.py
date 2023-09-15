import logging

from komora_syncer.connections.KomoraApi import KomoraApi
from komora_syncer.connections.NetboxConnection import NetboxConnection
from komora_syncer.models.netbox.NbDevice import NbDevice
from komora_syncer.models.netbox.NbInventoryItem import NbInventoryItem
from komora_syncer.models.netbox.NbRegion import NbRegion
from komora_syncer.models.netbox.NbSite import NbSite
from komora_syncer.models.netbox.NbTenant import NbTenant

logger = logging.getLogger(__name__)


class Synchronizer:
    """
    A class for synchronizing data between Komora and NetBox.
    """

    def __init__(self):
        self.sites = []
        self.regions_all = []
        self.districts_all = []
        self.municipalities_all = []
        self.regions_assigned = []
        self.districts_assigned = []
        self.municipalities_assigned = []

    def __prepare_all_regions(self):
        """
        Prepares the lists of all regions, municipalities, districts, and sites from Komora API.
        """
        if not self.regions_all:
            self.regions_all = KomoraApi.get_regions()
        if not self.municipalities_all:
            self.municipalities_all = KomoraApi.get_municipalities()
        if not self.districts_all:
            self.districts_all = KomoraApi.get_districts()
        if not self.sites:
            self.sites = KomoraApi.get_sites()

    def __prepare_assigned_regions(self):
        """
        Prepares the lists of assigned regions, municipalities, districts, and sites from Komora API.
        """
        if not self.regions_all or not self.municipalities_all or not self.districts_all or not self.sites:
            self.__prepare_all_regions()

        municipalities_on_sites = [[site.address.municipalityName,
                                    site.address.districtName] for site in self.sites if site.address]
        self.municipalities_assigned = [muni for muni in self.municipalities_all if [
            muni.name, muni.districtName] in municipalities_on_sites]

        districts_on_assigned_municipalities = set(
            municipality.districtName for municipality in self.municipalities_assigned)
        self.districts_assigned = [
            dis for dis in self.districts_all if dis.name in districts_on_assigned_municipalities]

        regions_on_assigned_districts = set(
            district.regionName for district in self.districts_assigned)
        self.regions_assigned = [
            reg for reg in self.regions_all if reg.name in regions_on_assigned_districts]

        sites_without_address_with_region = [[site.regionId, site.regionName]
                                             for site in self.sites if not site.address and site.regionId]
        self.regions_assigned.extend([reg for reg in self.regions_all if [
                                     reg.id, reg.name] in sites_without_address_with_region])

    def sync_regions(self):
        """
        Synchronizes regions, districts, and municipalities from Komora API to NetBox.
        """
        if not self.regions_assigned or not self.municipalities_assigned or not self.districts_assigned or not self.sites:
            self.__prepare_assigned_regions()

        logger.info("Synchronizing regions")
        for reg in self.regions_assigned:
            try:
                NbRegion(reg, 'region').synchronize()
            except Exception as e:
                logger.exception(
                    f"Failed to synchronize region {reg.name}: {e}")
                raise e

        for dis in self.districts_assigned:
            try:
                NbRegion(dis, 'district').synchronize()
            except Exception as e:
                logger.exception(
                    f"Failed to synchronize district {dis.name}: {e}")
                raise e

        for muni in self.municipalities_assigned:
            try:
                NbRegion(muni, 'municipality').synchronize()
            except Exception as e:
                logger.exception(
                    f"Failed to synchronize municipality {muni.name}: {e}")
                raise e

    def sync_sites(self, site_name=None):
        """
        Synchronizes sites from Komora API to NetBox.
        If site_name is specified, synchronizes only the site with the given name.
        """
        try:
            if not self.sites:
                self.sites = KomoraApi.get_sites()
        except Exception as e:
            raise e

        if site_name:
            logger.info(f"Synchronizing site: {site_name}")
            found_sites = [
                site for site in self.sites if site.name == site_name]
            if len(found_sites) == 0:
                raise ValueError(f"No object found with name '{site_name}'")
            elif len(found_sites) > 1:
                raise ValueError(
                    f"Multiple objects found with name '{site_name}'")
            else:
                try:
                    NbSite(found_sites[0]).synchronize()
                except Exception as e:
                    logger.exception(
                        f"Failed to synchronize site {site_name}: {e}")
                    raise e
        else:
            logger.info("Synchronizing sites")
            for site in self.sites:
                try:
                    NbSite(site).synchronize()
                except Exception as e:
                    logger.exception(
                        f"Failed to synchronize site {site.name}: {e}")
                    raise e

    def sync_organizations(self):
        """
        Synchronizes organizations from Komora API to NetBox.
        """
        organizations = KomoraApi.get_organizations()

        logger.info("Synchronizing organizations")
        for organization in organizations:
            try:
                NbTenant(organization).synchronize()
            except Exception as e:
                logger.exception(
                    f"Failed to synchronize organization {organization.name}: {e}")
                raise e

    def sync_devices(self):
        """
        Synchronizes devices from Komora API to NetBox, and unsets links to Komora for devices not found in Komora API.
        """
        try:
            logger.info("Posting devices")
            post_devices = NbDevice.get_nb_devices_data()
            KomoraApi.post_devices(post_devices)
        except Exception as e:
            raise e

        try:
            devices = KomoraApi.get_devices()
        except Exception as e:
            raise e

        logger.info("Synchronizing devices")
        for dev in devices:
            try:
                NbDevice(dev).synchronize()
            except Exception as e:
                logger.exception(
                    f"Failed to synchronize device {dev.name}: {e}")
                raise e

        komora_ids = [dev.id for dev in devices]
        devices_not_in_komora = NetboxConnection.get_connection(
        ).dcim.devices.filter(cf_komora_id__n=komora_ids)

        devices_to_unset_links = [dev for dev in devices_not_in_komora]
        for dev in devices_to_unset_links:
            dev.custom_fields["komora_id"] = None
            dev.custom_fields["komora_url"] = None

        try:
            if NetboxConnection.get_connection().dcim.devices.update(devices_to_unset_links):
                logger.info("Devices links to Komora successfully unset")
            else:
                logger.info("No device found for unset links to Komora")
        except Exception as e:
            raise e

    def sync_inventory_items(self):
        try:
            logger.info("Posting inventory items")
            post_inventory_items = NbInventoryItem.get_nb_inventory_items_data()
            KomoraApi.post_inventories(post_inventory_items)
        except Exception as e:
            raise e

        try:
            inventories = KomoraApi.get_inventories()
        except Exception as e:
            raise e

        logger.info("Synchronizing inventory items")

        for inv in inventories:
            nb_inv = NbInventoryItem(inv)
            nb_inv.synchronize()

        # TODO: Make method
        # Get all komora_id from devices at Komora system
        komora_ids = [inv.id for inv in inventories]

        # filter devices, which are not stored in KOMORA
        invs_not_in_komora = NetboxConnection.get_connection().dcim.inventory_items.filter(
            cf_komora_id__n=komora_ids)

        # Unset komora link to those devices
        invs_to_update = []
        for inv in invs_not_in_komora:
            inv.custom_fields["komora_id"] = None
            inv.custom_fields["komora_url"] = None
            invs_to_update.append(inv)

        # Update netbox DB
        try:
            if NetboxConnection.get_connection().dcim.inventory_items.update(invs_to_update):
                logger.info(f"Invs links to Komora successfully unset")
            else:
                logger.info(f"No device found for unsetting links to Komora")
        except Exception as e:
            raise e

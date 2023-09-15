import logging
from komora_syncer.connections.NetboxConnection import NetboxConnection


logger = logging.getLogger(__name__)


class NetboxCache():
    nb_client = NetboxConnection.get_connection()
    tenant_cache = {}
    device_cache = {}
    site_cache = {}
    region_cache = {}

    def __init__(self):
        raise TypeError("This is a static class")

    @classmethod
    def init_tenant_cache(cls, force=False):
        if cls.tenant_cache and not force:
            return cls.tenant_cache
        
        try:
            tenants = cls.nb_client.tenancy.tenants.all()
            for tenant in tenants:
                if tenant.custom_fields.get("komora_id"):
                    cls.tenant_cache[tenant.custom_fields.get("komora_id")] = tenant   
        except Exception:
            logger.exception("Unable to initialize tenant cache")
            raise
    
    @classmethod
    def init_device_cache(cls, force=False):
        if cls.device_cache and not force:
            return cls.device_cache
        
        try:
            devices = cls.nb_client.dcim.devices.all()
            for device in devices:
                if device.custom_fields.get("komora_id"):
                    cls.device_cache[device.custom_fields.get("komora_id")] = device
        except Exception:
            logger.exception("Unable to initialize device cache")
            raise
        
    @classmethod
    def init_site_cache(cls, force=False):
        if cls.site_cache and not force:
            return cls.site_cache
        
        try:
            sites = cls.nb_client.dcim.sites.all()
            for site in sites:
                if site.custom_fields.get("komora_id"):
                    cls.site_cache[site.custom_fields.get("komora_id")] = site
        except Exception:
            logger.exception("Unable to initialize site cache")
            raise
        
    @classmethod
    def init_region_cache(cls, force=False):
        if cls.region_cache and not force:
            return cls.region_cache
        try:
            regions = cls.nb_client.dcim.regions.all()
            for region in regions:
                if region.custom_fields.get("komora_id"):
                    cls.region_cache[region.custom_fields.get("komora_id")] = region
        except Exception:
            logger.exception("Unable to initialize region cache")
            raise
                
    @classmethod
    def get_tenant_cache(cls):
        if not cls.tenant_cache:
            cls.init_tenant_cache()
        return cls.tenant_cache
    
    @classmethod
    def get_device_cache(cls):
        if not cls.device_cache:
            cls.init_device_cache()
        return cls.device_cache
    
    @classmethod
    def get_site_cache(cls):
        if not cls.site_cache:
            cls.init_site_cache()
        return cls.site_cache
    
    @classmethod
    def get_region_cache(cls):
        if not cls.region_cache:
            cls.init_region_cache()
        return cls.region_cache
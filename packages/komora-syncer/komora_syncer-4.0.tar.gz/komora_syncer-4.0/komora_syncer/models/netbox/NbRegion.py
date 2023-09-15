import logging
from slugify import slugify

from komora_syncer.models.netbox.NetboxBase import NetboxBase
from komora_syncer.models.netbox.NetboxCache import NetboxCache


logger = logging.getLogger(__name__)


class NbRegion(NetboxBase):
    REGION_TYPES = ['region', 'district', 'municipality']

    def __init__(self, komora_obj=None, region_type=None):
        super().__init__()
        self.api_object = None

        self.name = komora_obj.name
        self.slug = slugify(self.name)
        self.komora_id = komora_obj.id
        self.region_type = region_type

        self.parent = None
        self._find_parent(komora_obj, region_type)

    def _find_parent(self, komora_obj, region_type):
        if self.slug == 'zahranicni-kraj':
            return

        parent_name, parent_type = self._get_parent_info(komora_obj, region_type)
        if not parent_name:
            return

        try:
            self.parent = self.nb.dcim.regions.get(
                name=parent_name, cf_region_type=parent_type, cf_komora_id__n=self.komora_id)
        except Exception as e:
            logger.exception(f"Parent region {parent_name} does not exist")

    def _get_parent_info(self, komora_obj, region_type):
        if region_type == 'region':
            return "CZ", 'state'
        elif region_type == 'district':
            return komora_obj.regionName, 'region'
        elif region_type == 'municipality':
            return komora_obj.districtName, 'district'
        else:
            raise ValueError(f"Invalid region type: {region_type}")

    def find_or_create(self):
        self.find()
        if not self.api_object:
            self.create()

        return self.api_object

    def find(self):
        if self.komora_id:
            try:
                if self.komora_id in NetboxCache.get_region_cache():
                    netbox_region = NetboxCache.get_region_cache()[self.komora_id]
                else:
                    netbox_region = self.nb.dcim.regions.get(cf_komora_id=self.komora_id)
                    
                if netbox_region:
                    self.api_object = netbox_region
                    return self.api_object
            except Exception as e:
                logger.exception(f"Unable to find region by komora_id: {self.komora_id}")
                logger.debug(e)

    def create(self):
        try:
            netbox_region_param = self.params
            netbox_region = self.nb.dcim.regions.create(netbox_region_param)

            logger.info("Region: %s created successfully", self.name)
            self.api_object = netbox_region
        except Exception as e:
            logger.exception("Unable to create netbox site: %s", self.name)
            raise e

        return self.api_object

    def update(self, nb_region):
        try:
            if nb_region.update(self.params):
                self.api_object = nb_region
                logger.info(f"Region: {self.name} updated successfully")
        except Exception as e:
            logger.exception(f"Unable to update region {self.name}")
            raise e

    def synchronize(self):
        region = self.find()

        if region:
            self.update(region)
        else:
            self.create()

    @property
    def params(self):
        params = {'name': self.name, 'slug': self.slug}

        if self.parent:
            params['parent'] = self.parent.id

        if self.komora_id:
            params.setdefault('custom_fields', {})['komora_id'] = self.komora_id

        if self.region_type:
            params.setdefault('custom_fields', {})['region_type'] = self.region_type

        return params
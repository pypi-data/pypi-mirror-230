from komora_syncer.models.netbox.NetboxBase import NetboxBase
from slugify import slugify

import logging

logger = logging.getLogger(__name__)


class NbLocation(NetboxBase):
    def __init__(self, location_komora, parent_location_komora, nb_site):
        super().__init__()
        self.name = str(location_komora.name or "").strip()
        self.slug = slugify(self.name)
        self.description = str(location_komora.description or "").strip()
        self.komora_id = location_komora.id
        self.api_object = None
        self.site = nb_site
        self.parent = None

        if parent_location_komora:
            nb_parent_location = NbLocation(
                parent_location_komora, None, nb_site)
            if nb_parent_location.find():
                self.parent = nb_parent_location.api_object
            else:
                logger.critical(
                    f"Parent object exists: {parent_location_komora.name}, but not found in Netbox")


    def find_or_create(self):
        self.find()
        if not self.api_object:
            self.create()
        return self.api_object

    def find(self):
        try:
            netbox_location = self.nb.dcim.locations.get(
                name__ie=self.name, site_id=self.site.id)
            if netbox_location:
                self.api_object = netbox_location
        except Exception as e:
            logger.exception(
                f"Unable to get location {self.name} {self.site.name} from Netbox")
            raise e
        return self.api_object

    def create(self):
        try:
            netbox_location = self.nb.dcim.locations.create(self.params)

            if netbox_location:
                logger.info("Location: %s created successfully", self.name)
                self.api_object = netbox_location
            else:
                logger.critical(
                    f"Unable to create location {self.name}, site: {self.site_id}")
        except Exception as e:
            logger.exception("Unable to create Netbox location: %s", self.name)
            raise e
        return self.api_object

    def update(self, nb_location):
        try:
            if nb_location.update(self.params):
                self.api_object = nb_location
                logger.info(f"Location: {self.name} updated successfully")
        except Exception as e:
            logger.exception(
                f"Unable to update location {self.name} in Netbox")
            raise e

    def synchronize(self):
        location = self.find()
        if location:
            self.update(location)
        else:
            self.create()

    @property
    def params(self):
        params = {
            'name': self.name,
            'slug': self.slug,
            "description": self.description,
            "site": self.site.id,
        }
        params.update({"parent": self.parent.id} if self.parent else {})
        params.update({"custom_fields": {"komora_id": self.komora_id}} if self.komora_id is not None else {})
        return params
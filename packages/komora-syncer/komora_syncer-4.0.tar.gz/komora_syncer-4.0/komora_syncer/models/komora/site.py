from komora_syncer.models.komora.location import Location
from komora_syncer.models.komora.address import Address
from komora_syncer.models.komora.site_contact import SiteContact


class Site():
    def __init__(self, **kwargs):
        self.name = (kwargs.get('name') or "").strip()
        self.fullName = (kwargs.get('fullName') or "").strip()
        self.description = (kwargs.get('description') or "").strip()
        self.facility = kwargs.get('facility')
        self.latitude = kwargs.get('latitude')
        self.longitude = kwargs.get('longitude')
        self.code = kwargs.get('code')
        self.typeId = kwargs.get('typeId')
        self.typeName = kwargs.get('typeName')
        self.isActive = kwargs.get('isActive')
        self.id = kwargs.get('id')

        self.organizationId = kwargs.get('organizationId')
        self.organizationName = kwargs.get('organizationName')

        if kwargs.get('address', None):
            self.address = Address(**kwargs.get('address'))
        else:
            self.address = kwargs.get('address')

        if kwargs.get('locations', None):
            self.locations = []
            for location in kwargs.get('locations'):
                self.locations.append(Location(**location))
        else:
            self.locations = kwargs.get('locations')

        if kwargs.get('contacts', None):
            self.contacts = []
            for contact in kwargs.get('contacts'):
                self.contacts.append(SiteContact(**contact))
        else:
            self.contacts = kwargs.get('contacts')

        self.flatten_locations = flatten_locations(
            self.locations) if self.locations else []

        self.regionId = kwargs.get('regionId')
        self.regionName = kwargs.get('regionName')

def flatten_locations(nested_locations):
    result = []

    def flat(nested_locations):
        for location in nested_locations:
            result.append(location)
            flat(location.locations)
        return result

    flat(nested_locations)
    return result

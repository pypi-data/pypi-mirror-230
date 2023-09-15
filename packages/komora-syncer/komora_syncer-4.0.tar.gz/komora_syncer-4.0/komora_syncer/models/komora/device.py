class Device():
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.primaryIP4Id = kwargs.get('primaryIP4Id')
        self.primaryIP4Address = kwargs.get('primaryIP4Address')
        self.serialNumber = kwargs.get('serialNumber')
        self.locationId = kwargs.get('locationId')
        self.locationName = kwargs.get('locationName')
        self.siteId = kwargs.get('siteId')
        self.siteName = kwargs.get('siteName')
        self.organizationId = kwargs.get('organizationId')
        self.organizationName = kwargs.get('organizationName')
        self.rackId = kwargs.get('rackId')
        self.rackFace = kwargs.get('rackFace')
        self.validFrom = kwargs.get('validFrom')
        self.validTo = kwargs.get('validTo')
        self.isActive = kwargs.get('isActive')
        self.id = kwargs.get('id')

        self.netBoxId = kwargs.get('netBoxId')

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

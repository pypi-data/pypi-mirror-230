class District():
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.regionId = kwargs.get('regionId')
        self.regionName = kwargs.get('regionName')
        self.isActive = kwargs.get('isActive')
        self.id = kwargs.get('id')

class Inventory():
    def __init__(self, **kwargs):
        '''
           'active': True,
           'assetNumbers': 'T5',
           'deviceId': 9776,
           'deviceName': 'AS1-PRG',
           'deviceSerialNumber': 'FGL164510GR',
           'id': 55,
           'inventarizationNumber': 'T5',
           'lastProbed': '2017-01-01T00:00:00',
           'locationId': None,
           'locationName': None,
           'netboxUrl': 'www.seznam.cz',
           'siteId': 11,
           'siteName': 'Praha-CESNET'
        '''
        self.active = kwargs.get('active')
        self.assetNumbers = kwargs.get('assetNumbers')
        self.deviceId = kwargs.get('deviceId')
        self.deviceName = kwargs.get('deviceName')
        self.deviceSerialNumber = kwargs.get('deviceSerialNumber')
        self.id = kwargs.get('id')
        self.inventarizationNumber = kwargs.get('inventarizationNumber')
        self.lastProbed = kwargs.get('lastProbed')
        self.locationId = kwargs.get('locationId')
        self.locationName = kwargs.get('locationName')
        self.netboxUrl = kwargs.get('netboxUrl')
        self.siteId = kwargs.get('siteId')
        self.siteName = kwargs.get('siteName')

    def __str__(self):
        return self.inventarizationNumber

    def __repr__(self):
        return self.inventarizationNumber

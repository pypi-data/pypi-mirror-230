class SiteContact():
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.firstName = kwargs.get('firstName')
        self.surname = kwargs.get('surname')
        self.fullname = kwargs.get('fullname')
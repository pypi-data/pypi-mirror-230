class Region():
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.isActive = kwargs.get('isActive')
        self.id = kwargs.get('id')

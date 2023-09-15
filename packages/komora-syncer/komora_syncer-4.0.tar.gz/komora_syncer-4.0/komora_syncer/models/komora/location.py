class Location():
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.roomPin = kwargs.get('roomPin')
        self.parentId = kwargs.get('parentId')
        self.id = kwargs.get('id')

        if kwargs.get('locations'):
            self.locations = []
            for location in kwargs.get('locations'):
                self.locations.append(Location(**location))
        else:
            self.locations = kwargs.get('locations')

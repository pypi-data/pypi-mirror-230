class DatasetNameAlreadyExists(Exception):
    def __init__(self, errors):            
        # Call the base class constructor with the parameters it needs
        super().__init__("Dataset name already exists, please choose another name")
            
        # Now for your custom code...
        self.errors = errors
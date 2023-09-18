class auto_attribute:
    def __init__(self, **kwargs) -> None:
        self.set_attribute_with_dictionary(kwargs)

    def __str__(self) -> str:
        return '\n'.join("{key}: {value}".format(key=item[0], value=item[1]) for item in vars(self).items())
    
    def set_attribute(self, **kwargs) -> None:
        self.set_attribute_with_dictionary(kwargs)

    def set_attribute_with_dictionary(self, dictionary) -> None:
        for key, value in dictionary.items():
            setattr(self, key, value)

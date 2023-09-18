class auto_attribute:
    def __init__(self, **kwargs) -> None:
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __str__(self) -> str:
        return '\n'.join("{0}: {1}".format(item[0], item[1]) for item in vars(self).items())

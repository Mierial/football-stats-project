class IntegerOnly:
    def __new__(cls, value):
        if not isinstance(value, int):
            return None
        instance = super().__new__(cls)
        return instance


    def __init__(self, value):
        self.value = value
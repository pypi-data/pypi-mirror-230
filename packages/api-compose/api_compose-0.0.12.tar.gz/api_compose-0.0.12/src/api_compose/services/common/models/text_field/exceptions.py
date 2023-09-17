class FailedToDeserialiseString(Exception):
    def __init__(self,
                 string: str,
                 format: str
                 ):
        self.string = string
        self.format = format

    def __str__(self):
        return f'Failed to Deserialise the below String with format {self.format=} \n' \
               f"{self.string=}"

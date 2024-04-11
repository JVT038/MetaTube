class MetaTubeException(Exception):
    def __init__(self, message, payload=None):
        self.message = message
        self.payload = payload
    def __str__(self):
        return str(self.message)
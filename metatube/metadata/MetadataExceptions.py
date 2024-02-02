from metatube.Exception import MetaTubeException

class InvalidAudioExtension(MetaTubeException):
    pass

class InvalidVideoExtension(MetaTubeException):
    pass

class NoWAVExtension(MetaTubeException):
    pass

class NoAudioTags(MetaTubeException):
    pass

class InvalidAudioFile(MetaTubeException):
    pass

class InvalidVideoFile(MetaTubeException):
    pass

class InvalidCoverURL(MetaTubeException):
    pass

class NoMetadataAPIResult(MetaTubeException):
    pass

class NoMetadataFound(MetaTubeException):
    pass
from metatube.Exception import MetaTubeException
class EmptyFragments(MetaTubeException):
    pass

class NoOutputType(MetaTubeException):
    pass

class InvalidHardwareTranscoding(MetaTubeException):
    pass

class InvalidYouTubeUrl(MetaTubeException):
    pass
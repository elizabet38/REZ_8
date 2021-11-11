

class htmlError(Exception):
    pass


class PageNotFoundError(htmlError):
    pass


class AbuseError(htmlError):
    pass

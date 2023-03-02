class FairCheckerException(Exception):
    """Base class for FAIR-Checker exceptions."""

    pass


class NotYetImplementedException(FairCheckerException):
    """Base class for FAIR-Checker exceptions."""

    pass


class BioschemasProfileException(FairCheckerException):
    """Base class for FAIR-Checker exceptions."""

    pass


class BioschemasProfileNotFoundException(BioschemasProfileException):
    """Base class for FAIR-Checker exceptions."""

    pass

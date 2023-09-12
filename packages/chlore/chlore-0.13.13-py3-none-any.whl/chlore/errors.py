class ChloreError(Exception):
    status_code = 500
    error_code = "EUNKNOWN"
    detail = "Erreur inconnue."


class InternalError(ChloreError):
    """Base class for coding/config error.
    Raise this if the application state is incorrect due to a programmer's error, a misconfiguration, etc...
    """
    status_code = 500
    error_code = "EINTERNAL"
    detail = "Internal error."


class ConfigurationError(InternalError):
    status_code = 500
    detail = "Internal error: application configuration problem."


class ExternalApiError(ChloreError):
    status_code = 500
    error_code = "EUNKNOWN"
    detail = "Unexpected error when using external API."


class NotFound(ChloreError):
    status_code = 404
    error_code = "ENOENT"
    detail = "No such resource."


class PermissionDenied(ChloreError):
    status_code = 403
    error_code = "EPERM"
    detail = "You do not have the required permissions."


class AlreadyExists(ChloreError):
    status_code = 422
    error_code = "EEXIST"
    detail = "You cannot create the resource, it already exists."

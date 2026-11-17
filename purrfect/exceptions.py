from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler
import logging
logger = logging.getLogger(__name__)

class ConflictError(APIException):
    status_code = 409
    default_detail = 'Conflict'
    default_code = 'conflict'

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    request = context.get("request")
    user = getattr(request, "user", None)
    user_id = user.id if user and user.is_authenticated else None

    if response is None:
        return None

    if response.status_code >= 500:
        logger.error("Server error: status=%s, exception=%s, method=%s, path=%s, user_id=%s",
                     response.status_code,
                     type(exc).__name__,
                     getattr(request, "method", None),
                     getattr(request, "path", None),
                     user_id,
                     exc_info=exc,
                     )
    else:
        logger.warning(
            "Api error: status=%s, exception=%s, method=%s, path=%s, user_id=%s",
            response.status_code,
            type(exc).__name__,
            getattr(request, "method", None),
            getattr(request, "path", None),
            user_id,
        )

    if isinstance(exc, ValidationError):
        response.data = {"message": "Validation error", "errors": response.data}
    else:
        response.data = {"message": response.data.get("detail", "Error")}
    return response

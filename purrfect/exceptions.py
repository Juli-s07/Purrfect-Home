from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler

class ConflictError(APIException):
    status_code = 409
    default_detail = 'Conflict'
    default_code = 'conflict'

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    if isinstance(exc, ValidationError):
        response.data = {"message": "Validation error", "errors": response.data}
    else:
        response.data = {"message": response.data.get("detail", "Error")}
    return response

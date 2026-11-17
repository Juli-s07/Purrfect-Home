from rest_framework.permissions import BasePermission, SAFE_METHODS

import logging
logger = logging.getLogger(__name__)

class IsAdminOrReadOnly(BasePermission):
    message = "Only administrator can add, edit and delete."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        allowed =  bool(request.user and request.user.is_staff)
        if not allowed:
            logger.warning("Access denied: user_id=%s, method=%s, path=%s",
                           request.user.id if request.user.is_authenticated else None,
                           request.method,
                           request.path,
                           )
        return allowed

from rest_framework.permissions import BasePermission
from .settings import remote_auth_token


class AllowRemoteAuthServer(BasePermission):
    """
    Allow remote auth server to access this API.
    """

    def has_permission(self, request, view):
        token = request.META.get("HTTP_AUTHORIZATION", None)
        if token is None:
            return False

        if token != remote_auth_token:
            return False

        return True

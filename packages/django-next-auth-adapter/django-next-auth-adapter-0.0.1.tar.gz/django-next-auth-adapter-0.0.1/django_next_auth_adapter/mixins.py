from django.http import HttpRequest
from .response import Response
from rest_framework.response import Response as DRFResponse


class WrappedResponseMixin:
    def is_success_status_code(self, status_code):
        return status_code >= 200 and status_code < 300

    def finalize_response(
        self, request: HttpRequest, response: DRFResponse, *args, **kwargs
    ):
        if self.is_success_status_code(response.status_code):
            wrappend_response = Response.success(
                data=response.data, status=response.status_code
            )
        else:
            wrappend_response = Response.error(
                error=response.data, status=response.status_code
            )
        return super().finalize_response(request, wrappend_response, *args, **kwargs)

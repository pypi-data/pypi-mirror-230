from rest_framework.response import Response as DRFResponse
from typing import Any
from rest_framework import status

SendableJson = dict | Any | None


class Response:
    @staticmethod
    def get_response_dict(
        data: dict, status: int, message: str, error: SendableJson = None
    ):
        return {"data": data, "status": status, "message": message, "error": error}

    @staticmethod
    def success(
        data: SendableJson = None,
        status: int = status.HTTP_200_OK,
        template_name: Any | None = None,
        headers: Any | None = None,
        exception: bool = False,
        content_type: Any | None = None,
    ):
        return DRFResponse(
            data=Response.get_response_dict(
                data=data, status=status, message="success"
            ),
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )

    @staticmethod
    def error(
        data: SendableJson = None,
        status: int = status.HTTP_400_BAD_REQUEST,
        template_name: Any | None = None,
        headers: Any | None = None,
        exception: bool = False,
        content_type: Any | None = None,
        error: SendableJson = None,
    ):
        return DRFResponse(
            data=Response.get_response_dict(
                data=data, status=status, message="error", error=error
            ),
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )

    @staticmethod
    def get_response_schema(schema: dict) -> dict:
        return {
            "type": "object",
            "properties": {
                "data": schema,
                "status": {
                    "type": "integer",
                    "format": "int32",
                },
                "message": {
                    "type": "string",
                },
                "error": {
                    "type": "object",
                    "nullable": True,
                },
            },
        }

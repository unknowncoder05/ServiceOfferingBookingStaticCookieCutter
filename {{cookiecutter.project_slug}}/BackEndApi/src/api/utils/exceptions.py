"""Custom DRF exception handler.

Returns a consistent JSON shape for every error:
  {
    "error": "<human-readable message>",
    "fields": { "<field>": ["<msg>", ...], ... }   # only on validation errors
  }

Unhandled Python exceptions (i.e. bugs) are caught, logged, and returned as
500s instead of crashing with an HTML traceback.
"""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception — log it and return a safe 500
        view = context.get("view")
        logger.exception("Unhandled exception in %s", view.__class__.__name__ if view else "unknown view")
        return Response(
            {"error": "An unexpected error occurred. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = response.data

    # Already normalised (e.g. re-entrant call)
    if isinstance(data, dict) and "error" in data:
        return response

    if isinstance(data, list):
        # e.g. ["This field is required."]
        message = data[0] if data else "Error."
        response.data = {"error": str(message)}
        return response

    if isinstance(data, dict):
        non_field = data.pop("non_field_errors", None)

        if "detail" in data and len(data) == 1:
            # Single DRF detail message — lift it
            response.data = {"error": str(data["detail"])}
            return response

        # Collect field-level errors
        field_errors = {}
        for key, val in data.items():
            if isinstance(val, list):
                field_errors[key] = [str(v) for v in val]
            else:
                field_errors[key] = [str(val)]

        if non_field:
            top_message = str(non_field[0]) if isinstance(non_field, list) else str(non_field)
        elif field_errors:
            # Take the first field error as the top-level message
            first_field_msgs = next(iter(field_errors.values()))
            top_message = first_field_msgs[0] if first_field_msgs else "Validation failed."
        else:
            top_message = "Validation failed."

        result = {"error": top_message}
        if field_errors:
            result["fields"] = field_errors
        response.data = result

    return response

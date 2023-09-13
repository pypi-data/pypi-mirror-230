from typing import Any, Dict

from django.utils.translation import gettext_lazy as _
from drf_spectacular.openapi import AutoSchema as DefaultAutoSchema

from df_api_drf.serializers import ErrorResponseSerializer


class AutoSchema(DefaultAutoSchema):
    def get_response_serializers(self) -> Dict[str, Any]:
        response_serializers = (
            self.view.response_serializer_class
            if hasattr(self.view, "response_serializer_class")
            else super().get_response_serializers()
        )

        responses: Dict[str, Any] = {"400": ErrorResponseSerializer}

        if self.method == "DELETE":
            responses["204"] = {"description": _("No response body")}
        elif self._is_create_operation():
            responses["201"] = response_serializers
        else:
            responses["200"] = response_serializers
        return responses

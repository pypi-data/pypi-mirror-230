from typing import Any, Dict, Optional, Type

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer


def create_and_return_in_view(
    request: Request,
    create_serializer: Type[Serializer],
    return_serializer: Type[Serializer],
    create_context: Optional[Dict[str, Any]] = None,
) -> Response:
    """
    A helper function that is supposed to be used in a create view.

    It takes an create_serializer that serializes the request.data
    and returns the updated model instance via the return_serializer.
    """

    context = {"request": request}
    if create_context:
        context = {**context, **create_context}

    serializer = create_serializer(data=request.data, context=context)

    if serializer.is_valid():
        created_instance = serializer.save()
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        data=return_serializer(instance=created_instance).data,
        status=status.HTTP_201_CREATED,
    )

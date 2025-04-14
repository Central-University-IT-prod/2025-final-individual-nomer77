from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class BulkUpdateOrCreateViewsMixin:
    """
    A generic mixin for bulk creating and updating model instances.
    It immediately returns a 400 response on the first validation error.
    """

    model = None
    pk_field_name = 'id'
    serializer_class = None

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_create_or_update(self, request):
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of objects."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pk_values = set()
        for data in request.data:
            pk_value = data.get(self.pk_field_name)
            if pk_value is None:
                return Response(
                    {"error": f"Field '{self.pk_field_name}' is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if pk_value in pk_values:
                return Response(
                    {"error": "Duplicate UUIDs found in request."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            pk_values.add(pk_value)

        serializer = self.serializer_class(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                data={'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data
        changed_objects = [self.model(**data) for data in validated_data]
        self.model.objects.bulk_update_or_create(
            objects=changed_objects
        )

        return Response(
            data=self.serializer_class(changed_objects, many=True).data,
            status=status.HTTP_201_CREATED
        )


class RemoveNullableValuesSerializerMixin:

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {key: value for key, value in representation.items() if value is not None}
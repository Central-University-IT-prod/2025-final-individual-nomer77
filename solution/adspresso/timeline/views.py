from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from timeline.models import TimeLine


class AdvanceTime(APIView):

    @staticmethod
    def post(request):
        current_date: str | None = request.data.get('current_date')
        if current_date is None:
            return Response(
                data={'detail': 'current_date is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if isinstance(current_date, str):
            if not current_date.isdigit():
                return Response(
                    data={'detail': 'current_date must be digit.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            current_date = int(current_date)
        if current_date < 0:
            return Response(
                data={'detail': 'current_date must be not negative.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        date_obj = TimeLine.get_current_date_object()
        date_obj.current_date = current_date
        date_obj.save()
        return Response(
            data={'current_date': date_obj.current_date},
            status=status.HTTP_200_OK
        )
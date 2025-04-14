from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from MLScorer.serializers import MLScoreSerializer


class MLScoreAPIView(APIView):
    serializer_class = MLScoreSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

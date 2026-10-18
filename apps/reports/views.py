from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .tasks import generate_report


class ReportViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="trigger")
    def trigger(self, request):
        task = generate_report()
        return Response(
            {"message": "Report generation triggered", "task_id": "task.id"},
            status=status.HTTP_202_ACCEPTED,
        )

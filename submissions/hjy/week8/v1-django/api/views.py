from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import ActionItem, Note
from .serializers import ActionItemSerializer, NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        qs = Note.objects.all()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
        ordering = self.request.query_params.get("ordering")
        if ordering:
            qs = qs.order_by(ordering)
        return qs


class ActionItemViewSet(viewsets.ModelViewSet):
    serializer_class = ActionItemSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        qs = ActionItem.objects.all()
        completed = self.request.query_params.get("completed")
        if completed is not None:
            qs = qs.filter(completed=completed.lower() == "true")
        return qs

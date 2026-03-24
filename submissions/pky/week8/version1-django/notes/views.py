from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ActionItem, Note
from .serializers import ActionItemSerializer, NoteSerializer


def _apply_sort(queryset, sort_param, allowed_fields):
    if not sort_param:
        return queryset.order_by("-created_at")
    field = sort_param.lstrip("-")
    if field not in allowed_fields:
        return queryset.order_by("-created_at")
    return queryset.order_by(sort_param)


def _paginate(queryset, request):
    skip = int(request.query_params.get("skip", 0))
    limit = int(request.query_params.get("limit", 100))
    return queryset[skip : skip + limit]


@api_view(["GET", "POST"])
def notes_list(request):
    if request.method == "GET":
        qs = Note.objects.all()
        q = request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
        sort = request.query_params.get("sort")
        qs = _apply_sort(qs, sort, {"title", "created_at", "updated_at"})
        qs = _paginate(qs, request)
        return Response(NoteSerializer(qs, many=True).data)

    serializer = NoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
def notes_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == "GET":
        return Response(NoteSerializer(note).data)
    if request.method == "DELETE":
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = NoteSerializer(note, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["GET", "POST"])
def action_items_list(request):
    if request.method == "GET":
        qs = ActionItem.objects.all()
        completed = request.query_params.get("completed")
        if completed is not None:
            qs = qs.filter(completed=completed.lower() == "true")
        sort = request.query_params.get("sort")
        qs = _apply_sort(qs, sort, {"description", "completed", "created_at", "updated_at"})
        qs = _paginate(qs, request)
        return Response(ActionItemSerializer(qs, many=True).data)

    serializer = ActionItemSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
def action_items_detail(request, pk):
    item = get_object_or_404(ActionItem, pk=pk)
    if request.method == "DELETE":
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = ActionItemSerializer(item, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["PUT"])
def action_items_complete(request, pk):
    item = get_object_or_404(ActionItem, pk=pk)
    item.completed = True
    item.save()
    return Response(ActionItemSerializer(item).data)

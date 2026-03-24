from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ActionItem, Note
from .serializers import ActionItemSerializer, NoteSerializer


# ── Notes ──


@api_view(["GET", "POST"])
def note_list(request):
    if request.method == "POST":
        serializer = NoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    qs = Note.objects.all()

    q = request.query_params.get("q")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))

    sort = request.query_params.get("sort", "-created_at")
    sort_field = sort.lstrip("-")
    valid_fields = {f.name for f in Note._meta.get_fields()}
    if sort_field in valid_fields:
        qs = qs.order_by(sort)
    else:
        qs = qs.order_by("-created_at")

    skip = int(request.query_params.get("skip", 0))
    limit = int(request.query_params.get("limit", 50))
    qs = qs[skip : skip + limit]

    serializer = NoteSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET", "PATCH"])
def note_detail(request, pk):
    try:
        note = Note.objects.get(pk=pk)
    except Note.DoesNotExist:
        return Response({"detail": "Note not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PATCH":
        serializer = NoteSerializer(note, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    serializer = NoteSerializer(note)
    return Response(serializer.data)


# ── Action Items ──


@api_view(["GET", "POST"])
def action_item_list(request):
    if request.method == "POST":
        serializer = ActionItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    qs = ActionItem.objects.all()

    completed = request.query_params.get("completed")
    if completed is not None:
        qs = qs.filter(completed=completed.lower() == "true")

    sort = request.query_params.get("sort", "-created_at")
    sort_field = sort.lstrip("-")
    valid_fields = {f.name for f in ActionItem._meta.get_fields()}
    if sort_field in valid_fields:
        qs = qs.order_by(sort)
    else:
        qs = qs.order_by("-created_at")

    skip = int(request.query_params.get("skip", 0))
    limit = int(request.query_params.get("limit", 50))
    qs = qs[skip : skip + limit]

    serializer = ActionItemSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET", "PATCH"])
def action_item_detail(request, pk):
    try:
        item = ActionItem.objects.get(pk=pk)
    except ActionItem.DoesNotExist:
        return Response(
            {"detail": "Action item not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "PATCH":
        serializer = ActionItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    serializer = ActionItemSerializer(item)
    return Response(serializer.data)


@api_view(["PUT"])
def action_item_complete(request, pk):
    try:
        item = ActionItem.objects.get(pk=pk)
    except ActionItem.DoesNotExist:
        return Response(
            {"detail": "Action item not found"}, status=status.HTTP_404_NOT_FOUND
        )

    item.completed = True
    item.save()
    serializer = ActionItemSerializer(item)
    return Response(serializer.data)

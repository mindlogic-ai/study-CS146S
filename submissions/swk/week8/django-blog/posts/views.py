from rest_framework import viewsets, filters

from .models import Post
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content", "author", "tags"]
    ordering_fields = ["created_at", "title"]
    ordering = ["-created_at"]

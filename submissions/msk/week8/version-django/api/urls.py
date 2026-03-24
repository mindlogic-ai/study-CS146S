from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ActionItemViewSet, NoteViewSet

router = DefaultRouter()
router.register(r"notes", NoteViewSet, basename="note")
router.register(r"action-items", ActionItemViewSet, basename="action-item")

urlpatterns = [
    path("", include(router.urls)),
]

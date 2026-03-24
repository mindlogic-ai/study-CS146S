from django.urls import path

from . import views

urlpatterns = [
    path("notes/", views.notes_list, name="notes-list"),
    path("notes/<int:pk>/", views.notes_detail, name="notes-detail"),
    path("action-items/", views.action_items_list, name="action-items-list"),
    path("action-items/<int:pk>/", views.action_items_detail, name="action-items-detail"),
    path("action-items/<int:pk>/complete/", views.action_items_complete, name="action-items-complete"),
]

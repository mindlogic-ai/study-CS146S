from django.urls import path
from . import views

urlpatterns = [
    path("notes/", views.note_list),
    path("notes/<int:pk>/", views.note_detail),
    path("action-items/", views.action_item_list),
    path("action-items/<int:pk>/", views.action_item_detail),
    path("action-items/<int:pk>/complete/", views.action_item_complete),
]

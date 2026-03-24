from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("api/", include("notes.urls")),
    path("", TemplateView.as_view(template_name="index.html")),
]

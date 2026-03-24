from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import RedirectView

from tracker import views

urlpatterns = [
    path("", RedirectView.as_view(url="/static/index.html")),
    path("api/transactions", views.transactions),
    path("api/transactions/<int:pk>", views.transaction_detail),
    path("api/summary", views.summary),
    path("api/categories", views.categories),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

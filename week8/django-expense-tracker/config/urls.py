from django.urls import path

from tracker import views

urlpatterns = [
    path("api/transactions", views.transactions),
    path("api/transactions/<int:pk>", views.transaction_detail),
    path("api/summary", views.summary),
    path("api/categories", views.categories),
]

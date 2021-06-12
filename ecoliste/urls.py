from django.urls import path

from . import views

urlpatterns = [
    path("", views.search_page, name="search_page"),
    path("structure/<int:enterprise_id>/", views.enterprise, name="enterprise"),
]

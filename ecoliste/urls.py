from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "ecoliste"
urlpatterns = [
    path(_(""), views.search_page, name="search"),
    path(_("entreprise/<int:enterprise_id>/"), views.enterprise, name="enterprise"),
]
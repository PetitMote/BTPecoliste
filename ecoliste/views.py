from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.serializers import serialize
from .models import Enterprise


def search_view(request):
    return render(request, "ecoliste/search.html")


def enterprise_view(request, enterprise_id):
    enterprise = get_object_or_404(Enterprise, pk=enterprise_id)
    addresses = enterprise.addresses.all()
    contacts = enterprise.contacts.all()

    materials = (
        enterprise.products.all()
        .select_related("type", "type__category")
        .prefetch_related("address", "biobased_material")
    )
    addresses_points = serialize(
        "geojson",
        addresses,
        geometry_field="geolocation",
        fields=("text_version", "is_production"),
    )

    context = {
        "enterprise": enterprise,
        "addresses": addresses,
        "materials": materials,
        "contacts": contacts,
        "addresses_points": addresses_points,
    }
    return render(request, "ecoliste/enterprise.html", context)


def about_view(request):
    return render(request, "ecoliste/about.html")

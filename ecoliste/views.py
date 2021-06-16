from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Enterprise, MaterialTypeCategory, MaterialType


def search_view(request):
    return HttpResponse("Page de recherche de matériaux")


def enterprise_view(request, enterprise_id):
    enterprise = get_object_or_404(Enterprise, pk=enterprise_id)
    addresses = enterprise.addresses.all()
    contacts = enterprise.contacts.all()

    materials = (
        enterprise.products.all()
        .select_related("type", "type__category", "origin")
        .prefetch_related("address")
    )

    context = {
        "enterprise": enterprise,
        "addresses": addresses,
        "materials": materials,
        "contacts": contacts,
    }
    return render(request, "ecoliste/enterprise.html", context)

def about_view(request):
    return render(request,"ecoliste/about.html")
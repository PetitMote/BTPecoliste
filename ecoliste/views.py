from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import Http404

# Create your views here.
from .models import Enterprise, Address


def search_page(request):
    return HttpResponse("Page de recherche de matériaux")


def enterprise(request, enterprise_id):
    enterprise = get_object_or_404(Enterprise, pk=enterprise_id)
    addresses = Address.objects.filter(enterprise=enterprise)
    context = {
        "page_title": enterprise.name,
        "enterprise": enterprise,
        "addresses": addresses,
    }
    return render(request, "ecoliste/enterprise.html", context)

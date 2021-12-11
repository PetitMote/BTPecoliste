from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest, QueryDict
from django.core.serializers import serialize
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from .models import Enterprise, Address


def ecoliste_research(
    search_location: Point, distance: int, filters: dict = None
) -> list[Address]:
    """
    The search of addresses corresponding to the user desired parameters.

    :param search_location: A geolocation using a Point object from django.contrib.gis.geos
    :param distance: The distance around the search location, in kilometers
    :param filters: A dictionary containing all available parameters from the models: material types, origin, enterprise
    size… Some parameters (materials, origin, biobased), who can have multiple values at once, need to be organized
    through the form filters[key] = [list of values] even if there is only one value. There should not be empty values
    or [""] values coming from a QueryDict.
    :return: A list of Address objects.
    """
    addresses = Address.objects.filter(
        geolocation__distance_lte=(search_location, D(km=distance))
    )
    if filters:
        if "materials" in filters.keys():
            # This parameter needs to be passed as a list
            addresses = addresses.filter(
                enterprise__products__type_id__in=filters["materials"]
            )
        if "origin" in filters.keys():
            # This parameter needs to be passed as a list
            addresses = addresses.filter(
                enterprise__products__origin__in=filters["origin"]
            )
        if "biobased" in filters.keys():
            # This parameter needs to be passed as a list
            addresses = addresses.filter(
                enterprise__products__biobased_material__id__in=filters["biobased"]
            )
        if "sup_nemployees" in filters.keys():
            # This parameter needs to be passed as a direct value (not a list)
            addresses = addresses.filter(
                enterprise__n_employees__gte=filters["sup_nemployees"]
            )
        if "inf_nemployees" in filters.keys():
            # This parameter needs to be passed as a direct value (not a list)
            addresses = addresses.filter(
                enterprise__n_employees__lte=filters["inf_nemployees"]
            )
        if "sup_sales" in filters.keys():
            # This parameter needs to be passed as a direct value (not a list)
            addresses = addresses.filter(
                enterprise__annual_sales__gte=filters["sup_sales"]
            )
        if "inf_sales" in filters.keys():
            # This parameter needs to be passed as a direct value (not a list)
            addresses = addresses.filter(
                enterprise__annual_sales__lte=filters["inf_sales"]
            )
    return addresses


def ecoliste_research_querydict(
    search_location: Point, search_distance: int, querydict: QueryDict
) -> list[Address]:
    """
    Transcripts the QueryDict to a Dict, removes empty values, and passes it the ecoliste_research function.
    :param search_location: A geolocation using a Point object from django.contrib.gis.geos
    :param search_distance: The distance around the search location, in kilometers
    :param querydict: The QueryDict object sent by the html form.
    :return: A list of Address objects.
    """
    # filters = {key: value for key, value in querydict.lists()}
    filters = {}
    for key, value in querydict.lists():
        if not value == "":
            filters[key] = value
    return ecoliste_research(search_location, search_distance, filters=filters)


def search_view(request: HttpRequest) -> HttpResponse:
    return render(request, "ecoliste/search.html")


def enterprise_view(request: HttpRequest, enterprise_id: int) -> HttpResponse:
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


def about_view(request: HttpRequest) -> HttpResponse:
    return render(request, "ecoliste/about.html")

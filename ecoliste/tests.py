from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from . import models

ENTERPRISE_VIEW = "ecoliste:enterprise"


def add_materials_types() -> None:
    structure = models.MaterialTypeCategory(name="Structure", order=1)
    structure.save()
    isolation = models.MaterialTypeCategory(name="Isolation", order=2)
    isolation.save()
    slabs = models.MaterialType(name="Slabs", order=1, category=structure)
    slabs.save()
    beams = models.MaterialType(name="Beams", order=2, category=structure)
    beams.save()
    panels = models.MaterialType(name="Panels", order=1, category=isolation)
    panels.save()
    bulk = models.MaterialType(name="Bulk", order=2, category=isolation)
    bulk.save()


class EnterpriseViewIdentityTestCase(TestCase):
    def setUp(self) -> None:
        self.enterprise1 = models.Enterprise(
            name="Enterprise 1",
            website="https://enterprise1.com",
            description="Fake enterprise 1 with some data",
            annual_sales=4,
            n_employees=5000,
        )
        self.enterprise1.save()
        self.enterprise2 = models.Enterprise(
            name="Enterprise 2",
            website="https://enterprise2.com",
            description="Fake enterprise 2 with some data",
            annual_sales=3,
            n_employees=1000,
        )
        self.enterprise2.save()
        self.empty_enterprise = models.Enterprise(name="Empty Enterprise")
        self.empty_enterprise.save()

        self.url_enterprise1 = reverse(ENTERPRISE_VIEW, args=[self.enterprise1.pk])
        self.url_enterprise2 = reverse(ENTERPRISE_VIEW, args=[self.enterprise2.pk])
        self.url_empty_enterprise = reverse(
            ENTERPRISE_VIEW, args=[self.empty_enterprise.pk]
        )

    def test_200_response_when_correct_input(self) -> None:
        response = self.client.get(self.url_enterprise1)
        self.assertEqual(response.status_code, 200)

    def test_404_response_when_invalid_enterprise_id(self) -> None:
        url = reverse(ENTERPRISE_VIEW, args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_right_templates_used(self) -> None:
        response = self.client.get(self.url_enterprise1)
        self.assertTemplateUsed(response, "ecoliste/enterprise.html")
        self.assertTemplateUsed(response, "ecoliste/enterprise/identity.html")

    def test_returns_correct_name(self) -> None:
        response = self.client.get(self.url_enterprise1)
        self.assertContains(response, self.enterprise1.name)

    def test_returns_correct_description(self) -> None:
        response = self.client.get(self.url_enterprise1)
        self.assertContains(response, self.enterprise1.description)

    def test_returns_correct_website(self) -> None:
        response = self.client.get(self.url_enterprise1)
        self.assertContains(response, self.enterprise1.website)

    def test_returns_correct_n_employees(self) -> None:
        response = self.client.get(self.url_enterprise1)
        self.assertContains(response, self.enterprise1.get_n_employees_display())

    def test_returns_correct_annual_sales(self) -> None:
        response = self.client.get(self.url_enterprise1)
        self.assertContains(response, self.enterprise1.get_annual_sales_display())

    def test_200_response_for_not_the_first_enterprise(self) -> None:
        response = self.client.get(self.url_enterprise2)
        self.assertEqual(response.status_code, 200)

    def test_returns_not_other_name(self) -> None:
        response = self.client.get(self.url_enterprise1)
        self.assertNotContains(response, self.enterprise2.name)

    def test_returns_not_other_description(self) -> None:
        response = self.client.get(self.url_enterprise1)
        self.assertNotContains(response, self.enterprise2.description)

    def test_empty_website(self) -> None:
        response = self.client.get(self.url_empty_enterprise)
        self.assertContains(response, _("Aucun site web indiqué"))

    def test_empty_description(self) -> None:
        response = self.client.get(self.url_empty_enterprise)
        self.assertContains(response, _("Pas de description"))

    def test_empty_annual_sales(self) -> None:
        response = self.client.get(self.url_empty_enterprise)
        self.assertContains(response, _("Chiffre d'affaires inconnu"))

    def test_empty_n_employees(self) -> None:
        response = self.client.get(self.url_empty_enterprise)
        self.assertContains(response, _("Nombre d'employés inconnu"))


class EnterpriseViewAdressesTestCase(TestCase):
    def setUp(self) -> None:
        self.one_address = models.Enterprise(name="Enterprise 1")
        self.one_address.save()
        self.multi_addresses = models.Enterprise(name="Enterprise 2")
        self.multi_addresses.save()
        self.empty_enterprise = models.Enterprise(name="Empty Enterprise")
        self.empty_enterprise.save()

        self.url_one_address = reverse(ENTERPRISE_VIEW, args=[self.one_address.pk])
        self.url_multi_addresses = reverse(
            ENTERPRISE_VIEW, args=[self.multi_addresses.pk]
        )
        self.url_empty_enterprise = reverse(
            ENTERPRISE_VIEW, args=[self.empty_enterprise.pk]
        )

        self.one_address_address = models.Address(
            enterprise=self.one_address,
            text_version="address 1 of one_address",
            geolocation=Point([10, 10]),
            is_production=False,
        )
        self.one_address_address.save()
        self.multi_addresses_1 = models.Address(
            enterprise=self.multi_addresses,
            text_version="address 1 of multi_addresses",
            geolocation=Point([20, 20]),
            is_production=False,
        )
        self.multi_addresses_1.save()
        self.multi_addresses_2 = models.Address(
            enterprise=self.multi_addresses,
            text_version="address 1 of multi_addresses",
            geolocation=Point([30, 30]),
            is_production=False,
        )
        self.multi_addresses_2.save()

    def test_right_template_used(self) -> None:
        response = self.client.get(self.url_one_address)
        self.assertTemplateUsed(response, "ecoliste/enterprise/addresses.html")

    def test_returns_one_address_text_version(self) -> None:
        response = self.client.get(self.url_one_address)
        self.assertContains(response, self.one_address_address.text_version)

    def test_returns_one_address_geolocation(self) -> None:
        response = self.client.get(self.url_one_address)
        self.assertContains(response, "[10.0, 10.0]")

    def test_returns_multi_addresses_text_versions(self) -> None:
        response = self.client.get(self.url_multi_addresses)
        self.assertContains(response, self.multi_addresses_1.text_version)
        self.assertContains(response, self.multi_addresses_2.text_version)

    def test_returns_multi_addresses_geolocations(self) -> None:
        response = self.client.get(self.url_multi_addresses)
        self.assertContains(response, "[20.0, 20.0]")
        self.assertContains(response, "[30.0, 30.0]")

    def test_returns_not_other_address_text_version(self) -> None:
        response = self.client.get(self.url_multi_addresses)
        self.assertNotContains(response, self.one_address_address.text_version)

    def test_returns_not_other_address_geolocation(self) -> None:
        response = self.client.get(self.url_multi_addresses)
        self.assertNotContains(response, "[10.0, 10.0]")

    def test_empty_address(self) -> None:
        response = self.client.get(self.url_empty_enterprise)
        self.assertContains(response, _("Aucune adresse connue"))

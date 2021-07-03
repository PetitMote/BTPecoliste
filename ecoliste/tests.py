from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from . import models

ENTERPRISE_VIEW = "ecoliste:enterprise"

def add_materials_types():
    structure = models.MaterialTypeCategory(name="Structure", order=1)
    structure.save()
    isolation = models.MaterialTypeCategory(name="Isolation", order=1)
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

        self.url_enterprise1 = reverse(
            ENTERPRISE_VIEW, args=[self.enterprise1.pk]
        )
        self.url_enterprise2 = reverse(
            ENTERPRISE_VIEW, args=[self.enterprise2.pk]
        )
        self.url_empty_enterprise = reverse(
            ENTERPRISE_VIEW, args=[self.empty_enterprise.pk]
        )

    def test_200_response_when_correct_input(self):
        response = self.client.get(self.url_enterprise1)
        self.assertEqual(response.status_code, 200)

    def test_404_response_when_invalid_enterprise_id(self):
        url = reverse(ENTERPRISE_VIEW, args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_right_templates_used(self):
        response = self.client.get(self.url_enterprise1)
        self.assertTemplateUsed(response, "ecoliste/enterprise.html")
        self.assertTemplateUsed(response, "ecoliste/enterprise/identity.html")

    def test_returns_correct_name(self):
        response = self.client.get(self.url_enterprise1)
        self.assertContains(response, self.enterprise1.name)

    def test_returns_correct_description(self):
        response = self.client.get(self.url_enterprise1)
        self.assertContains(response, self.enterprise1.description)

    def test_returns_correct_website(self):
        response = self.client.get(self.url_enterprise1)
        self.assertContains(response, self.enterprise1.website)

    def test_returns_correct_n_employees(self):
        response = self.client.get(self.url_enterprise1)
        self.assertContains(response, self.enterprise1.get_n_employees_display())

    def test_returns_correct_annual_sales(self):
        response = self.client.get(self.url_enterprise1)
        self.assertContains(response, self.enterprise1.get_annual_sales_display())

    def test_200_response_for_not_the_first_enterprise(self):
        response = self.client.get(self.url_enterprise2)
        self.assertEqual(response.status_code, 200)

    def test_returns_not_other_name(self):
        response = self.client.get(self.url_enterprise1)
        self.assertNotContains(response, self.enterprise2.name)

    def test_returns_not_other_description(self):
        response = self.client.get(self.url_enterprise1)
        self.assertNotContains(response, self.enterprise2.description)

    def test_empty_website(self):
        response = self.client.get(self.url_empty_enterprise)
        self.assertContains(response, _("Aucun site web indiqué"))

    def test_empty_description(self):
        response = self.client.get(self.url_empty_enterprise)
        self.assertContains(response, _("Pas de description"))

    def test_empty_annual_sales(self):
        response = self.client.get(self.url_empty_enterprise)
        self.assertContains(response, _("Chiffre d'affaires inconnu"))

    def test_empty_n_employees(self):
        response = self.client.get(self.url_empty_enterprise)
        self.assertContains(response, _("Nombre d'employés inconnu"))

    class EnterpriseViewAdressesTestCas(TestCase):
        def setUp(self) -> None:
            self.enterprise1 = models.Enterprise(name="Enterprise 1")
            self.enterprise1.save()
            self.enterprise2 = models.Enterprise(name="Enterprise 2")
            self.enterprise2.save()
            self.empty_enterprise = models.Enterprise(name="Empty Enterprise")
            self.empty_enterprise.save()

            self.url_enterprise1 = reverse(
                ENTERPRISE_VIEW, args=[self.enterprise1.pk]
            )
            self.url_enterprise2 = reverse(
                ENTERPRISE_VIEW, args=[self.enterprise2.pk]
            )
            self.url_empty_enterprise = reverse(
                ENTERPRISE_VIEW, args=[self.empty_enterprise.pk]
            )

            self.enterprise1_address1 = models.Address()

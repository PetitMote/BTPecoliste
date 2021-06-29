from django.test import TestCase
from django.urls import reverse

from . import models


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

        self.enterprise_path_name = "ecoliste:enterprise"

    def test_200_response_when_correct_input(self):
        url = reverse(self.enterprise_path_name, args=[self.enterprise1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_right_templates_used(self):
        url = reverse(self.enterprise_path_name, args=[self.enterprise1.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, "ecoliste/enterprise.html")
        self.assertTemplateUsed(response, "ecoliste/enterprise/identity.html")

    def test_returns_correct_name(self):
        url = reverse(self.enterprise_path_name, args=[self.enterprise1.pk])
        response = self.client.get(url)
        self.assertContains(response, self.enterprise1.name)

    def test_returns_correct_description(self):
        url = reverse(self.enterprise_path_name, args=[self.enterprise1.pk])
        response = self.client.get(url)
        self.assertContains(response, self.enterprise1.description)

    def test_returns_correct_website(self):
        url = reverse(self.enterprise_path_name, args=[self.enterprise1.pk])
        response = self.client.get(url)
        self.assertContains(response, self.enterprise1.website)

    def test_returns_correct_n_employees(self):
        url = reverse(self.enterprise_path_name, args=[self.enterprise1.pk])
        response = self.client.get(url)
        self.assertContains(response, self.enterprise1.get_n_employees_display())

    def test_returns_correct_annual_sales(self):
        url = reverse(self.enterprise_path_name, args=[self.enterprise1.pk])
        response = self.client.get(url)
        self.assertContains(response, self.enterprise1.get_annual_sales_display())

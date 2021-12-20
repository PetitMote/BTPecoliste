from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from . import models
from .views import ecoliste_research

ENTERPRISE_VIEW = "ecoliste:enterprise"


def add_materials_types() -> list[models.MaterialType]:
    structure = models.MaterialTypeCategory(name="Structure", order=1)
    structure.save()
    isolation = models.MaterialTypeCategory(name="Isolation", order=2)
    isolation.save()

    # Some tests depend on the number of material types here. If you remove some of them, check they still work.
    slabs = models.MaterialType(name="Slabs", order=1, category=structure)
    slabs.save()
    beams = models.MaterialType(name="Beams", order=2, category=structure)
    beams.save()
    panels = models.MaterialType(name="Panels", order=1, category=isolation)
    panels.save()
    bulk = models.MaterialType(name="Bulk", order=2, category=isolation)
    bulk.save()

    return [slabs, beams, panels, bulk]


def add_biobased_origins() -> list[models.BiobasedOriginMaterial]:
    # Some tests will depend on these. Ok to add, careful when removing or modifying existing.
    wood = models.BiobasedOriginMaterial(name="Wood")
    wood.save()
    cotton = models.BiobasedOriginMaterial(name="Cotton")
    cotton.save()
    return [wood, cotton]


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


class EnterpriseViewMaterialsTestCase(TestCase):
    def setUp(self) -> None:
        self.one_material = models.Enterprise(
            name="Enterprise 1",
            website="https://enterprise1.com",
            description="Fake enterprise 1 with some data",
            annual_sales=4,
            n_employees=5000,
        )
        self.one_material.save()
        self.multi_materials = models.Enterprise(
            name="Enterprise 2",
            website="https://enterprise2.com",
            description="Fake enterprise 2 with some data",
            annual_sales=3,
            n_employees=1000,
        )
        self.multi_materials.save()
        self.empty_enterprise = models.Enterprise(name="Empty Enterprise")
        self.empty_enterprise.save()

        self.url_one_material = reverse(ENTERPRISE_VIEW, args=[self.one_material.pk])
        self.url_multi_materials = reverse(
            ENTERPRISE_VIEW, args=[self.multi_materials.pk]
        )
        self.url_empty_enterprise = reverse(
            ENTERPRISE_VIEW, args=[self.empty_enterprise.pk]
        )

        self.mat_types = add_materials_types()
        self.material_one_material = models.MaterialByEnterprise(
            enterprise=self.one_material, type=self.mat_types[0], origin=1
        )
        self.material_one_material.save()

        self.material_multi_1 = models.MaterialByEnterprise(
            enterprise=self.multi_materials, type=self.mat_types[0], origin=1
        )
        self.material_multi_1.save()
        self.material_multi_2 = models.MaterialByEnterprise(
            enterprise=self.multi_materials, type=self.mat_types[1], origin=2
        )
        self.material_multi_2.save()
        self.material_multi_3 = models.MaterialByEnterprise(
            enterprise=self.multi_materials, type=self.mat_types[2], origin=1
        )
        self.material_multi_3.save()
        self.material_multi_4 = models.MaterialByEnterprise(
            enterprise=self.multi_materials, type=self.mat_types[3], origin=2
        )
        self.material_multi_4.save()

    def test_right_template_used(self) -> None:
        response = self.client.get(self.url_one_material)
        self.assertTemplateUsed(response, "ecoliste/enterprise/materials.html")

    def test_returns_one_material(self) -> None:
        response = self.client.get(self.url_one_material)
        self.assertContains(response, self.material_one_material.type.name)

    def test_returns_one_material_category(self) -> None:
        response = self.client.get(self.url_one_material)
        self.assertContains(response, self.material_one_material.type.category.name)

    def test_returns_multi_materials(self) -> None:
        response = self.client.get(self.url_multi_materials)
        self.assertContains(response, self.material_multi_1.type.name)
        self.assertContains(response, self.material_multi_2.type.name)
        self.assertContains(response, self.material_multi_3.type.name)
        self.assertContains(response, self.material_multi_4.type.name)

    def test_returns_multi_material_categories(self):
        response = self.client.get(self.url_multi_materials)
        self.assertContains(response, self.material_multi_1.type.category.name)
        self.assertContains(response, self.material_multi_4.type.category.name)

    def test_returns_not_other_material(self) -> None:
        response = self.client.get(self.url_one_material)
        self.assertNotContains(response, self.material_multi_4.type.name)

    def test_returns_not_other_material_category(self) -> None:
        response = self.client.get(self.url_one_material)
        self.assertNotContains(response, self.material_multi_4.type.category.name)

    def test_empty_materials(self) -> None:
        response = self.client.get(self.url_empty_enterprise)
        for material in self.mat_types:
            self.assertNotContains(response, material.name)


class EnterpriseViewContactsTestCase(TestCase):
    def setUp(self) -> None:
        self.one_contact = models.Enterprise(name="Enterprise 1")
        self.one_contact.save()
        self.multi_contacts = models.Enterprise(name="Enterprise 2")
        self.multi_contacts.save()
        self.empty_enterprise = models.Enterprise(name="Empty Enterprise")
        self.empty_enterprise.save()

        self.url_one_address = reverse(ENTERPRISE_VIEW, args=[self.one_contact.pk])
        self.url_multi_addresses = reverse(
            ENTERPRISE_VIEW, args=[self.multi_contacts.pk]
        )
        self.url_empty_enterprise = reverse(
            ENTERPRISE_VIEW, args=[self.empty_enterprise.pk]
        )

    def test_uses_right_template(self) -> None:
        pass


class SearchFunctionTestCase(TestCase):
    def setUp(self) -> None:
        # [0, 0] to [1, 1] ~157km
        self.search_location = Point([0, 0])

        # Two enterprises to distinguish our results
        self.enterprise1 = models.Enterprise(
            name="Enterprise 1",
            n_employees=models.Enterprise.NEmployees.SMALL,
            annual_sales=models.Enterprise.AnnualSales.SMALL,
        )
        self.enterprise1.save()
        self.enterprise2 = models.Enterprise(
            name="Enterprise 2",
            n_employees=models.Enterprise.NEmployees.BIG,
            annual_sales=models.Enterprise.AnnualSales.BIG,
        )
        self.enterprise2.save()

        # Adding the address for enterprise 1
        self.ent1_address = models.Address(
            enterprise=self.enterprise1,
            text_version="Address for enterprise 1",
            geolocation=Point([1, 1]),
            is_production=False,
        )
        self.ent1_address.save()
        # To use for the search to return this address
        self.search_distance_ent1 = 158

        # Adding addresses to the second enterprise
        self.ent2_address1 = models.Address(
            enterprise=self.enterprise2,
            text_version="Address 1 for enterprise 2",
            geolocation=Point([2, 2]),
            is_production=False,
        )
        self.ent2_address1.save()
        self.ent2_address2 = models.Address(
            enterprise=self.enterprise2,
            text_version="Address 2 for enterprise 2",
            geolocation=Point([3, 3]),
            is_production=False,
        )
        self.ent2_address2.save()
        # To use for the search to return this address
        self.search_distance_multi1 = 158 * 2
        self.search_distance_multi2 = 158 * 3

        # Creating some material types and biobased origins
        self.mat_types = add_materials_types()
        self.bio_origins = add_biobased_origins()

        # Adding materials to enterprise 1
        self.ent1_mat1 = models.MaterialByEnterprise(
            enterprise=self.enterprise1,
            type=self.mat_types[0],
            origin=models.MaterialByEnterprise.MaterialOrigins.REUSE,
        )
        self.ent1_mat1.save()
        self.ent1_mat2 = models.MaterialByEnterprise(
            enterprise=self.enterprise1,
            type=self.mat_types[1],
            origin=models.MaterialByEnterprise.MaterialOrigins.BIOBASED,
        )
        self.ent1_mat2.save()
        self.ent1_mat2.biobased_material.add(self.bio_origins[0])

        # Adding materials to enterprise 2
        self.ent2_mat1 = models.MaterialByEnterprise(
            enterprise=self.enterprise2,
            type=self.mat_types[2],
            origin=models.MaterialByEnterprise.MaterialOrigins.RECYCLED,
        )
        self.ent2_mat1.save()
        self.ent2_mat2 = models.MaterialByEnterprise(
            enterprise=self.enterprise2,
            type=self.mat_types[3],
            origin=models.MaterialByEnterprise.MaterialOrigins.REUSABLE,
        )
        self.ent2_mat2.save()
        self.ent2_mat3 = models.MaterialByEnterprise(
            enterprise=self.enterprise2,
            type=self.mat_types[3],
            origin=models.MaterialByEnterprise.MaterialOrigins.BIOBASED,
        )
        self.ent2_mat3.save()
        self.ent2_mat3.biobased_material.add(self.bio_origins[1])

        # To use for tests with multiple conditions
        self.ent3 = models.Enterprise(
            name="Ent3",
            annual_sales=models.Enterprise.AnnualSales.MEDIUM,
            n_employees=models.Enterprise.NEmployees.MEDIUM,
        )
        self.ent3.save()
        self.ent3_address1 = models.Address(
            enterprise=self.ent3,
            text_version="Ent3 addr1",
            geolocation=Point([-2, 2]),
            is_production=True,
        )
        self.ent3_address1.save()
        self.ent3_addr2 = models.Address(
            enterprise=self.ent3,
            text_version="Ent3 addr1",
            geolocation=Point([-3, 3]),
            is_production=False,
        )
        self.ent3_addr2.save()
        self.ent3_mat1 = models.MaterialByEnterprise(
            enterprise=self.ent3,
            type=self.mat_types[0],
            origin=models.MaterialByEnterprise.MaterialOrigins.RECYCLED,
        )
        self.ent3_mat1.save()

    def test_search_only_distance(self) -> None:
        addresses = ecoliste_research(self.search_location, self.search_distance_ent1)
        self.assertIn(self.ent1_address, addresses)

    def test_search_only_distance_not_other_addresses(self) -> None:
        addresses = ecoliste_research(self.search_location, self.search_distance_ent1)
        self.assertNotIn(self.ent2_address1, addresses)
        self.assertNotIn(self.ent2_address2, addresses)

    def test_search_only_distance_multi_results(self) -> None:
        addresses = ecoliste_research(self.search_location, self.search_distance_multi1)
        self.assertIn(self.ent1_address, addresses)
        self.assertIn(self.ent2_address1, addresses)
        self.assertNotIn(self.ent2_address2, addresses)

    def test_search_materialtype(self) -> None:
        # filter = material type from mat1 from enterprise 1
        filters = {"materials": [self.ent1_mat1.type.id]}
        addresses = ecoliste_research(self.search_location, 1000, filters=filters)
        self.assertIn(self.ent1_address, addresses)
        self.assertNotIn(self.ent2_address1, addresses)
        self.assertNotIn(self.ent2_address2, addresses)

    def test_search_origin(self) -> None:
        # filter = material origin from mat1 from enterprise 1
        filters = {"origin": [self.ent1_mat1.origin]}
        addresses = ecoliste_research(self.search_location, 1000, filters=filters)
        self.assertIn(self.ent1_address, addresses)
        self.assertNotIn(self.ent2_address1, addresses)
        self.assertNotIn(self.ent2_address2, addresses)

    def test_search_biobased(self) -> None:
        filters = {"biobased": [self.bio_origins[0].id]}
        addresses = ecoliste_research(self.search_location, 1000, filters=filters)
        self.assertIn(self.ent1_address, addresses)
        self.assertNotIn(self.ent2_address1, addresses)
        self.assertNotIn(self.ent2_address2, addresses)

    def test_search_nemployees(self):
        filters = {
            "nemployees": (
                models.Enterprise.NEmployees.MEDIUM.value,
                models.Enterprise.NEmployees.BIG,
            )
        }
        addresses = ecoliste_research(self.search_location, 1000, filters=filters)
        self.assertIn(self.ent2_address1, addresses)
        self.assertIn(self.ent2_address2, addresses)
        self.assertNotIn(self.ent1_address, addresses)

    def test_search_sales(self):
        filters = {
            "sales": (
                models.Enterprise.AnnualSales.MEDIUM.value,
                models.Enterprise.AnnualSales.BIG,
            )
        }
        addresses = ecoliste_research(self.search_location, 1000, filters=filters)
        self.assertIn(self.ent2_address1, addresses)
        self.assertIn(self.ent2_address2, addresses)
        self.assertNotIn(self.ent1_address, addresses)

    def test_search_multiple_conditions(self):
        filters = {
            "materials": [self.mat_types[0].id, self.mat_types[2].id],
            "origin": [models.MaterialByEnterprise.MaterialOrigins.RECYCLED],
            "nemployees": (models.Enterprise.NEmployees.MEDIUM.value,
                models.Enterprise.NEmployees.BIG.value,)
        }
        addresses = ecoliste_research(self.search_location, 158 * 2, filters=filters)
        self.assertIn(self.ent3_address1, addresses)
        self.assertIn(self.ent2_address1, addresses)
        self.assertNotIn(self.ent1_address, addresses)
        self.assertNotIn(self.ent2_address2, addresses)

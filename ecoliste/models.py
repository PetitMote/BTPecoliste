# We use the WGS84 spherical projection. It's easier to use, but performances might be impacted. It could be useful
# to change to a local projection. It would need to specify a projection setting, so it's easily changeable,
# and also to reproject the coordinates.

from django.contrib.gis.db import models


class Enterprise(models.Model):
    """
    An enterprise and its identity.

    All the structure depends on this model, as everything links to it.
    """
    name = models.CharField("Nom", max_length=200, null=False)
    website = models.URLField("Site web", max_length=200, null=False, blank=True)
    description = models.TextField("Description", max_length=1000, null=False, blank=True)
    annual_sales = models.PositiveIntegerField("Chiffre d'affaires", null=True, blank=True)
    n_employees = models.PositiveIntegerField("Nombre d'employés", null=True, blank=True)
    added = models.DateField("Date d'ajout", auto_now_add=True)
    updated = models.DateField("Date de mise à jour", auto_now=True)


class Address(models.Model):
    """
    An address where an enterprise has a site.

    The site can be a production site, where materials are made.
    """
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, verbose_name="Entreprise",
                                   related_name="addresses")
    text_version = models.CharField("Adresse textuelle", max_length=400, null=False)
    geolocation = models.PointField("Coordonnées", geography=True, null=False)
    is_production = models.BooleanField("Est un lieu de production")


class MaterialTypeCategory(models.Model):
    """
    These categories are used to regroup Material Types.
    """
    name = models.CharField("Nom de la catégorie", max_length=200, null=False)
    order = models.PositiveSmallIntegerField("Ordre d'affichage", null=False, default=99)


class MaterialType(models.Model):
    """
    Defines the usages of the materials (insulation, beam...).
    """
    category = models.ForeignKey(MaterialTypeCategory, on_delete=models.SET_NULL, null=True,
                                 verbose_name="Catégorie d'usage", related_name="usages")
    name = models.CharField("Usage de matériaux", max_length=200, null=False)
    order = models.PositiveSmallIntegerField("Ordre d'affichage", null=False, default=99)


class MaterialByEnterprise(models.Model):
    """
    A material produced by an enterprise.

    These materials have a type (for their usage), but also an origin. This last one defines why they are "ecological".
    """
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, verbose_name="Entreprise",
                                   related_name="materials_producted")
    type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, verbose_name="Usage", related_name="products")
    origin = models.CharField("Origine", max_length=50, null=False)


class MaterialProductionAddress(models.Model):
    """
    Links the materials to their production addresses.
    """
    material = models.ForeignKey(MaterialByEnterprise, on_delete=models.CASCADE, verbose_name="Matériau",
                                 related_name="production_addresses")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name="Addresse de production",
                                related_name="materials")


class BiobasedOriginMaterial(models.Model):
    """
    Based materials / origins for the biobased materials (wood, straw...).
    """
    name = models.CharField("Nom", max_length=50, null=False)


class LinkBiobasedMaterial(models.Model):
    """
        Links the biobased material to the based material (wood, straw...).
    """
    material = models.ForeignKey(MaterialByEnterprise, on_delete=models.CASCADE,
                                 verbose_name="Matériau de l'entreprise", related_name="biobased_origins")
    biobased_origin = models.ForeignKey(BiobasedOriginMaterial, on_delete=models.CASCADE,
                                        verbose_name="Origine biosourcée", related_name="based_materials")

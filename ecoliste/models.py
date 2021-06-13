# We use the WGS84 spherical projection. It's easier to use, but performances might be impacted. It could be useful
# to change to a local projection. It would need to specify a projection setting, so it's easily changeable,
# and also to reproject the coordinates.

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class Enterprise(models.Model):
    """
    An enterprise and its identity.

    All the structure depends on this model, as everything links to it.
    """

    name = models.CharField(_("Nom"), max_length=200, null=False)
    website = models.URLField(_("Site web"), max_length=200, null=False, blank=True)
    description = models.TextField(
        _("Description"), max_length=1000, null=False, blank=True
    )
    annual_sales = models.PositiveIntegerField(
        _("Chiffre d'affaires"), null=True, blank=True
    )
    n_employees = models.PositiveIntegerField(
        _("Nombre d'employés"), null=True, blank=True
    )
    added = models.DateField(_("Date d'ajout"), auto_now_add=True)
    updated = models.DateField(_("Date de mise à jour"), auto_now=True)

    def __str__(self):
        return self.name


class Address(models.Model):
    """
    An address where an enterprise has a site.

    The site can be a production site, where materials are made.
    """

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        verbose_name=_("Entreprise"),
        related_name="addresses",
    )
    text_version = models.CharField(_("Adresse textuelle"), max_length=400, null=False)
    geolocation = models.PointField(_("Coordonnées"), geography=True, null=False)
    is_production = models.BooleanField(_("Est un lieu de production"))

    def __str__(self):
        return self.text_version


class MaterialTypeCategory(models.Model):
    """
    These categories are used to regroup Material Types.
    """

    name = models.CharField(_("Nom de la catégorie"), max_length=200, null=False)
    order = models.PositiveSmallIntegerField(
        _("Ordre d'affichage"), null=False, default=99
    )

    def __str__(self):
        return self.name


class MaterialType(models.Model):
    """
    Defines the usages of the materials (insulation, beam...).
    """

    category = models.ForeignKey(
        MaterialTypeCategory,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Catégorie de typologie"),
        related_name="usages",
    )
    name = models.CharField(_("Typologie de matériaux"), max_length=200, null=False)
    order = models.PositiveSmallIntegerField(
        _("Ordre d'affichage"), null=False, default=99
    )

    def __str__(self):
        return self.name


class MaterialByEnterprise(models.Model):
    """
    A material produced by an enterprise.

    These materials have a type (for their usage), but also an origin. This last one defines why they are "ecological".
    """

    class MaterialOrigins(models.IntegerChoices):
        REUSE = 1, _("De réemploi")
        BIOBASED = 2, _("Biosourcé")
        RECYCLED = 3, _("Recyclé")
        REUSABLE = 4, _("Réutilisable")

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        verbose_name=_("Entreprise"),
        related_name=_("materials_producted"),
    )
    type = models.ForeignKey(
        MaterialType,
        on_delete=models.CASCADE,
        verbose_name=_("Typologie"),
        related_name="products",
    )
    origin = models.PositiveSmallIntegerField(
        _("Origine"),
        choices=MaterialOrigins.choices,
        null=False,
    )

    def __str__(self):
        return _("{type} {origin} produit par {enterprise}").format(
            type=self.type, origin=self.origin, enterprise=self.enterprise
        )


class MaterialProductionAddress(models.Model):
    """
    Links the materials to their production addresses.
    """

    material = models.ForeignKey(
        MaterialByEnterprise,
        on_delete=models.CASCADE,
        verbose_name=_("Matériau"),
        related_name="production_addresses",
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        verbose_name=_("Addresse de production"),
        related_name="materials",
    )

    def __str__(self):
        return _("{material} à {address}").format(
            material=self.material, address=self.address
        )


class BiobasedOriginMaterial(models.Model):
    """
    Based materials / origins for the biobased materials (wood, straw...).
    """

    name = models.CharField(_("Nom"), max_length=50, null=False)

    def __str__(self):
        return self.name


class LinkBiobasedMaterial(models.Model):
    """
    Links the biobased material to the based material (wood, straw...).
    """

    material = models.ForeignKey(
        MaterialByEnterprise,
        on_delete=models.CASCADE,
        verbose_name=_("Matériau de l'entreprise"),
        related_name="biobased_origins",
    )
    biobased_origin = models.ForeignKey(
        BiobasedOriginMaterial,
        on_delete=models.CASCADE,
        verbose_name=_("Origine biosourcée"),
        related_name="based_materials",
    )

    def __str__(self):
        return _("{material} en {biobased_origin}").format(
            material=self.material, biobased_origin=self.biobased_origin
        )


class Contact(models.Model):
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        verbose_name=_("Entreprise"),
        related_name="contacts",
    )
    firstname = models.CharField(_("Prénom"), max_length=50, null=False)
    surname = models.CharField(_("Nom de famille"), max_length=50, null=False)
    description = models.TextField(_("Description"), max_length=200)
    phone1 = models.CharField(_("Téléphone 1"), max_length=25)
    phone2 = models.CharField(_("Téléphone 2"), max_length=25)
    mail = models.EmailField(_("Adresse mail"))

    def __str__(self):
        return _("{firstname} {surname}").format(
            firstname=self.firstname, surname=self.surname
        )

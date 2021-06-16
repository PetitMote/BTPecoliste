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

    class Meta:
        verbose_name = _("Entreprise")
        verbose_name_plural = _("Entreprises")
        ordering = ["name"]

    class NEmployees(models.IntegerChoices):
        INDIVIDUAL = 1, "1"
        MICRO = 2, "2 - 9"
        SMALL = 10, "10 - 49"
        MEDIUM = 50, "50 - 249"
        MIDSIZE1 = 250, "250 - 999"
        MIDSIZE2 = 1000, "1000 - 4999"
        BIG = 5000, "5000+"

    class AnnualSales(models.IntegerChoices):
        MICRO = 1, _("< 2 millions €")
        SMALL = 2, _("2 à 10 millions €")
        MEDIUM = 3, _("10 à 50 millions €")
        INTERSIZE1 = 4, _("50 à 200 millions €")
        INTERSIZE2 = 5, _("200 à 1500 millions €")
        BIG = 6, _("> 1500 millions €")

    name = models.CharField(_("Nom"), max_length=200, null=False, db_index=True)
    website = models.URLField(
        _("Site web"),
        max_length=200,
        null=False,
        blank=True,
        db_index=True,
    )
    description = models.TextField(
        _("Description"), max_length=1000, null=False, blank=True
    )
    annual_sales = models.PositiveIntegerField(
        _("Chiffre d'affaires"),
        choices=AnnualSales.choices,
        null=True,
        blank=True,
        db_index=True,
    )
    n_employees = models.PositiveIntegerField(
        _("Nombre d'employés"),
        choices=NEmployees.choices,
        null=True,
        blank=True,
        db_index=True,
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

    class Meta:
        verbose_name = _("Adresse")
        verbose_name_plural = _("Adresses")

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        verbose_name=_("Entreprise"),
        related_name="addresses",
        db_index=True,
    )
    text_version = models.CharField(_("Adresse textuelle"), max_length=400, null=False)
    geolocation = models.PointField(
        _("Coordonnées"), geography=True, null=False, spatial_index=True
    )
    is_production = models.BooleanField(_("Est un lieu de production"))

    def __str__(self):
        return self.text_version


class MaterialTypeCategory(models.Model):
    """
    These categories are used to regroup Material Types.
    """

    class Meta:
        verbose_name = _("Catégorie de typologies")
        verbose_name_plural = _("Catégories de typologies")
        ordering = ["order"]

    name = models.CharField(
        _("Nom de la catégorie"), max_length=200, null=False, unique=True
    )
    order = models.PositiveSmallIntegerField(
        _("Ordre d'affichage"), null=False, default=99, db_index=True
    )

    def __str__(self):
        return self.name


class MaterialType(models.Model):
    """
    Defines the usages of the materials (insulation, beam...).
    """

    class Meta:
        verbose_name = _("Typologie de matériaux")
        verbose_name_plural = _("Typologies de matériaux")
        ordering = ["category", "order"]

    category = models.ForeignKey(
        MaterialTypeCategory,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Catégorie de typologie"),
        related_name="usages",
        db_index=True,
    )
    name = models.CharField(
        _("Typologie de matériaux"), max_length=200, null=False, unique=True
    )
    order = models.PositiveSmallIntegerField(
        _("Ordre d'affichage"), null=False, default=99, db_index=True
    )

    def __str__(self):
        return self.name


class MaterialOrigin(models.Model):
    """
    The different ecological origins of the materials (reuse, biobased...).
    """

    class Meta:
        verbose_name = _("Origine écologiques")
        verbose_name_plural = _("Origines écologiques")

    name = models.CharField(
        _("Nom de l'origine"),
        unique=True,
        max_length=50,
        null=False,
    )

    def __str__(self):
        return self.name


class BiobasedOriginMaterial(models.Model):
    """
    Based materials / origins for the biobased materials (wood, straw...).
    """

    class Meta:
        verbose_name = _("Matériau biosourcé")
        verbose_name_plural = _("Matériaux biosourcés")
        ordering = ["name"]

    name = models.CharField(
        _("Nom"), max_length=50, null=False, unique=True, db_index=True
    )

    def __str__(self):
        return self.name


class MaterialByEnterprise(models.Model):
    """
    A material produced by an enterprise.

    These materials have a type (for their usage), but also an origin. This last one defines why they are "ecological".
    """

    class Meta:
        verbose_name = _("Matériau produit")
        verbose_name_plural = _("Matériaux produits")
        ordering = ["type"]
        unique_together = [["enterprise", "type", "origin"]]

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        verbose_name=_("Entreprise"),
        related_name=_("products"),
        db_index=True,
    )
    type = models.ForeignKey(
        MaterialType,
        on_delete=models.CASCADE,
        verbose_name=_("Typologie"),
        related_name="products",
        db_index=True,
    )
    origin = models.ForeignKey(
        MaterialOrigin,
        on_delete=models.CASCADE,
        verbose_name=_("Origine"),
        null=False,
        related_name="materials",
        db_index=True,
    )
    address = models.ManyToManyField(
        Address,
        verbose_name=_("Adresse de production"),
        blank=True,
        related_name="products",
        db_index=True,
    )
    biobased_material = models.ManyToManyField(
        BiobasedOriginMaterial,
        verbose_name=_("Matériau biosourcé"),
        blank=True,
        related_name="products",
        db_index=True,
    )

    def __str__(self):
        return _("{type} {origin} produit par {enterprise}").format(
            type=self.type, origin=self.origin, enterprise=self.enterprise
        )


class Contact(models.Model):
    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        verbose_name=_("Entreprise"),
        related_name="contacts",
        db_index=True,
    )
    firstname = models.CharField(_("Prénom"), max_length=50, null=False, db_index=True)
    surname = models.CharField(
        _("Nom de famille"), max_length=50, null=False, db_index=True, blank=True
    )
    description = models.TextField(_("Description"), max_length=200, blank=True)
    phone1 = models.CharField(
        _("Téléphone 1"), max_length=25, db_index=True, blank=True
    )
    phone2 = models.CharField(
        _("Téléphone 2"), max_length=25, db_index=True, blank=True
    )
    mail = models.EmailField(_("Adresse mail"), db_index=True, null=True, blank=True)

    def __str__(self):
        return _("{firstname} {surname}").format(
            firstname=self.firstname, surname=self.surname
        )

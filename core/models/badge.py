import json
import uuid
from enum import Enum
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator, MinLengthValidator
from django.core.serializers.json import DjangoJSONEncoder

class KeyType(Enum):
    RSA = 'rsa'
    ED25519 = 'ed25519'
    SECP256K1 = 'secp256k1'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class BadgeVersion(Enum):
    V2 = 'v2'
    V3 = 'v3'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class JSONTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.default_type = kwargs.pop('default_type', dict)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return value
        return json.dumps(value, cls=DjangoJSONEncoder)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return self.default_type()
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return self.default_type()

    def to_python(self, value):
        if isinstance(value, (dict, list)):
            return value
        if value is None:
            return self.default_type()
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return self.default_type()

class Issuer(models.Model):
    """Représente un émetteur de badge compatible avec OpenBadge v2 et v3 (Profile en v3)"""
    version = models.CharField(
        _('version'),
        max_length=2,
        choices=BadgeVersion.choices(),
        default=BadgeVersion.V2.value,
        help_text=_('Version du standard OpenBadge utilisée')
    )
    name = models.CharField(
        _('nom'),
        max_length=255,
        help_text=_('Nom de l\'organisation émettrice'),
        validators=[MinLengthValidator(2)]
    )
    url = models.URLField(
        _('site web'),
        validators=[URLValidator()],
        help_text=_('URL du site web de l\'organisation')
    )
    email = models.EmailField(
        _('email de contact'),
        help_text=_('Adresse email de contact de l\'organisation')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Description détaillée de l\'organisation')
    )
    image = models.URLField(
        _('logo'),
        validators=[URLValidator()],
        help_text=_('URL du logo de l\'organisation')
    )
    public_key = models.TextField(
        _('clé publique'),
        blank=True,
        help_text=_('Clé publique pour la vérification des badges signés')
    )
    key_type = models.CharField(
        _('type de clé'),
        max_length=10,
        choices=KeyType.choices(),
        blank=True,
        help_text=_('Type d\'algorithme de signature utilisé')
    )
    privacy_policy = models.URLField(
        _('politique de confidentialité'),
        validators=[URLValidator()],
        blank=True,
        help_text=_('URL de la politique de confidentialité')
    )
    verification = JSONTextField(
        _('vérification'),
        default_type=dict,
        blank=True,
        help_text=_('Méthode de vérification des badges')
    )
    revocation_list = models.URLField(
        _('liste de révocation'),
        validators=[URLValidator()],
        blank=True,
        help_text=_('URL de la liste des badges révoqués')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_issuers',
        verbose_name=_('propriétaire'),
        help_text=_('Utilisateur propriétaire de cet émetteur')
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='joined_issuers',
        verbose_name=_('membres'),
        blank=True,
        help_text=_('Utilisateurs membres de cet émetteur')
    )
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('mis à jour le'), auto_now=True)

    class Meta:
        verbose_name = _('émetteur')
        verbose_name_plural = _('émetteurs')
        ordering = ['name']

    def __str__(self):
        return self.name

class BadgeClass(models.Model):
    """Représente une classe de badge compatible avec OpenBadge v2 et v3 (Achievement en v3)"""
    version = models.CharField(
        _('version'),
        max_length=2,
        choices=BadgeVersion.choices(),
        default=BadgeVersion.V2.value,
        help_text=_('Version du standard OpenBadge utilisée')
    )
    name = models.CharField(
        _('nom'),
        max_length=255,
        help_text=_('Nom du badge'),
        validators=[MinLengthValidator(2)]
    )
    type = models.CharField(
        _('type'),
        max_length=100,
        default='Achievement',
        help_text=_('Type d\'achievement (ex: Badge, Certificate, Diploma)')
    )
    description = models.TextField(
        _('description'),
        help_text=_('Description détaillée du badge et de ses critères d\'obtention')
    )
    image = models.ImageField(
        _('image'),
        upload_to='badges',
        help_text=_('Image du badge')
    )
    criteria_url = models.URLField(
        _('critères'),
        validators=[URLValidator()],
        help_text=_('URL décrivant les critères d\'obtention du badge')
    )
    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.CASCADE,
        verbose_name=_('émetteur'),
        related_name='badge_classes',
        help_text=_('Organisation qui émet ce badge')
    )
    category = models.CharField(
        _('catégorie'),
        max_length=100,
        blank=True,
        help_text=_('Catégorie du badge (ex: compétence, certification)')
    )
    skills = models.TextField(
        _('compétences'),
        blank=True,
        help_text=_('Liste des compétences validées par ce badge')
    )
    level = models.CharField(
        _('niveau'),
        max_length=50,
        blank=True,
        help_text=_('Niveau de difficulté ou de maîtrise')
    )
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('mis à jour le'), auto_now=True)

    class Meta:
        verbose_name = _('classe de badge')
        verbose_name_plural = _('classes de badge')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.issuer.name})"

class Assertion(models.Model):
    """Représente une assertion de badge compatible avec OpenBadge v2 et v3"""
    # Champs communs v2/v3
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('destinataire'),
        related_name='badge_assertions',
        help_text=_('Destinataire du badge')
    )
    badge_class = models.ForeignKey(
        'BadgeClass',
        on_delete=models.CASCADE,
        verbose_name=_('badge'),
        related_name='v2_assertions',
        help_text=_('Badge attribué (v2)')
    )
    achievement = models.ForeignKey(
        'BadgeClass',
        on_delete=models.CASCADE,
        verbose_name=_('achievement'),
        related_name='v3_assertions',
        null=True,
        blank=True,
        help_text=_('Achievement obtenu (v3)')
    )
    issuance_date = models.DateTimeField(
        _('date d\'attribution'),
        auto_now_add=True,
        help_text=_('Date d\'attribution du badge')
    )
    evidence = JSONTextField(
        _('preuves'),
        default_type=list,
        blank=True,
        help_text=_('Liste des preuves justifiant l\'obtention du badge')
    )
    expires_at = models.DateTimeField(
        _('expire le'),
        null=True,
        blank=True,
        help_text=_('Date d\'expiration du badge')
    )
    revoked = models.BooleanField(
        _('révoqué'),
        default=False,
        help_text=_('Indique si le badge a été révoqué')
    )
    revocation_reason = models.TextField(
        _('raison de révocation'),
        blank=True,
        help_text=_('Raison de la révocation du badge')
    )
    
    # Champs d'identification
    identifier = models.URLField(
        _('identifiant'),
        unique=True,
        blank=True,
        help_text=_('URL unique identifiant cette assertion')
    )
    
    def save(self, *args, **kwargs):
        if not self.identifier:
            # Générer un identifiant unique basé sur l'ID
            self.identifier = f'https://example.com/badges/{self.pk if self.pk else uuid.uuid4()}'
        super().save(*args, **kwargs)
    recipient_identifier = models.CharField(
        _('identifiant destinataire'),
        max_length=255,
        default='default@example.com',
        help_text=_('Identifiant unique du destinataire (email, URL, etc.)')
    )
    issued_on = models.DateTimeField(
        _('date d\'émission'),
        auto_now_add=True,
        help_text=_('Date d\'émission du badge')
    )
    evidence_url = models.URLField(
        _('URL des preuves'),
        blank=True,
        help_text=_('URL des preuves justifiant l\'obtention')
    )
    narrative = models.TextField(
        _('description des preuves'),
        blank=True,
        help_text=_('Description détaillée des preuves')
    )
    expires = models.DateTimeField(
        _('date d\'expiration'),
        null=True,
        blank=True,
        help_text=_('Date d\'expiration du badge')
    )

    # Champs spécifiques v3
    version = models.CharField(
        _('version'),
        max_length=2,
        choices=BadgeVersion.choices(),
        default=BadgeVersion.V2.value,
        help_text=_('Version du standard OpenBadge utilisée')
    )
    credential_id = models.URLField(
        _('identifiant'),
        unique=True,
        null=True,
        blank=True,
        help_text=_('Identifiant unique du credential (v3)')
    )
    credential_type = JSONTextField(
        _('types'),
        default_type=list,
        null=True,
        blank=True,
        help_text=_('Types du credential (v3: VerifiableCredential, OpenBadgeCredential)')
    )
    verification = JSONTextField(
        _('vérification'),
        default_type=dict,
        blank=True,
        help_text=_('Méthode de vérification de l\'assertion')
    )
    signature = models.TextField(
        _('signature'),
        blank=True,
        help_text=_('Signature cryptographique de l\'assertion (v3)')
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('destinataire'),
        related_name='badge_assertions',
        help_text=_('Personne recevant le badge')
    )
    achievement = models.ForeignKey(
        BadgeClass,
        on_delete=models.CASCADE,
        verbose_name=_('achievement'),
        related_name='assertions',
        null=True,
        help_text=_('Achievement obtenu')
    )

    evidence = JSONTextField(
        _('preuves'),
        default_type=list,
        blank=True,
        help_text=_('Liste des preuves justifiant l\'obtention du badge')
    )
    verification = JSONTextField(
        _('vérification'),
        default_type=dict,
        blank=True,
        help_text=_('Méthode de vérification de l\'assertion')
    )
    signature = models.TextField(
        _('signature'),
        blank=True,
        help_text=_('Signature cryptographique de l\'assertion')
    )
    expires_at = models.DateTimeField(
        _('expire le'),
        null=True,
        blank=True,
        help_text=_('Date d\'expiration du badge')
    )
    revoked = models.BooleanField(
        _('révoqué'),
        default=False,
        help_text=_('Indique si le badge a été révoqué')
    )
    revocation_reason = models.TextField(
        _('raison de révocation'),
        blank=True,
        help_text=_('Raison de la révocation du badge')
    )

    class Meta:
        verbose_name = _('assertion')
        verbose_name_plural = _('assertions')
        ordering = ['-issuance_date']
        unique_together = [['badge_class', 'recipient']]

    def __str__(self):
        return f"{self.achievement} - {self.recipient.email}"

class Alignment(models.Model):
    """Représente l'alignement avec un référentiel de compétences"""
    badge_class = models.ForeignKey(
        BadgeClass,
        on_delete=models.CASCADE,
        verbose_name=_('badge'),
        related_name='alignments',
        help_text=_('Badge aligné avec le référentiel')
    )
    target_name = models.CharField(
        _('référentiel'),
        max_length=255,
        help_text=_('Nom du référentiel de compétences')
    )
    target_url = models.URLField(
        _('URL'),
        validators=[URLValidator()],
        help_text=_('URL du référentiel')
    )
    target_description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Description du référentiel')
    )
    target_framework = models.CharField(
        _('framework'),
        max_length=255,
        blank=True,
        help_text=_('Nom du framework de compétences')
    )
    target_code = models.CharField(
        _('code'),
        max_length=255,
        blank=True,
        help_text=_('Code de la compétence dans le référentiel')
    )

    class Meta:
        verbose_name = _('alignement')
        verbose_name_plural = _('alignements')
        ordering = ['target_name']

    def __str__(self):
        return f"{self.target_name} - {self.badge_class}"

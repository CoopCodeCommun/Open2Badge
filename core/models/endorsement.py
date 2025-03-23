from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator

from .badge import JSONTextField, BadgeClass, Issuer, Assertion


class EndorsementType(models.TextChoices):
    BADGE_CLASS = 'badge_class', _('Badge')
    ISSUER = 'issuer', _('Émetteur')
    ASSERTION = 'assertion', _('Assertion')


class Endorsement(models.Model):
    """
    Représente un endorsement selon la norme Open Badges v3.0.
    
    Un endorsement est une déclaration faite par une entité (personne ou organisation)
    qui soutient ou approuve un badge, un émetteur, ou une assertion de badge.
    """
    # Identifiant unique de l'endorsement
    id = models.CharField(
        _('identifiant'),
        max_length=255,
        primary_key=True,
        help_text=_('Identifiant unique de l\'endorsement')
    )
    
    # Type d'endorsement (badge, émetteur, assertion)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=EndorsementType.choices,
        help_text=_('Type d\'élément endorsé')
    )
    
    # Liens vers les différents types d'éléments qui peuvent être endorsés
    badge_class = models.ForeignKey(
        BadgeClass,
        on_delete=models.CASCADE,
        verbose_name=_('badge'),
        related_name='endorsements',
        null=True,
        blank=True,
        help_text=_('Badge endorsé')
    )
    
    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.CASCADE,
        verbose_name=_('émetteur'),
        related_name='endorsements',
        null=True,
        blank=True,
        help_text=_('Émetteur endorsé')
    )
    
    assertion = models.ForeignKey(
        Assertion,
        on_delete=models.CASCADE,
        verbose_name=_('assertion'),
        related_name='endorsements',
        null=True,
        blank=True,
        help_text=_('Assertion endorsée')
    )
    
    # Informations sur l'endorser
    endorser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('endorser'),
        related_name='given_endorsements',
        help_text=_('Utilisateur qui fait l\'endorsement')
    )
    
    # Claim de l'endorsement
    claim = JSONTextField(
        _('claim'),
        default_type=dict,
        help_text=_('Déclaration faite par l\'endorser à propos de l\'élément endorsé')
    )
    
    # Informations sur l'endorsement
    issued_on = models.DateTimeField(
        _('date d\'émission'),
        auto_now_add=True,
        help_text=_('Date d\'émission de l\'endorsement')
    )
    
    verification = JSONTextField(
        _('vérification'),
        default_type=dict,
        blank=True,
        help_text=_('Méthode de vérification de l\'endorsement')
    )
    
    # Métadonnées
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('mis à jour le'), auto_now=True)
    
    class Meta:
        verbose_name = _('endorsement')
        verbose_name_plural = _('endorsements')
        ordering = ['-issued_on']
    
    def __str__(self):
        if self.type == EndorsementType.BADGE_CLASS and self.badge_class:
            return f"Endorsement de {self.endorser} pour le badge {self.badge_class}"
        elif self.type == EndorsementType.ISSUER and self.issuer:
            return f"Endorsement de {self.endorser} pour l'émetteur {self.issuer}"
        elif self.type == EndorsementType.ASSERTION and self.assertion:
            return f"Endorsement de {self.endorser} pour l'assertion {self.assertion}"
        return f"Endorsement de {self.endorser}"
    
    def save(self, *args, **kwargs):
        # Vérifier que l'endorsement est lié à un seul type d'élément
        if sum(bool(x) for x in [self.badge_class, self.issuer, self.assertion]) != 1:
            raise ValueError(_("Un endorsement doit être lié à exactement un badge, un émetteur ou une assertion."))
        
        # Générer un identifiant unique si nécessaire
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
            
        super().save(*args, **kwargs)

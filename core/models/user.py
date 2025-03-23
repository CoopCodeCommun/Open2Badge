import secrets
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'adresse email est obligatoire'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Un superuser doit avoir is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Un superuser doit avoir is_superuser=True'))

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    # Champs d'authentification
    email = models.EmailField(_('adresse email'), unique=True)
    is_staff = models.BooleanField(
        _('staff'),
        default=False,
        help_text=_('Peut se connecter à l\'interface d\'administration.')
    )
    is_active = models.BooleanField(
        _('actif'),
        default=True,
        help_text=_('Indique si ce compte est actif.')
    )
    date_joined = models.DateTimeField(_('date d\'inscription'), auto_now_add=True)

    # Validation d'email
    email_verified = models.BooleanField(
        _('email vérifié'),
        default=False,
        help_text=_('Indique si l\'adresse email a été vérifiée.')
    )
    verification_token = models.CharField(
        _('token de vérification'),
        max_length=64,
        blank=True,
        help_text=_('Token pour la vérification d\'email')
    )
    verification_sent_at = models.DateTimeField(
        _('dernier email de vérification'),
        null=True,
        blank=True,
        help_text=_('Date du dernier envoi d\'email de vérification')
    )

    # Profil
    display_name = models.CharField(
        _('nom affiché'),
        max_length=255,
        blank=True,
        help_text=_('Nom affiché publiquement')
    )
    bio = models.TextField(
        _('biographie'),
        blank=True,
        help_text=_('Courte biographie')
    )
    avatar_url = models.URLField(
        _('avatar'),
        blank=True,
        help_text=_('URL de l\'avatar')
    )
    website = models.URLField(
        _('site web'),
        blank=True,
        help_text=_('Site web personnel')
    )

    # Préférences
    language = models.CharField(
        _('langue'),
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        help_text=_('Langue préférée')
    )
    email_notifications = models.BooleanField(
        _('notifications email'),
        default=True,
        help_text=_('Recevoir des notifications par email')
    )
    
    # Rôles
    is_place_admin = models.BooleanField(
        _('administrateur de lieu'),
        default=False,
        help_text=_('Indique si l\'utilisateur est administrateur d\'un lieu et peut endorser des badges.')
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')

    def __str__(self):
        return self.display_name or self.email

    def get_display_name(self):
        return self.display_name or self.email.split('@')[0]

    def generate_verification_token(self):
        """Génère un nouveau token de vérification."""
        self.verification_token = secrets.token_urlsafe(48)
        return self.verification_token

    def send_verification_email(self):
        """Envoie l'email de vérification."""
        if not self.verification_token:
            self.generate_verification_token()

        context = {
            'user': self,
            'verification_url': f"https://localhost:8000/verify-email/{self.verification_token}/"
        }

        send_mail(
            subject=_('Vérifiez votre adresse email'),
            message=render_to_string('core/email/verify_email.txt', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            html_message=render_to_string('core/email/verify_email.html', context)
        )

        self.verification_sent_at = timezone.now()
        self.save(update_fields=['verification_sent_at'])

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.template.response import TemplateResponse

from .models import User, Issuer
from .models.badge import BadgeVersion, KeyType
from .utils.crypto import generate_key_pair


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['email']
    ordering = ['-date_joined']
    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        (_('Permissions'), {
            'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'],
        }),
        (_('Important dates'), {'fields': ['last_login', 'date_joined']}),
    ]


@admin.register(Issuer)
class IssuerAdmin(admin.ModelAdmin):
    change_form_template = 'admin/issuer/change_form.html'
    list_display = ['name', 'email', 'version', 'website_link', 'privacy_policy_link', 'has_key', 'created_at']
    list_filter = ['version', 'created_at', 'key_type']
    search_fields = ['name', 'email', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': ['name', 'description', 'image']
        }),
        (_('Contact'), {
            'fields': ['email', 'url', 'privacy_policy']
        }),
        (_('OpenBadge Configuration'), {
            'fields': ['version', 'key_type', 'public_key', 'verification'],
            'classes': ['collapse'],
            'description': _('Configuration technique pour la signature et la vérification des badges.')
        }),
        (_('Metadata'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse'],
        })
    ]

    def clean_public_key(self, value):
        """Valide le format de la clé publique selon le type choisi"""
        if not value:
            return value

        key_type = self.cleaned_data.get('key_type')
        if not key_type:
            raise ValidationError(_('Le type de clé doit être spécifié'))

        # Vérification basique du format
        if key_type == 'rsa' and not ('BEGIN PUBLIC KEY' in value and 'END PUBLIC KEY' in value):
            raise ValidationError(_('Format de clé RSA invalide'))
        elif key_type == 'ed25519' and len(value.strip()) != 64:
            raise ValidationError(_('La clé Ed25519 doit faire 64 caractères'))
        elif key_type == 'secp256k1' and not value.startswith('0x'):
            raise ValidationError(_('La clé secp256k1 doit commencer par 0x'))

        return value

    def save_model(self, request, obj, form, change):
        """Vérifie la cohérence entre la version et les champs obligatoires"""
        if obj.version == BadgeVersion.V3.value:
            if not obj.public_key:
                messages.warning(request, _('Une clé publique est recommandée pour OpenBadge v3'))
            if not obj.privacy_policy:
                messages.warning(request, _('Une politique de confidentialité est recommandée'))
        
        super().save_model(request, obj, form, change)

    def website_link(self, obj):
        if obj.url:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)
        return '-'
    website_link.short_description = _('Site web')

    def privacy_policy_link(self, obj):
        if obj.privacy_policy:
            return format_html('<a href="{}" target="_blank"><i class="fa fa-shield"></i></a>', obj.privacy_policy)
        return '-'
    privacy_policy_link.short_description = _('Politique')

    def has_key(self, obj):
        if obj.public_key and obj.key_type:
            return format_html('<span style="color: green;"><i class="fa fa-key"></i> {}</span>', obj.key_type)
        return format_html('<span style="color: red;"><i class="fa fa-times"></i></span>')
    has_key.short_description = _('Clé')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/generate_keys/',
                self.admin_site.admin_view(self.generate_keys_view),
                name='core_issuer_generate_keys',
            ),
        ]
        return custom_urls + urls

    def generate_keys_view(self, request, object_id):
        issuer = self.get_object(request, object_id)
        if not issuer:
            return self._get_obj_does_not_exist_redirect(request, self.model._meta, object_id)

        if request.method != 'POST':
            return TemplateResponse(request, 'admin/issuer/generate_keys.html', {
                'issuer': issuer,
                'key_types': KeyType.choices(),
                'opts': self.model._meta,
                'title': _('Générer des clés pour %s') % issuer,
            })

        key_type = request.POST.get('key_type')
        if not key_type:
            self.message_user(request, _('Type de clé requis'), level=messages.ERROR)
            return HttpResponseRedirect('.')

        try:
            private_key, public_key = generate_key_pair(key_type)
            issuer.key_type = key_type
            issuer.public_key = public_key
            issuer.save()

            self.message_user(
                request,
                _('Clés générées avec succès. IMPORTANT : Sauvegardez votre clé privée de manière sécurisée : %s')
                % private_key
            )
        except Exception as e:
            self.message_user(
                request,
                _('Erreur lors de la génération des clés : %s') % str(e),
                level=messages.ERROR
            )

        return HttpResponseRedirect(
            reverse(
                'admin:core_issuer_change',
                args=[object_id],
            )
        )

    def response_change(self, request, obj):
        if '_generate_keys' in request.POST:
            return HttpResponseRedirect(
                reverse(
                    'admin:core_issuer_generate_keys',
                    args=[obj.pk],
                )
            )
        return super().response_change(request, obj)

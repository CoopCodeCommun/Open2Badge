from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, ListView
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import viewsets
from django import forms

from .models import User
from .models.badge import Issuer, BadgeClass, Alignment
from .models.endorsement import Endorsement, EndorsementType

class EmailForm(forms.Form):
    email = forms.EmailField(
        label='Adresse email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

class IssuerForm(forms.ModelForm):
    class Meta:
        model = Issuer
        fields = ['name', 'url', 'email', 'description', 'image', 'public_key', 'key_type', 'privacy_policy', 'verification', 'revocation_list']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de votre organisation'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.exemple.org'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@exemple.org'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description de votre organisation'}),
            'image': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.exemple.org/logo.png'}),
            'public_key': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Clé publique (optionnel)'}),
            'key_type': forms.Select(attrs={'class': 'form-select'}),
            'privacy_policy': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.exemple.org/privacy'}),
            'verification': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '{}'}),
            'revocation_list': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.exemple.org/revocations'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marquer les champs obligatoires
        for field_name in ['name', 'url', 'email', 'image']:
            self.fields[field_name].required = True
            if 'class' in self.fields[field_name].widget.attrs:
                self.fields[field_name].widget.attrs['class'] += ' required'
        
        # Rendre les champs optionnels explicitement non requis
        for field_name in ['public_key', 'key_type', 'privacy_policy', 'verification', 'revocation_list']:
            self.fields[field_name].required = False


class BadgeClassForm(forms.ModelForm):
    class Meta:
        model = BadgeClass
        fields = ['name', 'description', 'image', 'criteria_url', 'issuer', 'category', 'skills', 'level', 'version']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'criteria_url': forms.URLInput(attrs={'class': 'form-control'}),
            'issuer': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'level': forms.TextInput(attrs={'class': 'form-control'}),
            'version': forms.Select(attrs={'class': 'form-select'}),
        }


class AlignmentForm(forms.ModelForm):
    class Meta:
        model = Alignment
        fields = ['target_name', 'target_url', 'target_description', 'target_framework', 'target_code']
        widgets = {
            'target_name': forms.TextInput(attrs={'class': 'form-control'}),
            'target_url': forms.URLInput(attrs={'class': 'form-control'}),
            'target_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'target_framework': forms.TextInput(attrs={'class': 'form-control'}),
            'target_code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EndorsementForm(forms.ModelForm):
    claim_text = forms.CharField(
        label=_('Déclaration d\'endorsement'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Pourquoi endorsez-vous cet élément ?')}),
        help_text=_('Expliquez pourquoi vous endorsez ce badge, cet émetteur ou cette assertion.'),
        required=True
    )
    
    class Meta:
        model = Endorsement
        fields = ['type']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.badge_class = kwargs.pop('badge_class', None)
        self.issuer = kwargs.pop('issuer', None)
        self.assertion = kwargs.pop('assertion', None)
        
        super().__init__(*args, **kwargs)
        
        # Déterminer automatiquement le type d'endorsement en fonction des paramètres fournis
        if self.badge_class:
            self.initial['type'] = EndorsementType.BADGE_CLASS
            self.fields['type'].widget = forms.HiddenInput()
        elif self.issuer:
            self.initial['type'] = EndorsementType.ISSUER
            self.fields['type'].widget = forms.HiddenInput()
        elif self.assertion:
            self.initial['type'] = EndorsementType.ASSERTION
            self.fields['type'].widget = forms.HiddenInput()
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Définir l'endorser
        instance.endorser = self.user
        
        # Générer un identifiant unique pour l'endorsement
        import uuid
        instance.id = f'endorsement-{uuid.uuid4()}'
        
        # Définir l'élément endorsé en fonction du type
        if self.initial['type'] == EndorsementType.BADGE_CLASS:
            instance.badge_class = self.badge_class
        elif self.initial['type'] == EndorsementType.ISSUER:
            instance.issuer = self.issuer
        elif self.initial['type'] == EndorsementType.ASSERTION:
            instance.assertion = self.assertion
        
        # Créer le claim en JSON
        instance.claim = {
            'text': self.cleaned_data['claim_text'],
            'date': timezone.now().isoformat()
        }
        
        if commit:
            instance.save()
        
        return instance

class BaseViewSet(viewsets.ViewSet):
    template_name = None

    def get_template_names(self):
        if self.template_name is None:
            raise NotImplementedError(
                'Template name not defined. Either override template_name '
                'or implement get_template_names().'
            )
        return [self.template_name]

    def get_context_data(self, **kwargs):
        return kwargs

    def render_to_response(self, context):
        return TemplateResponse(
            request=self.request,
            template=self.get_template_names(),
            context=context
        )

class HomeViewSet(BaseViewSet):
    template_name = 'core/home.html'

    def list(self, request):
        return self.render_to_response({})


class PublicIssuerListView(ListView):
    model = Issuer
    template_name = 'core/issuer/public_list.html'
    context_object_name = 'issuers'
    ordering = ['name']

class IssuerViewSet(BaseViewSet):
    template_name = 'core/issuer/list.html'

    def list(self, request):
        issuers = Issuer.objects.all()
        
        # Pour les requêtes HTMX avec le trigger refresh, on renvoie juste la liste partielle
        if 'HX-Request' in request.headers and request.headers.get('HX-Trigger') == 'refresh':
            return TemplateResponse(
                request=request,
                template='core/issuer/partials/issuer_list.html',
                context={'issuers': issuers}
            )
        
        # Pour les requêtes normales, on renvoie la page complète
        return self.render_to_response({
            'issuers': issuers
        })
        
    def create_modal(self, request):
        """Vue dédiée à l'affichage des champs du formulaire d'émetteur"""
        return TemplateResponse(
            request=request,
            template='core/issuer/modal/create_issuer_modal.html',
            context={'form': IssuerForm()}
        )
        
    def create(self, request):
        """Vue d'action pour la création d'un émetteur"""
        if request.method == 'GET':
            # Pour les requêtes normales, on renvoie la page complète
            return self.render_to_response({
                'form': IssuerForm(),
                'title': 'Créer un émetteur'
            })
        
        form = IssuerForm(request.POST, request.FILES)
        if form.is_valid():
            # Définir l'utilisateur connecté comme propriétaire de l'émetteur
            issuer = form.save(commit=False)
            issuer.owner = request.user
            issuer.save()
            messages.success(request, "L'émetteur a été créé avec succès.")
            
            # Pour les requêtes AJAX, on renvoie un statut 200
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse(status=200)
            
            # Pour les requêtes HTMX, on renvoie un code 286 pour indiquer un rafraîchissement
            if 'HX-Request' in request.headers:
                response = HttpResponse(status=286)
                response.headers['HX-Trigger'] = 'refresh'
                return response
            
            # Pour les requêtes normales, on redirige vers la liste
            return redirect('core:issuer-list')
        
        # En cas d'erreur avec AJAX ou HTMX, on renvoie le formulaire avec les erreurs
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'HX-Request' in request.headers:
            return TemplateResponse(
                request=request,
                template='core/issuer/modal/create_issuer_modal.html',
                context={'form': form},
                status=422
            )
        
        # Pour les requêtes normales, on renvoie la page complète avec les erreurs
        return self.render_to_response({
            'form': form,
            'title': 'Créer un émetteur'
        })
        
    def update_modal(self, request, pk):
        """Vue dédiée à l'affichage des champs du formulaire de modification d'émetteur"""
        issuer = get_object_or_404(Issuer, pk=pk)
        
        # Vérifier que l'utilisateur a le droit de modifier cet émetteur
        if not (request.user == issuer.owner or request.user.is_staff):
            return HttpResponse("Vous n'avez pas les droits pour modifier cet émetteur.", status=403)
            
        form = IssuerForm(instance=issuer)
        
        return TemplateResponse(
            request=request,
            template='core/issuer/modal/update_issuer_modal.html',
            context={
                'form': form,
                'issuer': issuer
            }
        )
        
    def update(self, request, pk):
        """Vue d'action pour la modification d'un émetteur"""
        issuer = get_object_or_404(Issuer, pk=pk)
        
        # Vérifier que l'utilisateur a le droit de modifier cet émetteur
        if not (request.user == issuer.owner or request.user.is_staff):
            messages.error(request, "Vous n'avez pas les droits pour modifier cet émetteur.")
            return redirect('core:issuer-list')
            
        if request.method == 'GET':
            # Pour les requêtes GET, on affiche le formulaire de modification
            form = IssuerForm(instance=issuer)
            return TemplateResponse(
                request=request,
                template='core/issuer/modal/update_issuer_modal.html',
                context={
                    'form': form,
                    'issuer': issuer
                }
            )
        
        # Pour les requêtes POST, on traite le formulaire
        form = IssuerForm(request.POST, request.FILES, instance=issuer)
        if form.is_valid():
            form.save()
            messages.success(request, "L'émetteur a été modifié avec succès.")
            
            # Pour les requêtes AJAX, on renvoie un statut 200
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse(status=200)
            
            # Pour les requêtes HTMX, on renvoie un code 286 pour indiquer un rafraîchissement
            if 'HX-Request' in request.headers:
                response = HttpResponse(status=286)
                response.headers['HX-Trigger'] = 'refresh'
                return response
            
            # Pour les requêtes normales, on redirige vers la liste
            return redirect('core:issuer-list')
        
        # En cas d'erreur avec AJAX ou HTMX, on renvoie le formulaire avec les erreurs
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'HX-Request' in request.headers:
            return TemplateResponse(
                request=request,
                template='core/issuer/modal/update_issuer_modal.html',
                context={
                    'form': form,
                    'issuer': issuer
                },
                status=422
            )
        
        # Pour les requêtes normales, on renvoie la page complète avec les erreurs
        return TemplateResponse(
            request=request,
            template='core/issuer/modal/update_issuer_modal.html',
            context={
                'form': form,
                'issuer': issuer
            }
        )


class BadgeClassViewSet(BaseViewSet):
    template_name = 'core/badge/list.html'

    def list(self, request):
        badges = BadgeClass.objects.all()
        
        # Pour les requêtes HTMX avec le trigger refresh, on renvoie juste la liste partielle
        if 'HX-Request' in request.headers and request.headers.get('HX-Trigger') == 'refresh':
            return TemplateResponse(
                request=request,
                template='core/badge/partials/badge_list.html',
                context={'badges': badges}
            )
        
        # Pour les requêtes normales, on renvoie la page complète
        return self.render_to_response({
            'badges': badges
        })
        
    def public_list(self, request):
        """Vue publique pour afficher les badges classés par émetteur"""
        # Récupérer tous les émetteurs qui ont des badges
        issuers_with_badges = Issuer.objects.filter(badge_classes__isnull=False).distinct()
        
        # Déterminer si l'utilisateur est administrateur d'un émetteur
        user_is_issuer_admin = False
        user_issuer_ids = []
        if request.user.is_authenticated:
            # Vérifier si l'utilisateur est propriétaire d'un émetteur ou staff
            if request.user.is_staff:
                user_is_issuer_admin = True
                user_issuer_ids = list(Issuer.objects.all().values_list('id', flat=True))
            else:
                # Vérifier si l'utilisateur est propriétaire d'au moins un émetteur
                user_issuer_ids = list(Issuer.objects.filter(owner=request.user).values_list('id', flat=True))
                if user_issuer_ids:
                    user_is_issuer_admin = True
        
        # Pour chaque émetteur, récupérer ses badges
        issuers_badges = []
        for issuer in issuers_with_badges:
            badges = BadgeClass.objects.filter(issuer=issuer)
            
            # Préparer les badges avec des compétences formatées
            formatted_badges = []
            for badge in badges:
                badge_dict = {
                    'id': badge.id,
                    'name': badge.name,
                    'description': badge.description,
                    'image': badge.image,
                    'criteria_url': badge.criteria_url,
                    'version': badge.version,
                    'category': badge.category,
                    'level': getattr(badge, 'level', None),
                }
                
                # Traiter les compétences si elles existent
                if hasattr(badge, 'skills') and badge.skills:
                    skills_list = [skill.strip() for skill in badge.skills.split(',')]
                    badge_dict['skills_list'] = skills_list
                    badge_dict['skills'] = badge.skills
                
                # Vérifier si le badge est déjà endorsé par un des émetteurs de l'utilisateur
                if user_is_issuer_admin:
                    badge_dict['is_endorsed'] = Endorsement.objects.filter(
                        type=EndorsementType.BADGE_CLASS,
                        badge_class_id=badge.id,
                        issuer_id__in=user_issuer_ids
                    ).exists()
                else:
                    badge_dict['is_endorsed'] = False
                
                formatted_badges.append(badge_dict)
            
            issuers_badges.append({
                'issuer': issuer,
                'badges': formatted_badges
            })
        
        return TemplateResponse(
            request=request,
            template='core/badge/public_list.html',
            context={
                'issuers_badges': issuers_badges,
                'is_public': True,
                'user_is_issuer_admin': user_is_issuer_admin
            }
        )
        
    def my_issuers_badges(self, request):
        """Vue pour afficher les badges des émetteurs de l'utilisateur connecté"""
        # Vérifier que l'utilisateur est connecté
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('core:login')
            
        # Récupérer les émetteurs de l'utilisateur (pour l'exemple, on prend tous les émetteurs)
        # Dans une implémentation réelle, il faudrait filtrer selon les droits de l'utilisateur
        # Par exemple: issuers = Issuer.objects.filter(user=request.user)
        issuers = Issuer.objects.all()
        
        # Pour chaque émetteur, récupérer ses badges
        issuers_badges = []
        for issuer in issuers:
            badges = BadgeClass.objects.filter(issuer=issuer)
            if badges.exists():  # Ne pas inclure les émetteurs sans badges
                # Préparer les badges avec des compétences formatées
                formatted_badges = []
                for badge in badges:
                    badge_dict = {
                        'id': badge.id,
                        'name': badge.name,
                        'description': badge.description,
                        'image': badge.image,
                        'criteria_url': badge.criteria_url,
                        'version': badge.version,
                        'category': badge.category,
                        'level': getattr(badge, 'level', None),
                    }
                    
                    # Traiter les compétences si elles existent
                    if hasattr(badge, 'skills') and badge.skills:
                        skills_list = [skill.strip() for skill in badge.skills.split(',')]
                        badge_dict['skills_list'] = skills_list
                        badge_dict['skills'] = badge.skills
                    
                    formatted_badges.append(badge_dict)
                
                issuers_badges.append({
                    'issuer': issuer,
                    'badges': formatted_badges
                })
        
        return TemplateResponse(
            request=request,
            template='core/badge/public_list.html',  # Réutilisation du même template
            context={
                'issuers_badges': issuers_badges,
                'is_public': False,
                'title': 'Mes badges à émettre',
                'description': 'Badges disponibles pour émission par vos organisations.'
            }
        )
    
    def create_modal(self, request):
        """Vue dédiée à l'affichage des champs du formulaire de badge"""
        return TemplateResponse(
            request=request,
            template='core/badge/partials/badge_form.html',
            context={'form': BadgeClassForm()}
        )
        
    def create(self, request):
        """Vue d'action pour la création d'un badge"""
        if request.method == 'GET':
            # Pour les requêtes normales, on renvoie la page complète
            return self.render_to_response({
                'form': BadgeClassForm(),
                'title': 'Créer un badge'
            })
        
        form = BadgeClassForm(request.POST, request.FILES)
        if form.is_valid():
            badge = form.save()
            messages.success(request, "Le badge a été créé avec succès.")
            
            # Pour les requêtes AJAX, on renvoie un statut 200
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse(status=200)
            
            # Pour les requêtes HTMX, on renvoie un code 286 pour indiquer un rafraîchissement
            if 'HX-Request' in request.headers:
                response = HttpResponse(status=286)
                response.headers['HX-Trigger'] = 'refresh'
                return response
            
            # Pour les requêtes normales, on redirige vers la liste
            return redirect('core:badge-list')
        
        # En cas d'erreur avec AJAX, on renvoie le formulaire avec les erreurs
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'HX-Request' in request.headers:
            return TemplateResponse(
                request=request,
                template='core/badge/partials/badge_form.html',
                context={'form': form},
                status=422
            )
        
        # Pour les requêtes normales, on renvoie la page complète avec les erreurs
        return self.render_to_response({
            'form': form,
            'title': 'Créer un badge'
        })
    
    def detail(self, request, pk):
        """Vue de détail d'un badge avec ses alignements"""
        badge = get_object_or_404(BadgeClass, pk=pk)
        alignments = badge.alignments.all()
        
        return self.render_to_response({
            'badge': badge,
            'alignments': alignments,
            'alignment_form': AlignmentForm()
        })
    
    def edit_modal(self, request, pk):
        """Vue modale pour l'édition d'un badge"""
        badge = get_object_or_404(BadgeClass, pk=pk)
        return TemplateResponse(
            request=request,
            template='core/badge/partials/badge_form.html',
            context={
                'form': BadgeClassForm(instance=badge),
                'badge': badge,
                'is_edit': True
            }
        )
    
    def endorsement_list(self, request):
        """Vue pour afficher la liste des badges à endorser"""
        # Vérifier que l'utilisateur est connecté
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('core:login')
            
        # Vérifier que l'utilisateur est un administrateur de lieu
        if not request.user.is_place_admin and not request.user.is_staff:
            messages.warning(request, "Vous devez être administrateur d'un lieu pour endorser des badges.")
            return redirect('core:home')
        
        # Récupérer tous les émetteurs qui ont des badges
        issuers_with_badges = Issuer.objects.filter(badge_classes__isnull=False).distinct()
        
        # Pour chaque émetteur, récupérer ses badges
        issuers_badges = []
        for issuer in issuers_with_badges:
            badges = BadgeClass.objects.filter(issuer=issuer)
            
            # Préparer les badges avec des compétences formatées
            formatted_badges = []
            for badge in badges:
                # Vérifier si l'utilisateur a déjà endorsé ce badge
                has_endorsed = Endorsement.objects.filter(
                    endorser=request.user,
                    badge_class=badge
                ).exists()
                
                badge_dict = {
                    'id': badge.id,
                    'name': badge.name,
                    'description': badge.description,
                    'image': badge.image,
                    'criteria_url': badge.criteria_url,
                    'version': badge.version,
                    'category': badge.category,
                    'level': getattr(badge, 'level', None),
                    'has_endorsed': has_endorsed
                }
                
                # Traiter les compétences si elles existent
                if hasattr(badge, 'skills') and badge.skills:
                    skills_list = [skill.strip() for skill in badge.skills.split(',')]
                    badge_dict['skills_list'] = skills_list
                    badge_dict['skills'] = badge.skills
                
                formatted_badges.append(badge_dict)
            
            if formatted_badges:  # Ne pas inclure les émetteurs sans badges
                issuers_badges.append({
                    'issuer': issuer,
                    'badges': formatted_badges
                })
        
        return TemplateResponse(
            request=request,
            template='core/badge/endorsement_list.html',
            context={
                'issuers_badges': issuers_badges,
                'title': 'Endorser des badges',
                'description': 'En tant qu\'administrateur de lieu, vous pouvez endorser des badges pour indiquer leur pertinence.'
            }
        )
    
    def update(self, request, pk):
        """Vue d'action pour la mise à jour d'un badge"""
        badge = get_object_or_404(BadgeClass, pk=pk)
        
        if request.method == 'GET':
            return self.render_to_response({
                'form': BadgeClassForm(instance=badge),
                'title': f'Modifier {badge.name}',
                'badge': badge
            })
        
        form = BadgeClassForm(request.POST, request.FILES, instance=badge)
        if form.is_valid():
            badge = form.save()
            messages.success(request, "Le badge a été mis à jour avec succès.")
            
            # Pour les requêtes AJAX, on renvoie un statut 200
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse(status=200)
            
            # Pour les requêtes HTMX, on renvoie un code 286 pour indiquer un rafraîchissement
            if 'HX-Request' in request.headers:
                response = HttpResponse(status=286)
                response.headers['HX-Trigger'] = 'refresh'
                return response
            
            # Pour les requêtes normales, on redirige vers la page de détail
            return redirect('core:badge-detail', pk=pk)
        
        # En cas d'erreur avec AJAX ou HTMX, on renvoie le formulaire avec les erreurs
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'HX-Request' in request.headers:
            return TemplateResponse(
                request=request,
                template='core/badge/partials/badge_form.html',
                context={
                    'form': form,
                    'badge': badge,
                    'is_edit': True
                },
                status=422
            )
        
        # Pour les requêtes normales, on renvoie la page complète avec les erreurs
        return self.render_to_response({
            'form': form,
            'title': f'Modifier {badge.name}',
            'badge': badge
        })
    
    def add_alignment_modal(self, request, pk):
        """Vue modale pour l'ajout d'un alignement"""
        badge = get_object_or_404(BadgeClass, pk=pk)
        return TemplateResponse(
            request=request,
            template='core/badge/partials/alignment_form.html',
            context={
                'form': AlignmentForm(),
                'badge': badge
            }
        )
    
    def add_alignment(self, request, pk):
        """Vue d'action pour l'ajout d'un alignement"""
        badge = get_object_or_404(BadgeClass, pk=pk)
        form = AlignmentForm(request.POST)
        
        if form.is_valid():
            alignment = form.save(commit=False)
            alignment.badge_class = badge
            alignment.save()
            messages.success(request, "L'alignement a été ajouté avec succès.")
            
            # Pour les requêtes HTMX, on renvoie la liste mise à jour
            if 'HX-Request' in request.headers:
                return TemplateResponse(
                    request=request,
                    template='core/badge/partials/alignments_list.html',
                    context={
                        'alignments': badge.alignments.all(),
                        'badge': badge
                    }
                )
            
            # Pour les requêtes normales, on redirige vers la page de détail
            return redirect('core:badge-detail', pk=pk)
        
        # En cas d'erreur avec HTMX, on renvoie le formulaire avec les erreurs
        if 'HX-Request' in request.headers:
            return TemplateResponse(
                request=request,
                template='core/badge/partials/alignment_form.html',
                context={
                    'form': form,
                    'badge': badge
                },
                status=422
            )
        
        # Pour les requêtes normales, on renvoie la page de détail avec les erreurs
        return self.render_to_response({
            'badge': badge,
            'alignments': badge.alignments.all(),
            'alignment_form': form
        })
    
    def delete_alignment(self, request, pk, alignment_pk):
        """Vue d'action pour la suppression d'un alignement"""
        alignment = get_object_or_404(Alignment, pk=alignment_pk, badge_class_id=pk)
        badge = alignment.badge_class
        
        alignment.delete()
        messages.success(request, "L'alignement a été supprimé avec succès.")
        
        # Pour les requêtes HTMX, on renvoie la liste mise à jour
        if 'HX-Request' in request.headers:
            return TemplateResponse(
                request=request,
                template='core/badge/partials/alignments_list.html',
                context={
                    'alignments': badge.alignments.all(),
                    'badge': badge
                }
            )
        
        # Pour les requêtes normales, on redirige vers la page de détail
        return redirect('core:badge-detail', pk=pk)
        
    def create(self, request):
        """Vue d'action pour la création d'un badge"""
        if request.method == 'GET':
            # Pour les requêtes normales, on renvoie la page complète
            return self.render_to_response({
                'form': BadgeClassForm(),
                'title': 'Créer un badge'
            })
        
        form = BadgeClassForm(request.POST, request.FILES)
        if form.is_valid():
            badge = form.save()
            messages.success(request, "Le badge a été créé avec succès.")
            
            # Pour les requêtes AJAX, on renvoie un statut 200
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse(status=200)
            
            # Pour les requêtes HTMX, on renvoie un code 286 pour indiquer un rafraîchissement
            if 'HX-Request' in request.headers:
                response = HttpResponse(status=286)
                response.headers['HX-Trigger'] = 'refresh'
                return response
            
            # Pour les requêtes normales, on redirige vers la liste
            return redirect('core:badge-list')
        
        # En cas d'erreur avec AJAX, on renvoie le formulaire avec les erreurs
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'HX-Request' in request.headers:
            return TemplateResponse(
                request=request,
                template='core/badge/partials/badge_form.html',
                context={'form': form},
                status=422
            )
        
        # Pour les requêtes normales, on renvoie la page complète avec les erreurs
        return self.render_to_response({
            'form': form,
            'title': 'Créer un badge'
        })
    

    
    def delete(self, request, pk=None):
        issuer = get_object_or_404(Issuer, pk=pk)
        
        if request.method == 'GET':
            return self.render_to_response({
                'issuer': issuer,
                'title': f'Supprimer {issuer.name}'
            })
        
        issuer.delete()
        if 'HX-Request' in request.headers:
            return HttpResponse(
                status=204,
                headers={'HX-Trigger': 'issuerListChanged'}
            )
        return redirect('core:issuer-list')

class AuthViewSet(BaseViewSet):
    template_name = 'core/auth/login.html'

    def login(self, request):
        if request.method == 'GET':
            form = EmailForm()
            return self.render_to_response({'form': form})
        
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user, created = User.objects.get_or_create(email=email)
            
            # Envoie l'email de vérification si c'est un nouveau compte
            if created:
                user.send_verification_email()
            
            login(request, user)
            
            # Retourne le menu utilisateur mis à jour
            if 'HX-Request' in request.headers:
                response = TemplateResponse(
                    request,
                    'partials/user_menu.html',
                    {'user': user}
                )
                response['HX-Trigger'] = 'userAuthenticated'
                return response
            return redirect('core:profile')
        
        # En cas d'erreur, retourne le formulaire avec les erreurs
        if 'HX-Request' in request.headers:
            return TemplateResponse(
                request,
                'partials/login_modal.html',
                {'form': form},
                status=400
            )
        return self.render_to_response({'form': form}, status=400)

    def logout(self, request):
        if not request.method == 'POST':
            return HttpResponse(status=405)

        logout(request)
        if 'HX-Request' in request.headers:
            response = TemplateResponse(
                request,
                'partials/user_menu.html',
                {'user': None}
            )
            response['HX-Trigger'] = 'userLoggedOut'
            return response
        return redirect('core:home')
    
    # Définir le template pour la vue profile
    profile_template_name = 'core/auth/profile.html'
    
    def profile(self, request):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        if request.method == 'POST':
            # Mise à jour du profil
            user = request.user
            user.display_name = request.POST.get('display_name', '')
            user.bio = request.POST.get('bio', '')
            user.website = request.POST.get('website', '')
            user.avatar_url = request.POST.get('avatar_url', '')
            user.language = request.POST.get('language', settings.LANGUAGE_CODE)
            user.email_notifications = request.POST.get('email_notifications') == 'on'
            user.save()
            
            if 'HX-Request' in request.headers:
                messages.success(request, _('Profil mis à jour avec succès.'))
                return HttpResponse(status=200)
            return redirect('core:profile')
        
        # Récupérer les émetteurs rejoints par l'utilisateur
        joined_issuers = request.user.joined_issuers.all()
        
        # Récupérer les émetteurs disponibles (que l'utilisateur n'a pas encore rejoints)
        available_issuers = Issuer.objects.exclude(members=request.user).exclude(owner=request.user)
        
        # Récupérer les badges disponibles à endorser
        badges = BadgeClass.objects.all().order_by('-created_at')[:12]  # Limiter à 12 badges récents
        
        # Récupérer les émetteurs que l'utilisateur peut utiliser pour endorser (ceux qu'il a rejoints ou dont il est propriétaire)
        user_issuers = list(joined_issuers) + list(Issuer.objects.filter(owner=request.user))
        
        context = {
            'languages': settings.LANGUAGES,
            'joined_issuers': joined_issuers,
            'available_issuers': available_issuers,
            'badges': badges,
            'user_issuers': user_issuers
        }
        
        # Sauvegarder le template actuel
        original_template = self.template_name
        # Définir le template pour cette requête
        self.template_name = self.profile_template_name
        # Rendre la réponse
        response = self.render_to_response(context)
        # Restaurer le template original
        self.template_name = original_template
        return response
        
    def profile_endorsement_badges(self, request):
        """Récupère les badges disponibles à endorser pour la page de profil"""
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        
        # Récupérer les badges disponibles à endorser
        badges = BadgeClass.objects.all().order_by('-created_at')[:12]  # Limiter à 12 badges récents
        
        # Récupérer les émetteurs que l'utilisateur peut utiliser pour endorser
        user_issuers = list(request.user.joined_issuers.all()) + list(Issuer.objects.filter(owner=request.user))
        
        # Récupérer les endorsements de l'utilisateur pour ces badges
        from .models.endorsement import Endorsement
        
        # Créer un dictionnaire pour stocker les badges déjà endorsés par l'utilisateur
        user_endorsed_badges = {}
        for badge in badges:
            # Vérifier si l'utilisateur a déjà endorsé ce badge en son nom
            user_endorsed = Endorsement.objects.filter(
                badge_class=badge,
                endorser=request.user,
                issuer__isnull=True
            ).exists()
            
            # Stocker le résultat dans le dictionnaire
            user_endorsed_badges[badge.id] = user_endorsed
        
        # Créer un dictionnaire pour stocker les badges déjà endorsés par l'utilisateur au nom d'un émetteur
        issuer_endorsed_badges = {}
        for badge in badges:
            # Pour chaque émetteur, vérifier si le badge a déjà été endorsé
            issuer_endorsed = {}
            for issuer in user_issuers:
                endorsed = Endorsement.objects.filter(
                    badge_class=badge,
                    endorser=request.user,
                    issuer=issuer
                ).exists()
                issuer_endorsed[issuer.id] = endorsed
            
            # Stocker le résultat dans le dictionnaire
            issuer_endorsed_badges[badge.id] = issuer_endorsed
        
        context = {
            'badges': badges,
            'user_issuers': user_issuers,
            'user_endorsed_badges': user_endorsed_badges,
            'issuer_endorsed_badges': issuer_endorsed_badges
        }
        
        return TemplateResponse(
            request,
            'core/auth/partials/endorsement_badges.html',
            context
        )
        
    def join_issuer(self, request, issuer_id):
        if not request.user.is_authenticated:
            if 'HX-Request' in request.headers:
                return HttpResponse(status=401)
            return redirect('core:login')
        
        issuer = get_object_or_404(Issuer, id=issuer_id)
        
        # Vérifier si l'utilisateur est déjà membre ou propriétaire
        if request.user == issuer.owner or issuer.members.filter(id=request.user.id).exists():
            messages.warning(request, _("Vous êtes déjà membre de cet émetteur."))
        else:
            # Ajouter l'utilisateur aux membres de l'émetteur
            issuer.members.add(request.user)
            messages.success(request, _(f"Vous avez rejoint l'émetteur {issuer.name} avec succès."))
        
        if 'HX-Request' in request.headers:
            # Récupérer les émetteurs rejoints et disponibles mis à jour
            joined_issuers = request.user.joined_issuers.all()
            available_issuers = Issuer.objects.exclude(members=request.user).exclude(owner=request.user)
            
            # Renvoyer le template partiel avec les données mises à jour
            response = render(request, 'core/auth/partials/issuers.html', {
                'joined_issuers': joined_issuers,
                'available_issuers': available_issuers
            })
            response.status_code = 286  # Code HTMX personnalisé pour succès avec rafraîchissement
            response['HX-Trigger'] = 'refreshIssuers'  # Déclencher un événement pour rafraîchir la liste des émetteurs
            return response
            
        return redirect('core:profile')
        
    def leave_issuer(self, request, issuer_id):
        if not request.user.is_authenticated:
            if 'HX-Request' in request.headers:
                return HttpResponse(status=401)
            return redirect('core:login')
        
        issuer = get_object_or_404(Issuer, id=issuer_id)
        
        # Vérifier si l'utilisateur est membre
        if issuer.members.filter(id=request.user.id).exists():
            # Retirer l'utilisateur des membres de l'émetteur
            issuer.members.remove(request.user)
            messages.success(request, _(f"Vous avez quitté l'émetteur {issuer.name} avec succès."))
        else:
            messages.warning(request, _("Vous n'êtes pas membre de cet émetteur."))
        
        if 'HX-Request' in request.headers:
            # Récupérer les émetteurs rejoints et disponibles mis à jour
            joined_issuers = request.user.joined_issuers.all()
            available_issuers = Issuer.objects.exclude(members=request.user).exclude(owner=request.user)
            
            # Renvoyer le template partiel avec les données mises à jour
            response = render(request, 'core/auth/partials/issuers.html', {
                'joined_issuers': joined_issuers,
                'available_issuers': available_issuers
            })
            response.status_code = 286  # Code HTMX personnalisé pour succès avec rafraîchissement
            response['HX-Trigger'] = 'refreshIssuers'  # Déclencher un événement pour rafraîchir la liste des émetteurs
            return response
            
        return redirect('core:profile')
    
    def verify_email(self, request, token):
        try:
            user = User.objects.get(verification_token=token, email_verified=False)
            user.email_verified = True
            user.verification_token = ''
            user.save()
            
            if not request.user.is_authenticated:
                login(request, user)
            
            messages.success(request, _('Votre adresse email a été vérifiée avec succès.'))
        except User.DoesNotExist:
            messages.error(request, _('Le lien de vérification est invalide ou a expiré.'))
        
        return redirect('core:profile')
    
    def resend_verification(self, request):
        if not request.user.is_authenticated or request.user.email_verified:
            return HttpResponse(status=400)
        
        user = request.user
        user.send_verification_email()
        
        if 'HX-Request' in request.headers:
            messages.success(request, _('Un nouvel email de vérification a été envoyé.'))
            return TemplateResponse(
                request,
                'core/auth/profile.html',
                {'user': user, 'languages': settings.LANGUAGES}
            )
        return redirect('core:profile')


class EndorsementViewSet(BaseViewSet):
    """
    ViewSet pour gérer les endorsements selon la norme Open Badges v3.0.
    
    Permet de créer des endorsements pour des badges, des émetteurs ou des assertions.
    """
    
    def endorsement_modal(self, request):
        """
        Affiche le formulaire d'endorsement dans une modal.
        """
        badge_class = None
        issuer = None
        assertion = None
        
        # Récupérer l'élément à endorser en fonction des paramètres
        if 'badge_class_id' in request.GET:
            badge_class = get_object_or_404(BadgeClass, pk=request.GET.get('badge_class_id'))
        elif 'issuer_id' in request.GET:
            issuer = get_object_or_404(Issuer, pk=request.GET.get('issuer_id'))
        elif 'assertion_id' in request.GET:
            from .models.badge import Assertion
            assertion = get_object_or_404(Assertion, pk=request.GET.get('assertion_id'))
        else:
            return HttpResponse(status=400)
        
        # Créer le formulaire
        form = EndorsementForm(user=request.user, badge_class=badge_class, issuer=issuer, assertion=assertion)
        
        context = {
            'form': form,
            'badge_class': badge_class,
            'issuer': issuer,
            'assertion': assertion,
        }
        
        return render(request, 'core/endorsement/partials/endorsement_modal.html', context)
    
    def create_endorsement(self, request):
        """
        Traite la soumission du formulaire d'endorsement.
        """
        if not request.user.is_authenticated:
            return HttpResponse("Vous devez être connecté pour endorser.", status=401)
            
        # Vérifier que l'utilisateur est un administrateur de lieu, propriétaire d'un émetteur ou staff
        user_issuer_ids = []
        
        # Vérifier si l'utilisateur est propriétaire d'un émetteur ou staff
        if request.user.is_staff:
            user_is_issuer_admin = True
            user_issuer_ids = list(Issuer.objects.all().values_list('id', flat=True))
        else:
            # Vérifier si l'utilisateur est propriétaire d'au moins un émetteur ou administrateur de lieu
            user_issuer_ids = list(Issuer.objects.filter(owner=request.user).values_list('id', flat=True))
            user_is_issuer_admin = len(user_issuer_ids) > 0 or request.user.is_place_admin
        
        if not user_is_issuer_admin:
            return HttpResponse("Vous devez être administrateur d'un lieu ou d'un émetteur pour endorser des badges.", status=403)
        
        badge_class = None
        issuer = None
        assertion = None
        
        # Récupérer l'élément à endorser en fonction des paramètres
        if 'badge_class_id' in request.POST:
            badge_class = get_object_or_404(BadgeClass, pk=request.POST.get('badge_class_id'))
        elif 'issuer_id' in request.POST:
            issuer = get_object_or_404(Issuer, pk=request.POST.get('issuer_id'))
        elif 'assertion_id' in request.POST:
            from .models.badge import Assertion
            assertion = get_object_or_404(Assertion, pk=request.POST.get('assertion_id'))
        else:
            return HttpResponse("Aucun élément à endorser n'a été spécifié.", status=400)
        
        # Créer le formulaire
        form = EndorsementForm(
            request.POST,
            user=request.user,
            badge_class=badge_class,
            issuer=issuer,
            assertion=assertion
        )
        
        if form.is_valid():
            # Importer logging pour le débogage
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                # Enregistrer les données du formulaire pour le débogage
                logger.debug(f"Données du formulaire: {form.cleaned_data}")
                logger.debug(f"Type d'endorsement: {form.initial.get('type')}")
                logger.debug(f"Badge class: {badge_class}")
                logger.debug(f"Issuer: {issuer}")
                logger.debug(f"Assertion: {assertion}")
                
                # Sauvegarder l'endorsement
                endorsement = form.save()
                logger.debug(f"Endorsement créé avec ID: {endorsement.id}")
                
                # Message de succès
                messages.success(request, "Votre endorsement a été créé avec succès.")
                
                # Pour les requêtes HTMX, on renvoie le HTML mis à jour de la carte du badge
                if 'HX-Request' in request.headers and badge_class:
                    # Préparer les données du badge pour le template
                    badge_dict = {
                        'id': badge_class.id,
                        'name': badge_class.name,
                        'description': badge_class.description,
                        'image': badge_class.image,
                        'criteria_url': badge_class.criteria_url,
                        'version': badge_class.version,
                        'level': badge_class.level,
                        'category': badge_class.category,
                        'skills_list': badge_class.skills.split(',') if badge_class.skills else [],
                        'is_endorsed': True  # Le badge vient d'être endorsé
                    }
                    
                    # Rendre le template partiel avec le badge mis à jour
                    return render(request, 'core/badge/partials/badge_card.html', {
                        'badge': badge_dict,
                        'user_is_issuer_admin': user_is_issuer_admin,
                        'is_public': True
                    })
                
                # Pour les requêtes normales, on redirige vers la page des badges publics
                return redirect('core:public-badge-list')
                
            except Exception as e:
                logger.error(f"Erreur lors de la création de l'endorsement: {str(e)}")
                # Message d'erreur
                messages.error(request, f"Erreur: {str(e)}")
                
                # Réafficher le formulaire avec l'erreur pour les requêtes HTMX
                if 'HX-Request' in request.headers:
                    return HttpResponse(f"<div class='alert alert-danger'>Erreur: {str(e)}</div>", status=400)
                
                # Pour les requêtes normales, on redirige avec un message d'erreur
                return redirect('core:public-badge-list')
        
        # En cas d'erreur de validation du formulaire
        if 'HX-Request' in request.headers:
            errors = "<div class='alert alert-danger'>"
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors += f"<p>{field}: {error}</p>"
            errors += "</div>"
            return HttpResponse(errors, status=400)
        
        # Pour les requêtes normales, on redirige avec un message d'erreur
        messages.error(request, "Une erreur s'est produite lors de la création de l'endorsement.")
        return redirect('core:public-badge-list')
    
    def get_endorsements(self, request):
        """
        Récupère les endorsements pour un badge, un émetteur ou une assertion.
        """
        badge_class = None
        issuer = None
        assertion = None
        endorsements = []
        
        # Récupérer l'élément dont on veut voir les endorsements
        if 'badge_class_id' in request.GET:
            badge_class = get_object_or_404(BadgeClass, pk=request.GET.get('badge_class_id'))
            endorsements = Endorsement.objects.filter(badge_class=badge_class).order_by('-issued_on')
        elif 'issuer_id' in request.GET:
            issuer = get_object_or_404(Issuer, pk=request.GET.get('issuer_id'))
            endorsements = Endorsement.objects.filter(issuer=issuer).order_by('-issued_on')
        elif 'assertion_id' in request.GET:
            from .models.badge import Assertion
            assertion = get_object_or_404(Assertion, pk=request.GET.get('assertion_id'))
            endorsements = Endorsement.objects.filter(assertion=assertion).order_by('-issued_on')
        else:
            return HttpResponse(status=400)
        
        context = {
            'endorsements': endorsements,
            'badge_class': badge_class,
            'issuer': issuer,
            'assertion': assertion,
            'user': request.user,
        }
        
        return render(request, 'core/endorsement/partials/endorsements_list.html', context)
    
    def edit_endorsement_modal(self, request, endorsement_id):
        """
        Affiche le formulaire de modification d'un endorsement dans une modal.
        """
        # Vérifier que l'utilisateur est authentifié
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        
        # Récupérer l'endorsement à modifier
        endorsement = get_object_or_404(Endorsement, pk=endorsement_id)
        
        # Vérifier que l'utilisateur est bien le créateur de l'endorsement
        if endorsement.endorser != request.user:
            return HttpResponse(status=403)
        
        # Déterminer le type d'élément endorsé
        badge_class = endorsement.badge_class
        issuer = endorsement.issuer
        assertion = endorsement.assertion
        
        # Créer le formulaire avec les données existantes
        initial_data = {
            'claim_text': endorsement.claim.get('text', ''),
        }
        
        form = EndorsementForm(
            initial=initial_data,
            user=request.user,
            badge_class=badge_class,
            issuer=issuer,
            assertion=assertion
        )
        
        context = {
            'form': form,
            'badge_class': badge_class,
            'issuer': issuer,
            'assertion': assertion,
            'endorsement': endorsement,
            'is_edit': True,
        }
        
        return render(request, 'core/endorsement/partials/endorsement_modal.html', context)
    
    def update_endorsement(self, request, endorsement_id):
        """
        Traite la soumission du formulaire de modification d'un endorsement.
        """
        # Vérifier que l'utilisateur est authentifié
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        
        # Récupérer l'endorsement à modifier
        endorsement = get_object_or_404(Endorsement, pk=endorsement_id)
        
        # Vérifier que l'utilisateur est bien le créateur de l'endorsement
        if endorsement.endorser != request.user:
            return HttpResponse(status=403)
        
        # Déterminer le type d'élément endorsé
        badge_class = endorsement.badge_class
        issuer = endorsement.issuer
        assertion = endorsement.assertion
        
        # Créer le formulaire avec les données soumises
        form = EndorsementForm(
            request.POST,
            user=request.user,
            badge_class=badge_class,
            issuer=issuer,
            assertion=assertion
        )
        
        if form.is_valid():
            # Mettre à jour l'endorsement existant
            claim_text = form.cleaned_data.get('claim_text')
            endorsement.claim['text'] = claim_text
            endorsement.save()
            
            # Pour les requêtes HTMX, on renvoie un code 286 pour indiquer un rafraîchissement
            if 'HTTP_HX_REQUEST' in request.META and request.META['HTTP_HX_REQUEST'] == 'true':
                response = HttpResponse(status=286)
                response['HX-Trigger'] = 'endorsementCreated'
                messages.success(request, "Votre endorsement a été créé avec succès.")
                return response
            
            # Pour les requêtes normales, on redirige vers la page d'endorsement
            messages.success(request, "Votre endorsement a été créé avec succès.")
            return redirect('core:badge-endorsement-list')
        
        # En cas d'erreur, réafficher le formulaire
        context = {
            'form': form,
            'badge_class': badge_class,
            'issuer': issuer,
            'assertion': assertion,
            'endorsement': endorsement,
            'is_edit': True,
        }
        
        return render(request, 'core/endorsement/partials/endorsement_modal.html', context)
    
    def delete_endorsement(self, request, endorsement_id):
        """
        Supprime un endorsement.
        """
        # Vérifier que l'utilisateur est authentifié
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        
        # Récupérer l'endorsement à supprimer
        endorsement = get_object_or_404(Endorsement, pk=endorsement_id)
        
        # Vérifier que l'utilisateur est bien le créateur de l'endorsement
        if endorsement.endorser != request.user:
            return HttpResponse(status=403)
        
        # Déterminer le type d'élément endorsé pour pouvoir rediriger vers la bonne liste
        badge_class = endorsement.badge_class
        issuer = endorsement.issuer
        assertion = endorsement.assertion
        
        # Supprimer l'endorsement
        endorsement.delete()
        
        # Récupérer la liste mise à jour des endorsements
        if badge_class:
            endorsements = Endorsement.objects.filter(badge_class=badge_class).order_by('-issued_on')
            context = {'endorsements': endorsements, 'badge_class': badge_class, 'user': request.user}
        elif issuer:
            endorsements = Endorsement.objects.filter(issuer=issuer).order_by('-issued_on')
            context = {'endorsements': endorsements, 'issuer': issuer, 'user': request.user}
        elif assertion:
            endorsements = Endorsement.objects.filter(assertion=assertion).order_by('-issued_on')
            context = {'endorsements': endorsements, 'assertion': assertion, 'user': request.user}
        
        # Retourner la liste mise à jour des endorsements
        return render(request, 'core/endorsement/partials/endorsements_list.html', context)

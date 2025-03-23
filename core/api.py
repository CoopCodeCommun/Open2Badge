from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import BadgeClass, Assertion

class OpenBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API en lecture seule pour les Open Badges au format JSON-LD v3.0.
    
    Cette API expose les badges selon la spécification IMS Global v3.0 avec :
    * Contexte @context standard
    * Types de données XMLSchema
    * Support des collections (@set)
    * Propriétés standardisées
    """
    queryset = Assertion.objects.all()
    
    def get_json_ld_context(self):
        """Retourne le contexte JSON-LD v3.0 pour les Open Badges"""
        return {
            "@context": "https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json"
        }
        
    def get_image_url(self, image):
        """Retourne l'URL absolue d'une image"""
        if not image:
            return None
        if isinstance(image, str) and (image.startswith('http://') or image.startswith('https://')):
            return image
        try:
            return self.request.build_absolute_uri(image.url)
        except:
            return None

    def get_achievement_json_ld(self, badge_class):
        """Convertit un BadgeClass en Achievement JSON-LD"""
        achievement = {
            "type": ["Achievement"],
            "achievementType": badge_class.type,
            "name": badge_class.name,
            "description": badge_class.description,
            "criteria": badge_class.criteria_url,
            "image": self.get_image_url(badge_class.image),
            "tag": badge_class.tags.names() if hasattr(badge_class, 'tags') else [],
            "version": str(badge_class.version)
        }
        
        # Ajouter les endorsements s'il y en a
        endorsements = self.get_endorsements_json_ld(badge_class)
        if endorsements:
            achievement["endorsement"] = endorsements
            
        return achievement

    def get_profile_json_ld(self, profile):
        """Convertit un Profile ou User en JSON-LD"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if isinstance(profile, User):
            # C'est un utilisateur
            return {
                "type": ["Profile"],
                "name": profile.display_name or profile.email,
                "email": profile.email,
                "url": None,
                "image": profile.avatar_url if hasattr(profile, 'avatar_url') else None
            }
        else:
            # C'est un Profile standard (Issuer)
            return {
                "type": ["Profile"],
                "name": profile.name,
                "email": profile.email,
                "url": profile.url,
                "image": self.get_image_url(profile.image)
            }

    def get_endorsements_json_ld(self, obj):
        """Récupère les endorsements pour un badge, un émetteur ou une assertion au format JSON-LD"""
        from .models.endorsement import Endorsement
        
        endorsements = []
        
        # Déterminer le type d'objet et récupérer les endorsements correspondants
        if hasattr(obj, 'id') and hasattr(obj, 'name'):
            if hasattr(obj, 'issuer'):
                # C'est un badge (BadgeClass)
                endorsements_list = Endorsement.objects.filter(badge_class=obj).order_by('-issued_on')
            elif hasattr(obj, 'url'):
                # C'est un émetteur (Issuer)
                endorsements_list = Endorsement.objects.filter(issuer=obj).order_by('-issued_on')
            else:
                # C'est une assertion (Assertion)
                endorsements_list = Endorsement.objects.filter(assertion=obj).order_by('-issued_on')
        else:
            return []
        
        # Convertir chaque endorsement en format JSON-LD
        for endorsement in endorsements_list:
            endorsement_json = {
                "type": ["EndorsementCredential"],
                "id": endorsement.id,
                "issuanceDate": endorsement.issued_on.isoformat(),
                "issuer": self.get_profile_json_ld(endorsement.endorser),
                "credentialSubject": {
                    "type": ["EndorsementSubject"],
                    "id": obj.id,
                    "endorsementComment": endorsement.claim.get('text', '')
                }
            }
            endorsements.append(endorsement_json)
        
        return endorsements
    
    def get_assertion_json_ld(self, assertion):
        """Convertit une Assertion en OpenBadgeCredential JSON-LD"""
        badge_class = assertion.badge_class
        recipient = assertion.recipient
        
        credential = {
            "@context": self.get_json_ld_context()["@context"],
            "type": assertion.credential_type if assertion.credential_type else ["OpenBadgeCredential"],
            "id": assertion.credential_id or assertion.identifier,
            "name": f"{badge_class.name} Credential",
            "awardedDate": assertion.issued_on.isoformat(),
            
            "achievement": self.get_achievement_json_ld(badge_class),
            
            "credentialSubject": {
                "type": ["AchievementSubject"],
                "identifier": assertion.recipient_identifier,
                "achievement": self.get_achievement_json_ld(badge_class)
            }
        }
        
        if assertion.evidence_url:
            credential["evidence"] = [{
                "type": ["Evidence"],
                "id": assertion.evidence_url,
                "narrative": assertion.narrative
            }]
            
        if assertion.expires:
            credential["expirationDate"] = assertion.expires.isoformat()
        
        # Ajouter les endorsements s'il y en a
        endorsements = self.get_endorsements_json_ld(assertion)
        if endorsements:
            credential["endorsement"] = endorsements
            
        return credential

    def retrieve(self, request, pk=None):
        """
        Récupère les détails d'un badge spécifique au format JSON-LD v3.0

        Retourne un OpenBadgeCredential complet avec :
        * Achievement associé
        * Informations du destinataire
        * Preuves d'obtention
        * Dates d'émission et d'expiration
        """
        assertion = get_object_or_404(self.queryset, pk=pk)
        json_ld = self.get_assertion_json_ld(assertion)
        return Response(json_ld)

    def list(self, request):
        """
        Liste tous les badges disponibles au format JSON-LD v3.0

        Retourne une liste d'OpenBadgeCredential avec leurs Achievements associés.
        Les badges sont triés par date d'émission décroissante.
        """
        assertions = self.queryset.all()
        json_ld_list = [self.get_assertion_json_ld(assertion) for assertion in assertions]
        return Response(json_ld_list)

    @action(detail=True, methods=['get'])
    def achievement(self, request, pk=None):
        """
        Récupère uniquement l'Achievement associé à un badge au format JSON-LD v3.0

        Retourne un Achievement avec :
        * Type de réalisation
        * Critères d'obtention
        * Alignements avec standards
        * Tags et métadonnées
        """
        assertion = get_object_or_404(self.queryset, pk=pk)
        json_ld = self.get_achievement_json_ld(assertion.badge_class)
        return Response(json_ld)
        
    @action(detail=False, methods=['get'])
    def badge_with_endorsements(self, request):
        """
        Récupère un badge avec ses endorsements au format JSON-LD v3.0
        
        Paramètre de requête:
        * badge_id: ID du badge à récupérer
        
        Retourne un Achievement complet avec ses endorsements intégrés
        conformément à la spécification Open Badges v3.0
        """
        badge_id = request.query_params.get('badge_id')
        if not badge_id:
            return Response({"error": "Le paramètre badge_id est requis"}, status=400)
            
        from .models import BadgeClass
        badge = get_object_or_404(BadgeClass, pk=badge_id)
        
        json_ld = self.get_achievement_json_ld(badge)
        return Response(json_ld)

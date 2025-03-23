from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models.badge import Issuer, BadgeClass, Assertion, BadgeVersion

User = get_user_model()

class OpenBadgeAPITests(APITestCase):
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Préparer l'image de test
        with open('media/404/img_badge_404.png', 'rb') as f:
            self.test_image = SimpleUploadedFile(
                name='img_badge_404.png',
                content=f.read(),
                content_type='image/png'
            )
        
        # Créer un émetteur
        self.issuer = Issuer.objects.create(
            name='Test Issuer',
            url='https://example.com',
            email='issuer@example.com',
            description='Test Issuer Description',
            image='https://example.com/logo.png',
            version=BadgeVersion.V3.value,
            owner=self.user
        )
        
        # Créer un badge
        self.badge_class = BadgeClass.objects.create(
            name='Test Badge',
            description='Test Badge Description',
            image=self.test_image,
            criteria_url='https://example.com/criteria',
            issuer=self.issuer,
            version=BadgeVersion.V3.value,
            category='Compétence',
            skills='Python, Django, API REST'
        )
        
        # Créer une assertion
        self.assertion = Assertion.objects.create(
            recipient=self.user,
            badge_class=self.badge_class,  # Requis pour compatibilité v2
            achievement=self.badge_class,  # Utilisé pour v3
            version=BadgeVersion.V3.value,
            credential_type=['VerifiableCredential', 'OpenBadgeCredential'],
            evidence=[{
                'type': ['Evidence'],
                'id': 'https://example.com/evidence/1',
                'narrative': 'Completed all requirements'
            }]
        )

    def test_list_badges(self):
        """Test de la liste des badges"""
        url = reverse('core:badges-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Vérifier le format JSON-LD
        self.assertEqual(response.data[0]['@context'],
                        'https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json')
        self.assertIn('OpenBadgeCredential', response.data[0]['type'])

    def test_retrieve_badge(self):
        """Test de la récupération d'un badge spécifique"""
        url = reverse('core:badges-detail', args=[self.assertion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier les données du badge
        self.assertEqual(response.data['id'], self.assertion.identifier)
        self.assertEqual(response.data['achievement']['name'], 'Test Badge')
        
        # Vérifier le format JSON-LD v3.0
        self.assertIn('achievement', response.data)
        self.assertIn('credentialSubject', response.data)
        self.assertEqual(response.data['credentialSubject']['type'], ['AchievementSubject'])

    def test_retrieve_achievement(self):
        """Test de la récupération d'un achievement"""
        url = reverse('core:badges-achievement', args=[self.assertion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le format Achievement
        self.assertEqual(response.data['type'], ['Achievement'])
        self.assertEqual(response.data['name'], 'Test Badge')
        self.assertEqual(response.data['version'], self.badge_class.version)
        
    def test_badge_with_endorsements(self):
        """Test de la récupération d'un badge avec ses endorsements"""
        # Créer un endorsement pour le badge
        from core.models.endorsement import Endorsement, EndorsementType
        import uuid
        
        endorsement = Endorsement.objects.create(
            id=str(uuid.uuid4()),
            type=EndorsementType.BADGE_CLASS,
            badge_class=self.badge_class,
            endorser=self.user,
            claim={
                'text': 'Ce badge est excellent',
                'rating': 5
            }
        )
        
        # Tester l'endpoint badge_with_endorsements
        url = reverse('core:badge-with-endorsements')
        response = self.client.get(url, {'badge_id': self.badge_class.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que les endorsements sont inclus dans la réponse
        self.assertIn('endorsement', response.data)
        self.assertEqual(len(response.data['endorsement']), 1)
        self.assertEqual(response.data['endorsement'][0]['id'], endorsement.id)
        self.assertEqual(response.data['endorsement'][0]['type'], ['EndorsementCredential'])
        self.assertEqual(response.data['endorsement'][0]['credentialSubject']['type'], ['EndorsementSubject'])
        self.assertEqual(response.data['endorsement'][0]['credentialSubject']['endorsementComment'], 'Ce badge est excellent')

    def test_badge_endorsement(self):
        """Test de l'endorsement d'un badge"""
        # Créer un autre utilisateur pour l'endorsement
        endorser = User.objects.create_user(
            email='endorser@example.com',
            password='endorser123'
        )
        
        # Créer un émetteur pour l'endorsement
        endorser_issuer = Issuer.objects.create(
            name='Endorser Org',
            url='https://endorser.com',
            email='org@endorser.com',
            description='Endorser Organization',
            image='https://endorser.com/logo.png',  # L'image de l'émetteur peut rester une URL
            version=BadgeVersion.V3.value,
            owner=endorser  # Ajouter le propriétaire de l'émetteur
        )
        
        # Créer un badge d'endorsement
        endorsement_badge = BadgeClass.objects.create(
            name='Endorsement Badge',
            description='Endorsement of Test Badge',
            image=self.test_image,
            criteria_url='https://endorser.com/criteria',
            issuer=endorser_issuer,
            version=BadgeVersion.V3.value,
            category='Endorsement'
        )
        
        # Créer une assertion d'endorsement
        endorsement = Assertion.objects.create(
            recipient=self.user,
            badge_class=endorsement_badge,  # Requis pour compatibilité v2
            achievement=endorsement_badge,  # Utilisé pour v3
            version=BadgeVersion.V3.value,
            credential_type=['VerifiableCredential', 'EndorsementCredential'],
            evidence=[{
                'type': ['Evidence'],
                'id': 'https://endorser.com/evidence/1',
                'narrative': 'Endorsement of original badge'
            }]
        )
        
        # Vérifier l'endorsement via l'API
        url = reverse('core:badges-detail', args=[endorsement.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le format de l'endorsement
        self.assertEqual(response.data['type'], ['VerifiableCredential', 'EndorsementCredential'])
        self.assertEqual(response.data['achievement']['name'], 'Endorsement Badge')
        self.assertEqual(response.data['achievement']['version'], BadgeVersion.V3.value)

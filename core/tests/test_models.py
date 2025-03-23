from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from core.models.badge import Issuer, BadgeClass

User = get_user_model()

class IssuerModelTests(TestCase):
    """Tests pour le modèle Issuer"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer un utilisateur pour être le propriétaire de l'émetteur
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.issuer_data = {
            'name': 'Université Test',
            'description': 'Une université fictive pour les tests',
            'url': 'https://universite-test.edu',
            'email': 'contact@universite-test.edu',
            'version': 'v2',
            'owner': self.user
        }
    
    def test_issuer_creation(self):
        """Test de création d'un émetteur"""
        issuer = Issuer.objects.create(**self.issuer_data)
        self.assertEqual(issuer.name, self.issuer_data['name'])
        self.assertEqual(issuer.description, self.issuer_data['description'])
        self.assertEqual(issuer.url, self.issuer_data['url'])
        self.assertEqual(issuer.email, self.issuer_data['email'])
        self.assertEqual(issuer.version, self.issuer_data['version'])
        
    def test_issuer_str_method(self):
        """Test de la méthode __str__ de l'émetteur"""
        issuer = Issuer.objects.create(**self.issuer_data)
        self.assertEqual(str(issuer), self.issuer_data['name'])


class BadgeClassModelTests(TestCase):
    """Tests pour le modèle BadgeClass"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer un utilisateur pour être le propriétaire de l'émetteur
        self.user = User.objects.create_user(
            email='badge_test@example.com',
            password='testpass123'
        )
        
        # Créer un émetteur pour les tests
        self.issuer = Issuer.objects.create(
            name='Université Test',
            description='Une université fictive pour les tests',
            url='https://universite-test.edu',
            email='contact@universite-test.edu',
            version='v2',
            owner=self.user
        )
        
        # Image de test pour le badge
        self.image_content = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        self.image = SimpleUploadedFile(
            name='test_image.gif',
            content=self.image_content,
            content_type='image/gif'
        )
        
        # Données pour le badge
        self.badge_data = {
            'name': 'Badge de Test',
            'description': 'Un badge pour tester le modèle',
            'image': self.image.name,
            'criteria_url': 'https://universite-test.edu/criteres',
            'issuer': self.issuer,
            'version': 'v2',
            'category': 'Test',
            'skills': 'Python,Django,Testing'
        }
    
    def test_badge_class_creation(self):
        """Test de création d'un badge"""
        badge = BadgeClass.objects.create(**self.badge_data)
        self.assertEqual(badge.name, self.badge_data['name'])
        self.assertEqual(badge.description, self.badge_data['description'])
        self.assertEqual(badge.criteria_url, self.badge_data['criteria_url'])
        self.assertEqual(badge.issuer, self.issuer)
        self.assertEqual(badge.version, self.badge_data['version'])
        self.assertEqual(badge.category, self.badge_data['category'])
        self.assertEqual(badge.skills, self.badge_data['skills'])
    
    def test_badge_str_method(self):
        """Test de la méthode __str__ du badge"""
        badge = BadgeClass.objects.create(**self.badge_data)
        expected_str = f"{self.badge_data['name']} ({self.issuer.name})"
        self.assertEqual(str(badge), expected_str)
    
    def test_issuer_badge_relation(self):
        """Test de la relation entre émetteur et badges"""
        # Créer plusieurs badges pour le même émetteur
        badge1 = BadgeClass.objects.create(**self.badge_data)
        
        badge2_data = self.badge_data.copy()
        badge2_data['name'] = 'Badge de Test 2'
        badge2 = BadgeClass.objects.create(**badge2_data)
        
        # Vérifier que l'émetteur est correctement lié aux badges
        badges = BadgeClass.objects.filter(issuer=self.issuer)
        self.assertEqual(badges.count(), 2)
        self.assertIn(badge1, badges)
        self.assertIn(badge2, badges)

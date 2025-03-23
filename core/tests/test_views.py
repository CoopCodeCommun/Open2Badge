from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models.badge import BadgeClass, Issuer
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class BadgeViewsTests(TestCase):
    """Tests pour les vues liées aux badges"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        
        # Créer un utilisateur pour les tests
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        
        # Créer des émetteurs pour les tests
        self.issuer1 = Issuer.objects.create(
            name='Université Test 1',
            description='Une université fictive pour les tests',
            url='https://universite-test1.edu',
            email='contact@universite-test1.edu',
            version='v2',
            owner=self.user
        )
        
        self.issuer2 = Issuer.objects.create(
            name='Université Test 2',
            description='Une autre université fictive pour les tests',
            url='https://universite-test2.edu',
            email='contact@universite-test2.edu',
            version='v3',
            owner=self.user
        )
        
        # Image de test pour les badges
        self.image_content = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        self.image = SimpleUploadedFile(
            name='test_image.gif',
            content=self.image_content,
            content_type='image/gif'
        )
        
        # Créer des badges pour les tests
        self.badge1 = BadgeClass.objects.create(
            name='Badge Python',
            description='Badge de compétence en Python',
            image=self.image.name,
            criteria_url='https://universite-test1.edu/criteres/python',
            issuer=self.issuer1,
            version='v2',
            category='Programmation',
            skills='Python,Programmation,Algorithmique'
        )
        
        self.badge2 = BadgeClass.objects.create(
            name='Badge Django',
            description='Badge de compétence en Django',
            image=self.image.name,
            criteria_url='https://universite-test1.edu/criteres/django',
            issuer=self.issuer1,
            version='v2',
            category='Web',
            skills='Django,Python,Web'
        )
        
        self.badge3 = BadgeClass.objects.create(
            name='Badge HTMX',
            description='Badge de compétence en HTMX',
            image=self.image.name,
            criteria_url='https://universite-test2.edu/criteres/htmx',
            issuer=self.issuer2,
            version='v3',
            category='Web',
            skills='HTMX,JavaScript,Web'
        )
    
    def test_public_badge_list(self):
        """Test de la vue publique des badges"""
        url = reverse('core:public-badge-list')
        response = self.client.get(url)
        
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le template correct est utilisé
        self.assertTemplateUsed(response, 'core/badge/public_list.html')
        
        # Vérifier que les émetteurs et leurs badges sont dans le contexte
        self.assertIn('issuers_badges', response.context)
        self.assertEqual(len(response.context['issuers_badges']), 2)  # 2 émetteurs
        
        # Vérifier que is_public est True
        self.assertTrue(response.context['is_public'])
        
        # Vérifier que le contenu HTML contient les noms des émetteurs et des badges
        self.assertContains(response, self.issuer1.name)
        self.assertContains(response, self.issuer2.name)
        self.assertContains(response, self.badge1.name)
        self.assertContains(response, self.badge2.name)
        self.assertContains(response, self.badge3.name)
    
    def test_my_issuers_badges_unauthenticated(self):
        """Test de la vue des badges de mes émetteurs sans authentification"""
        url = reverse('core:my-issuers-badges')
        response = self.client.get(url)
        
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        # Vérifier que le message d'avertissement est ajouté
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("connecté" in str(msg) for msg in messages))
    
    def test_my_issuers_badges(self):
        """Test de la vue des badges de mes émetteurs avec authentification"""
        # Connecter l'utilisateur
        self.client.login(email='testuser@example.com', password='testpassword123')
        
        url = reverse('core:my-issuers-badges')
        response = self.client.get(url)
        
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le template correct est utilisé
        self.assertTemplateUsed(response, 'core/badge/public_list.html')
        
        # Vérifier que les émetteurs et leurs badges sont dans le contexte
        self.assertIn('issuers_badges', response.context)
        
        # Vérifier que is_public est False
        self.assertFalse(response.context['is_public'])
        
        # Vérifier que le titre est correct
        self.assertEqual(response.context['title'], 'Mes badges à émettre')
        
        # Vérifier que le contenu HTML contient les noms des émetteurs et des badges
        self.assertContains(response, self.issuer1.name)
        self.assertContains(response, self.issuer2.name)
        self.assertContains(response, self.badge1.name)
        self.assertContains(response, self.badge2.name)
        self.assertContains(response, self.badge3.name)
        
        # Vérifier que le bouton "Nouveau badge" est présent
        self.assertContains(response, 'Nouveau badge')

class BadgeFormTests(TestCase):
    """Tests pour les formulaires de badges"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        
        # Créer un utilisateur pour les tests
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
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
        with open('media/404/img_badge_404.png', 'rb') as f:
            self.image = SimpleUploadedFile(
                name='img_badge_404.png',
                content=f.read(),
                content_type='image/png'
            )
    
    def test_badge_creation_modal(self):
        """Test de l'affichage du modal de création de badge"""
        # Connecter l'utilisateur
        self.client.login(email='testuser@example.com', password='testpassword123')
        
        url = reverse('core:badge-create-modal')
        response = self.client.get(url)
        
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le template correct est utilisé
        self.assertTemplateUsed(response, 'core/badge/partials/badge_form.html')
        
        # Vérifier que le formulaire est dans le contexte
        self.assertIn('form', response.context)
        form = response.context['form']
        
        # Vérifier que tous les champs nécessaires du formulaire sont présents
        expected_fields = ['name', 'description', 'image', 'criteria_url', 'issuer', 'category', 'skills', 'level', 'version']
        for field in expected_fields:
            self.assertIn(field, form.fields)
        
        # Vérifier que les champs du formulaire sont rendus correctement dans le HTML
        for field in expected_fields:
            self.assertContains(response, f'id="id_{field}"')
        
        # Vérifier que les champs obligatoires sont marqués comme tels
        self.assertContains(response, '<span class="text-danger">*</span>')
        
        # Vérifier que le formulaire contient les attributs HTMX nécessaires
        self.assertContains(response, 'hx-post')
        self.assertContains(response, 'hx-encoding="multipart/form-data"')
        
        # Vérifier que le bouton de soumission est présent
        self.assertContains(response, 'type="submit"')
    
    def test_badge_creation(self):
        """Test de la création d'un badge"""
        # Connecter l'utilisateur
        self.client.login(email='testuser@example.com', password='testpassword123')
        
        # Utiliser l'image créée dans setUp
        image = self.image
        
        # Données pour la création du badge
        badge_data = {
            'name': 'Nouveau Badge',
            'description': 'Description du nouveau badge',
            'image': self.image,
            'criteria_url': 'https://universite-test.edu/criteres/nouveau',
            'issuer': self.issuer.id,
            'category': 'Test',
            'skills': 'Test,Nouveau,Badge',
            'level': 'Débutant',
            'version': 'v3'
        }
        
        # Nombre de badges avant la création
        badges_count_before = BadgeClass.objects.count()
        
        url = reverse('core:badge-create')
        response = self.client.post(url, badge_data, format='multipart', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print(response.content)
        # Afficher les erreurs de formulaire si la réponse est 200
        if response.status_code == 200 and hasattr(response, 'context') and response.context and 'form' in response.context:
            form = response.context['form']
            if form.errors:
                print(f"Erreurs de formulaire: {form.errors}")
        
        # Vérifier qu'un nouveau badge a été créé
        self.assertEqual(BadgeClass.objects.count(), badges_count_before + 1, "Le badge n'a pas été créé")
        
        # Vérifier que le badge a été créé avec les bonnes données
        new_badge = BadgeClass.objects.latest('id')
        self.assertEqual(new_badge.name, badge_data['name'])
        self.assertEqual(new_badge.description, badge_data['description'])
        self.assertEqual(new_badge.criteria_url, badge_data['criteria_url'])
        self.assertEqual(new_badge.issuer, self.issuer)
        self.assertEqual(new_badge.version, 'v3')
        self.assertEqual(new_badge.category, badge_data['category'])
        self.assertEqual(new_badge.skills, badge_data['skills'])
    
    def test_badge_creation_with_form(self):
        """Test de la création d'un badge depuis le formulaire avec une image de test"""
        # Connecter l'utilisateur
        self.client.login(email='testuser@example.com', password='testpassword123')
        
        # Ouvrir l'image de test depuis le dossier /media/404/
        with open('media/404/img_badge_404.png', 'rb') as f:
            test_image = SimpleUploadedFile(
                name='test_badge_image.png',
                content=f.read(),
                content_type='image/png'
            )
        
        # Données pour la création du badge via le formulaire
        badge_data = {
            'name': 'Badge FALC',
            'description': 'Un badge facile à lire et à comprendre',
            'image': test_image,
            'criteria_url': 'https://example.com/criteres-falc',
            'issuer': self.issuer.id,
            'category': 'Accessibilité',
            'skills': 'FALC,Accessibilité,Inclusion',
            'level': 'Intermédiaire',
            'version': 'v2'
        }
        
        # Nombre de badges avant la création
        badges_count_before = BadgeClass.objects.count()
        
        # Appeler la vue de création de badge
        url = reverse('core:badge-create')
        response = self.client.post(url, badge_data, format='multipart')
        
        # Afficher les erreurs de formulaire en cas d'échec
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            form = response.context['form']
            if form.errors:
                print(f"Erreurs de formulaire: {form.errors}")
        
        # Vérifier qu'un nouveau badge a été créé
        self.assertEqual(BadgeClass.objects.count(), badges_count_before + 1, "Le badge n'a pas été créé")
        
        # Récupérer le badge créé
        new_badge = BadgeClass.objects.latest('id')
        
        # Vérifier les données du badge
        self.assertEqual(new_badge.name, badge_data['name'])
        self.assertEqual(new_badge.description, badge_data['description'])
        self.assertEqual(new_badge.criteria_url, badge_data['criteria_url'])
        self.assertEqual(new_badge.issuer.id, badge_data['issuer'])
        self.assertEqual(new_badge.category, badge_data['category'])
        self.assertEqual(new_badge.skills, badge_data['skills'])
        self.assertEqual(new_badge.level, badge_data['level'])
        self.assertEqual(new_badge.version, badge_data['version'])
        
        # Vérifier que l'image a été enregistrée
        self.assertTrue(new_badge.image)
        self.assertIsNotNone(new_badge.image.name)


class IssuerViewsTests(TestCase):
    """Tests pour les vues liées aux émetteurs"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        
        # Créer un utilisateur pour les tests
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        
        # Créer un émetteur pour les tests
        self.issuer = Issuer.objects.create(
            name='Université Test',
            description='Une université fictive pour les tests',
            url='https://universite-test.edu',
            email='contact@universite-test.edu',
            owner=self.user,
            version='v2'
        )
    
    def test_issuer_list(self):
        """Test de la vue de liste des émetteurs"""
        url = reverse('core:issuer-list')
        response = self.client.get(url)
        
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le template correct est utilisé
        self.assertTemplateUsed(response, 'core/issuer/list.html')
        
        # Vérifier que les émetteurs sont dans le contexte
        self.assertIn('issuers', response.context)
        
        # Vérifier que le contenu HTML contient le nom de l'émetteur
        self.assertContains(response, self.issuer.name)
        
        # Vérifier que le bouton pour créer un nouvel émetteur est présent
        self.assertContains(response, 'Nouvel émetteur')
    
    def test_issuer_creation_modal(self):
        """Test de l'affichage du modal de création d'émetteur"""
        url = reverse('core:issuer-create-modal')
        response = self.client.get(url)
        
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le template correct est utilisé
        self.assertTemplateUsed(response, 'core/issuer/modal/create_issuer_modal.html')
        
        # Vérifier que le formulaire est dans le contexte
        self.assertIn('form', response.context)
        form = response.context['form']
        
        # Vérifier que tous les champs du modèle sont présents dans le formulaire
        expected_fields = ['name', 'url', 'email', 'description', 'image', 'public_key', 
                          'key_type', 'privacy_policy', 'verification', 'revocation_list']
        for field in expected_fields:
            self.assertIn(field, form.fields)
        
        # Vérifier que les champs du formulaire sont rendus correctement dans le HTML
        self.assertContains(response, 'id="id_name"')
        self.assertContains(response, 'id="id_url"')
        self.assertContains(response, 'id="id_email"')
        self.assertContains(response, 'id="id_description"')
        self.assertContains(response, 'id="id_image"')
        self.assertContains(response, 'id="id_public_key"')
        self.assertContains(response, 'id="id_key_type"')
        self.assertContains(response, 'id="id_privacy_policy"')
        self.assertContains(response, 'id="id_verification"')
        self.assertContains(response, 'id="id_revocation_list"')
        
        # Vérifier que les champs obligatoires sont marqués comme tels
        self.assertContains(response, '<span class="text-danger">*</span>')
        
        # Vérifier que les icônes Bootstrap sont présentes
        self.assertContains(response, 'class="bi bi-building')
        self.assertContains(response, 'class="bi bi-globe')
        self.assertContains(response, 'class="bi bi-envelope')
        self.assertContains(response, 'class="bi bi-image')
        
        # Vérifier que la section des paramètres avancés est présente
        self.assertContains(response, 'id="advancedFields"')
        self.assertContains(response, 'Paramètres avancés')
        
        # Vérifier que le bouton de soumission est présent avec la bonne icône
        self.assertContains(response, '<i class="bi bi-plus-circle me-1"></i>Créer cet émetteur')
    
    def test_issuer_creation(self):
        """Test de la création d'un émetteur"""
        # Connecter l'utilisateur
        self.client.login(email='testuser@example.com', password='testpassword123')
        
        # Données pour la création de l'émetteur
        issuer_data = {
            'name': 'Nouvel Émetteur',
            'description': 'Description du nouvel émetteur',
            'url': 'https://nouvel-emetteur.edu',
            'email': 'contact@nouvel-emetteur.edu',
            'image': 'https://nouvel-emetteur.edu/logo.png',
            'version': 'v2',
            'key_type': 'rsa',  # Utiliser la valeur en minuscules comme défini dans l'énumération KeyType
            'privacy_policy': 'https://nouvel-emetteur.edu/privacy'
        }
        
        # Nombre d'émetteurs avant la création
        issuers_count_before = Issuer.objects.count()
        
        url = reverse('core:issuer-create')
        response = self.client.post(url, issuer_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Afficher les erreurs de formulaire si la réponse est 422 ou 200
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            form = response.context['form']
            if form.errors:
                print(f"Erreurs de formulaire: {form.errors}")
        
        # Vérifier qu'un nouvel émetteur a été créé
        self.assertEqual(Issuer.objects.count(), issuers_count_before + 1, "L'émetteur n'a pas été créé")
        
        # Vérifier que l'émetteur a été créé avec les bonnes données
        new_issuer = Issuer.objects.latest('created_at')
        self.assertEqual(new_issuer.name, issuer_data['name'])
        self.assertEqual(new_issuer.description, issuer_data['description'])
        self.assertEqual(new_issuer.url, issuer_data['url'])
        self.assertEqual(new_issuer.email, issuer_data['email'])
        self.assertEqual(new_issuer.version, issuer_data['version'])


class UserProfileTests(TestCase):
    """Tests pour les fonctionnalités de profil utilisateur et d'adhésion aux émetteurs"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        
        # Créer deux utilisateurs pour les tests
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='password123',
            display_name='Utilisateur Test 1',
            bio='Bio de test',
            website='https://user1.example.com',
            avatar_url='https://example.com/avatar1.png',
            email_verified=True
        )
        
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='password123',
            display_name='Utilisateur Test 2'
        )
        
        # Créer des émetteurs pour les tests
        self.issuer1 = Issuer.objects.create(
            name='Émetteur Test 1',
            description='Un émetteur fictif pour les tests',
            url='https://emetteur1.example.com',
            email='contact@emetteur1.example.com',
            owner=self.user1,
            version='v2'
        )
        
        self.issuer2 = Issuer.objects.create(
            name='Émetteur Test 2',
            description='Un autre émetteur fictif pour les tests',
            url='https://emetteur2.example.com',
            email='contact@emetteur2.example.com',
            owner=self.user2,
            version='v2'
        )
        
        self.issuer3 = Issuer.objects.create(
            name='Émetteur Test 3',
            description='Un troisième émetteur fictif pour les tests',
            url='https://emetteur3.example.com',
            email='contact@emetteur3.example.com',
            owner=self.user2,
            version='v2'
        )
        
        # Ajouter l'utilisateur 1 comme membre de l'émetteur 2
        self.issuer2.members.add(self.user1)
    
    def test_profile_page_unauthenticated(self):
        """Test d'accès à la page de profil sans authentification"""
        url = reverse('core:profile')
        response = self.client.get(url)
        
        # Vérifier que la réponse est une redirection vers la page de connexion
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:login'))
    
    def test_profile_page_authenticated(self):
        """Test d'accès à la page de profil avec authentification"""
        # Connecter l'utilisateur
        self.client.login(email='user1@example.com', password='password123')
        
        url = reverse('core:profile')
        response = self.client.get(url)
        
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le template correct est utilisé
        self.assertTemplateUsed(response, 'core/auth/profile.html')
        
        # Vérifier que les informations de l'utilisateur sont présentes
        self.assertContains(response, self.user1.display_name)
        self.assertContains(response, self.user1.bio)
        self.assertContains(response, self.user1.website)
        
        # Vérifier que les émetteurs rejoints sont présents
        self.assertContains(response, self.issuer2.name)
        
        # Vérifier que les émetteurs disponibles sont présents
        self.assertContains(response, self.issuer3.name)
        
        # Vérifier que l'émetteur dont l'utilisateur est propriétaire n'est pas dans les émetteurs disponibles
        self.assertNotContains(response, 'Rejoindre" value="' + str(self.issuer1.id))
    
    def test_join_issuer(self):
        """Test de la fonctionnalité pour rejoindre un émetteur"""
        # Connecter l'utilisateur
        self.client.login(email='user1@example.com', password='password123')
        
        # Vérifier que l'utilisateur n'est pas déjà membre de l'émetteur 3
        self.assertFalse(self.issuer3.members.filter(id=self.user1.id).exists())
        
        # Rejoindre l'émetteur 3
        url = reverse('core:join-issuer', args=[self.issuer3.id])
        headers = {'HTTP_HX-Request': 'true'}
        response = self.client.post(url, {}, **headers)
        
        # Vérifier que la réponse est 286 (code HTMX pour rafraîchissement)
        self.assertEqual(response.status_code, 286)
        
        # Vérifier que l'utilisateur est maintenant membre de l'émetteur 3
        self.assertTrue(self.issuer3.members.filter(id=self.user1.id).exists())
        
        # Vérifier que le header HX-Trigger est présent pour rafraîchir la liste des émetteurs
        self.assertEqual(response.headers['HX-Trigger'], 'refreshIssuers')
    
    def test_leave_issuer(self):
        """Test de la fonctionnalité pour quitter un émetteur"""
        # Connecter l'utilisateur
        self.client.login(email='user1@example.com', password='password123')
        
        # Vérifier que l'utilisateur est membre de l'émetteur 2
        self.assertTrue(self.issuer2.members.filter(id=self.user1.id).exists())
        
        # Quitter l'émetteur 2
        url = reverse('core:leave-issuer', args=[self.issuer2.id])
        headers = {'HTTP_HX-Request': 'true'}
        response = self.client.post(url, {}, **headers)
        
        # Vérifier que la réponse est 286 (code HTMX pour rafraîchissement)
        self.assertEqual(response.status_code, 286)
        
        # Vérifier que l'utilisateur n'est plus membre de l'émetteur 2
        self.assertFalse(self.issuer2.members.filter(id=self.user1.id).exists())
        
        # Vérifier que le header HX-Trigger est présent pour rafraîchir la liste des émetteurs
        self.assertEqual(response.headers['HX-Trigger'], 'refreshIssuers')
    
    def test_update_profile(self):
        """Test de la mise à jour du profil utilisateur"""
        # Connecter l'utilisateur
        self.client.login(email='user1@example.com', password='password123')
        
        # Données pour la mise à jour du profil
        profile_data = {
            'display_name': 'Nouveau Nom',
            'bio': 'Nouvelle biographie',
            'website': 'https://nouveau-site.com',
            'avatar_url': 'https://example.com/nouveau-avatar.png',
            'language': 'en',
            'email_notifications': 'on'
        }
        
        # Mettre à jour le profil
        url = reverse('core:profile')
        headers = {'HTTP_HX-Request': 'true'}
        response = self.client.post(url, profile_data, **headers)
        
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Rafraîchir l'utilisateur depuis la base de données
        self.user1.refresh_from_db()
        
        # Vérifier que les données ont été mises à jour
        self.assertEqual(self.user1.display_name, profile_data['display_name'])
        self.assertEqual(self.user1.bio, profile_data['bio'])
        self.assertEqual(self.user1.website, profile_data['website'])
        self.assertEqual(self.user1.avatar_url, profile_data['avatar_url'])
        self.assertEqual(self.user1.language, profile_data['language'])
        self.assertTrue(self.user1.email_notifications)

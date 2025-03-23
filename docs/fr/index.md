# Documentation Librobadge

Bienvenue dans la documentation de Librobadge, une application de gestion des OpenBadges compatible avec les versions 2.0 et 3.0 de la spécification.

## Introduction

Librobadge est une application open-source qui permet de gérer les badges numériques selon le standard Open Badge. Elle permet la création, la gestion et la délivrance de badges numériques qui sont vérifiables, portables et contiennent des informations détaillées sur les compétences et les réalisations.

## Fonctionnalités implémentées

### Gestion des émetteurs (Issuers)

Librobadge permet de gérer des organisations émettrices de badges avec les fonctionnalités suivantes :

- Création et configuration d'organisations émettrices
- Gestion des profils d'émetteurs (logo, description, site web, politique de confidentialité)
- Support des clés cryptographiques pour signer les badges (conformité avec Verifiable Credentials)
- Compatibilité avec les versions 2.0 et 3.0 d'OpenBadge

### Création et gestion des badges

- Création de classes de badges avec définition des critères d'obtention
- Support des badges v2 (BadgeClass) et v3 (Achievement)
- Gestion des compétences associées à chaque badge
- Catégorisation et niveaux de badges
- Association avec des émetteurs

### Affichage des badges

- Vue publique pour afficher tous les badges groupés par émetteur
- Vue pour les badges des émetteurs de l'utilisateur connecté
- Interface responsive avec Bootstrap pour une expérience utilisateur optimale
- Formatage des compétences dans la vue pour un affichage clair

### Alignement avec des référentiels

- Association des badges avec des référentiels de compétences externes
- Définition des frameworks, codes et descriptions pour chaque alignement
- Liens vers les référentiels (URLs)

### Assertions de badges

- Création d'assertions pour attribuer des badges à des utilisateurs
- Gestion du cycle de vie des badges (émission, expiration, révocation)
- Support des assertions v2 et v3
- Stockage des preuves d'obtention

### Intégration HTMX

- Utilisation de HTMX pour les interactions dynamiques sans rechargement de page
- Optimisation du rendu partiel pour améliorer les performances
- Gestion des modales pour la création et l'édition de badges

### Sécurité et contrôle d'accès

- Protection des vues nécessitant une authentification
- Redirection des utilisateurs non connectés avec messages d'avertissement
- Validation des données de formulaire côté serveur
- Authentification par email (sans mot de passe)

## Architecture technique

Librobadge est développé avec :

### Backend
- Django et Django Rest Framework
- Viewset comme vues de base
- Base de données SQLite
- Poetry pour la gestion des dépendances
- django-solo, django-allauth, django-tenant
- Cryptographie avec Fernet

### Frontend
- Templates Django
- Bootstrap 5 avec Material Design
- HTMX pour l'interactivité
- Hyperscript pour la logique côté client

### Design
- Interface responsive
- FALC (Facile à lire et à comprendre)
- Rendu partiel optimisé HTMX
- Approche "Less JavaScript"

## Modèles principaux

### Émetteur (Issuer)

Un émetteur représente une organisation qui crée et délivre des badges. Il est compatible avec les profils v2 et v3 de la spécification OpenBadge.

Attributs principaux :
- Nom, URL, email, description
- Logo (image)
- Clé publique et type de clé pour la signature cryptographique
- Politique de confidentialité
- Méthode de vérification

### Classe de badge (BadgeClass)

Une classe de badge définit un type spécifique de badge qui peut être attribué. Elle est compatible avec les achievements v3 de la spécification.

Attributs principaux :
- Nom, description, image
- Critères d'obtention
- Émetteur associé
- Catégorie et niveau
- Compétences validées

### Assertion (Assertion)

Une assertion représente l'attribution d'un badge à un utilisateur spécifique.

Attributs principaux :
- Badge ou achievement attribué
- Destinataire
- Date d'émission et d'expiration
- Preuves d'obtention
- Statut de révocation

### Alignement (Alignment)

Un alignement associe un badge à un référentiel de compétences externe.

Attributs principaux :
- Badge associé
- Nom et URL du référentiel
- Description et framework
- Code de la compétence

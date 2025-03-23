# Cahier des charges

Nom : Librobadge

Application de gestion des OpenBadge 
Spécification de la V3 : https://www.imsglobal.org/spec/ob/v3p0/impl/

Doit être compatible avec les OpenBadge v2 et v3

## Présentation 

Définition de imsglobal (en) :
Open Badges is the world's leading format for digital badges. Open Badges is not a specific product or platform, but a type of digital badge that is verifiable, portable, and packed with information about skills and achievements.

Open Badges can be issued, earned, and managed by using a certified Open Badges platform.

Want to build new technologies to issue, display, or host Open Badges? The Open Badges standard is a free and open specification available for adoption.

## Exemple concret :

Imagine un badge numérique Open Badge v3.0 :

    L'université signe le badge avec sa clé privée.
    L'étudiant peut l'ajouter dans un portefeuille numérique.
    Un employeur peut vérifier facilement (sans contacter l'université) que le badge est authentique et valide.

## Pourquoi c'est important ?

Parce que ça décentralise la confiance : au lieu de dépendre d'une base de données centrale, tout est contenu dans l'identifiant et vérifiable de façon indépendante, souvent compatible avec les standards du Web décentralisé.

## Fonctionnalités

1. Gestion des Émetteurs (Issuers)

    Interface pour créer, configurer et vérifier des organisations émettrices.
    Gestion des profils d'émetteurs : logo, description, site web, politique de confidentialité.
    Gestion des clés cryptographiques pour signer les badges (conformité Verifiable Credentials).


2. Création et Gestion des Badges

    Outil pour concevoir graphiquement des badges (choisir icônes, couleurs, texte...).
    Définition des critères d'obtention : compétences, durée, évaluation nécessaire, etc.
    Alignement avec des frameworks de compétences (ex. ESCO, frameworks métiers).
    Support de plusieurs formats : Open Badge v3.0, Verifiable Credentials JSON-LD.

3. Attribution et Délivrance des Badges

    Attribution manuelle ou automatisée à des utilisateurs ou groupes (via API ou intégrations LMS : Moodle, Canvas...).
    Envoi des badges par email, QR code ou intégration dans un portefeuille numérique.
    Support des conditions de délivrance (validation d'un parcours, paiement, évaluation...).

4. Vérification des Badges

    Outil public ou API pour vérifier l'authenticité et la validité d’un badge (signature cryptographique).
    Support des standards Verifiable Credentials pour vérification décentralisée.

5. Portefeuille Utilisateur (Wallet)

    Espace personnel pour les apprenants où ils peuvent :
        Consulter, télécharger ou partager leurs badges.
        Connecter leur portefeuille à des services externes (LinkedIn, CV en ligne, Europass, etc.).
        Gérer la confidentialité et visibilité de leurs badges.

6. Interopérabilité & API

    API REST complète pour intégration avec :
        LMS (Moodle, Sakai…)
        CRM, ERP
        Systèmes RH (pour entreprises)
    Support des standards comme OpenID Connect ou LTI pour faciliter les intégrations.

7. Analytics & Reporting

    Tableau de bord pour :
        Voir le nombre de badges délivrés.
        Analyser la distribution (par compétence, par public, etc.).
        Exporter des rapports (CSV, JSON).

8. Gestion des utilisateurs & rôles

    Admin, émetteur, évaluateur, utilisateur final.
    Option d'authentification fédérée : SSO (SAML, OIDC), LDAP, Keycloak, etc.

9. Conformité & Confidentialité

    Respect du RGPD (anonymisation, consentement utilisateur, suppression de données).
    Transparence sur les données stockées.
    Support du Selective Disclosure pour partager uniquement certaines informations.


## Stack technique :

### Back 
Poetry
Django, Django Rest Framework
Viewset base view.
Base de donnée sqlite
django-solo
django-allauth
django-tenant
cryptography & fernet key

### Front 

- Template Django
- Bootstrap 5
- Material design
- HTMX
- Hyperscript

### Administration

implémenter Unfold : https://unfoldadmin.com/

### Design 
- Logiciel libre sous licence AGPLv3
- Model bien nommé pour du sémentique façon shema.org
- Responsive
- FALC (Facile a lire et à comprendre)
- Test Drived Development
- Htmx partials rendering view :
https://django-htmx.readthedocs.io/en/latest/tips.html

- Le moins possible de javascript. On code en philosophie hyperscript et hypermedia.

- Le plus important : que le code soit lisible par tous et toutes facilement. Beaucoup de commentaires et peu de fonctions complexes.

- On cherche à construire un commun numérique facile a lire et a comprendre. Chaque étape est bien explicite et fera l'objet d'une note de blog pour décrire les choix techniques et les raisons des décisions.

- Un modèle user sans mot de passe. Un email est utilisé pour identifier l'utilisateur. Il se connecte en validant son email avec un token de connexion de type signature django.

- Penser à brancher un SSO


## Compatibilité OpenBadge v2 et v3

Librobadge peut utiliser les badges version 2 et version 3.

Voici comment ça marche :

1. Les badges version 2 :
   - Continuent de fonctionner normalement
   - Peuvent être créés comme avant
   - Sont toujours valides

2. Les badges version 3 :
   - Ont de nouvelles fonctions
   - Utilisent des signatures numériques
   - Sont plus sécurisés

3. Passage de version 2 à version 3 :
   - On garde le badge version 2
   - On crée un nouveau badge version 3
   - Les deux badges restent valides
   - Le badge version 3 a plus de fonctions

C'est comme avoir deux formats de photo :
- La version 2 est comme une photo JPEG simple
- La version 3 est comme une photo JPEG avec des informations supplémentaires

Vous pouvez utiliser les deux versions selon vos besoins.

## Test unitaires importants :

- Export et Import de badge V2 et V3
# Documentation Technique de Librobadge

Cette page présente les aspects techniques de Librobadge, notamment l'architecture, les modèles de données et les processus d'implémentation.

## Architecture du système

Librobadge est construit sur une architecture Django MVT (Modèle-Vue-Template) avec une intégration de Django Rest Framework pour l'API.

```
├── core/                  # Application principale
│   ├── models/            # Modèles de données
│   │   ├── badge.py       # Modèles pour les badges et émetteurs
│   │   └── user.py        # Modèle utilisateur
│   ├── views.py           # Vues et viewsets
│   ├── urls.py            # Configuration des URLs
│   ├── templatetags/      # Tags et filtres personnalisés
│   └── tests/             # Tests unitaires et d'intégration
├── templates/             # Templates HTML
│   └── core/              # Templates spécifiques à l'application
│       ├── issuer/        # Templates pour les émetteurs
│       └── badge/         # Templates pour les badges
└── docs/                  # Documentation
    ├── fr/                # Documentation en français
    └── en/                # Documentation en anglais
```

## Modèles de données

### Diagramme de relation

Les modèles principaux et leurs relations :

```
Issuer (1) ---> (*) BadgeClass (1) ---> (*) Assertion (1) ---> (1) User
                     |
                     v
                 (*) Alignment
```

### Modèle Issuer

Le modèle `Issuer` représente une organisation qui émet des badges. Il peut être utilisé pour les versions 2 et 3 d'OpenBadge.

Attributs principaux :
- `version` : Version du standard OpenBadge (v2 ou v3)
- `name` : Nom de l'organisation
- `url` : Site web de l'organisation
- `email` : Email de contact
- `description` : Description de l'organisation
- `image` : Logo de l'organisation (URL)
- `public_key` : Clé publique pour la vérification des badges signés
- `key_type` : Type d'algorithme de signature (RSA, ED25519, SECP256K1)
- `verification` : Méthodes de vérification des badges (JSON)

### Modèle BadgeClass

Le modèle `BadgeClass` définit une classe de badge qui peut être attribuée. Pour OpenBadge v3, il correspond à un Achievement.

Attributs principaux :
- `version` : Version du standard OpenBadge (v2 ou v3)
- `name` : Nom du badge
- `type` : Type d'achievement (Badge, Certificate, Diploma)
- `description` : Description détaillée du badge
- `image` : Image représentative du badge
- `criteria_url` : URL des critères d'obtention
- `issuer` : Organisation émettrice (ForeignKey)
- `category` : Catégorie du badge
- `skills` : Compétences validées par le badge
- `level` : Niveau de difficulté ou de maîtrise

### Modèle Assertion

Le modèle `Assertion` représente l'attribution d'un badge à un utilisateur spécifique.

Attributs principaux :
- `version` : Version du standard OpenBadge (v2 ou v3)
- `badge_class` : Badge attribué (ForeignKey pour v2)
- `achievement` : Achievement attribué (ForeignKey pour v3)
- `recipient_identifier` : Identifiant du destinataire (email haché ou DID)
- `recipient_type` : Type d'identifiant (email, url, telephone, did)
- `recipient_hashed` : Indique si l'identifiant est haché
- `issuance_date` : Date d'émission
- `evidence` : Preuves de l'obtention (JSON)
- `expires_at` : Date d'expiration (optionnel)
- `revoked` : Indique si le badge a été révoqué
- `revocation_reason` : Raison de la révocation
- `verification_type` : Type de vérification (hosted, signed)
- `verification` : Données de vérification (JSON)

### Modèle Alignment

Le modèle `Alignment` représente l'alignement d'un badge avec un référentiel de compétences externe.

Attributs principaux :
- `badge_class` : Badge aligné (ForeignKey)
- `target_name` : Nom du référentiel
- `target_url` : URL du référentiel
- `target_description` : Description du référentiel
- `target_framework` : Nom du framework de compétences
- `target_code` : Code de la compétence dans le référentiel

## Gestion des versions OpenBadge

Librobadge gère à la fois les badges v2 et v3 grâce à une architecture flexible :

1. Chaque modèle (Issuer, BadgeClass, Assertion) a un champ `version`
2. Version par défaut : v2 pour assurer la compatibilité
3. Champs spécifiques à la v3 sont nullables pour les objets v2
4. Assertions v3 utilisent `achievement` au lieu de `badge_class`

Pour le passage de v2 à v3 :
- Une assertion v2 existante est conservée
- Une nouvelle assertion v3 est créée
- Les champs communs sont automatiquement mappés
- Les champs spécifiques à la v3 sont générés

## Interfaces utilisateur

### Vues principales

- `PublicIssuerListView` : Affichage public des émetteurs
- `IssuerViewSet` : Gestion des émetteurs
- `BadgeClassViewSet` : Gestion des badges
  - `public_list` : Badges groupés par émetteur (public)
  - `my_issuers_badges` : Badges des émetteurs de l'utilisateur connecté

### Intégration HTMX

L'application utilise HTMX pour les interactions dynamiques :

1. Rendu partiel optimisé :
   - Vues séparées pour l'affichage et le traitement
   - Templates partiels pour les listes d'émetteurs et de badges
   - Utilisation du code 286 pour indiquer un rafraîchissement

2. Exemples d'optimisation :
   - `hx-swap="none"` pour les actions déclenchant un rafraîchissement complet
   - `hx-swap="outerHTML"` pour les mises à jour partielles
   - Trigger HX-Trigger pour déclencher des événements sans rechargement

## Tests

Les tests sont organisés par fonctionnalité :

1. Tests unitaires :
   - Filtres de template personnalisés
   - Création et validation des modèles
   - Relations entre modèles

2. Tests d'intégration :
   - Vues publiques et protégées
   - Création et édition de badges
   - Format JSON-LD de l'API

Tous les tests sont exécutés avec pytest et sont documentés dans le fichier TEST.md.

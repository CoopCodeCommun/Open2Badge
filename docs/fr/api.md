# Documentation API OpenBadge

Cette page décrit l'API RESTful de Librobadge qui permet d'interagir programmatiquement avec la plateforme.

## Spécification OpenBadge

L'API de Librobadge implémente la spécification JSON-LD Open Badges v3.0 tout en maintenant la compatibilité avec la version 2.0.

### Formats de réponse

Toutes les réponses de l'API sont au format JSON-LD (JavaScript Object Notation for Linked Data), qui est une méthode d'encodage des données liées utilisant JSON.

## Points de terminaison principaux

### Émetteurs (Issuers)

```
GET /api/v3/issuers/
GET /api/v3/issuers/{id}/
POST /api/v3/issuers/
PUT /api/v3/issuers/{id}/
DELETE /api/v3/issuers/{id}/
```

### Classes de badges (BadgeClass)

```
GET /api/v3/badges/
GET /api/v3/badges/{id}/
POST /api/v3/badges/
PUT /api/v3/badges/{id}/
DELETE /api/v3/badges/{id}/
```

### Assertions

```
GET /api/v3/assertions/
GET /api/v3/assertions/{id}/
POST /api/v3/assertions/
PUT /api/v3/assertions/{id}/
DELETE /api/v3/assertions/{id}/
```

## Structure des données OpenBadge v3.0

### Classes principales

- **OpenBadgeCredential** : Credential de base pour un badge
- **Achievement** : Description de la réalisation/compétence
- **AchievementSubject** : Sujet ayant obtenu le badge
- **Profile** : Profil de l'émetteur ou du récipiendaire
- **Evidence** : Preuves justifiant l'obtention
- **Alignment** : Alignement avec des référentiels externes

### Exemple de réponse JSON-LD

```json
{
  "@context": "https://w3id.org/openbadges/v3",
  "type": "OpenBadgeCredential",
  "id": "urn:uuid:e79a029c-1488-4866-8499-3a5abbca0c81",
  "name": "Badge de compétence numérique",
  "issuer": {
    "type": "Profile",
    "id": "https://example.org/issuers/1",
    "name": "Université Numérique",
    "url": "https://example.org",
    "image": "https://example.org/logo.png"
  },
  "issuanceDate": "2023-09-15T00:00:00Z",
  "achievement": {
    "id": "https://example.org/achievements/1",
    "type": "Achievement",
    "name": "Compétences numériques avancées",
    "description": "Ce badge valide des compétences numériques de niveau avancé.",
    "criteria": {
      "narrative": "Pour obtenir ce badge, l'apprenant doit valider l'évaluation finale avec un score minimum de 80%."
    },
    "image": "https://example.org/badges/digital-skills.png"
  },
  "credentialSubject": {
    "type": "AchievementSubject",
    "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
    "achievement": "https://example.org/achievements/1"
  },
  "validFrom": "2023-09-15T00:00:00Z",
  "validUntil": "2026-09-15T00:00:00Z"
}
```

## Authentification

L'API utilise l'authentification par token pour sécuriser les points de terminaison. Pour accéder aux ressources protégées, incluez votre token d'API dans les en-têtes HTTP :

```
Authorization: Token <votre_token>
```

## Filtrage et pagination

Toutes les endpoints de liste prennent en charge le filtrage et la pagination.

### Paramètres de pagination

- `page` : numéro de page
- `page_size` : nombre d'éléments par page

### Paramètres de filtrage

Pour les badges :
- `issuer` : filtrer par émetteur
- `category` : filtrer par catégorie
- `skills` : filtrer par compétence

Pour les assertions :
- `badge_class` : filtrer par classe de badge
- `recipient` : filtrer par destinataire
- `revoked` : filtrer par statut de révocation

## Gestion des versions

L'API prend en charge à la fois OpenBadge v2 et v3. Vous pouvez spécifier la version dans le chemin de l'API :

- `/api/v2/` pour les points de terminaison v2
- `/api/v3/` pour les points de terminaison v3

## Traitement des erreurs

L'API utilise les codes d'état HTTP standard pour indiquer le succès ou l'échec d'une requête.

Codes courants :
- `200 OK` : Requête réussie
- `201 Created` : Ressource créée avec succès
- `400 Bad Request` : Données de requête incorrectes
- `401 Unauthorized` : Authentification requise
- `403 Forbidden` : Accès refusé
- `404 Not Found` : Ressource non trouvée
- `500 Internal Server Error` : Erreur serveur

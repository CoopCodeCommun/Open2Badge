# OpenBadge API Documentation

This page describes Librobadge's RESTful API that allows you to programmatically interact with the platform.

## OpenBadge Specification

Librobadge's API implements the JSON-LD Open Badges v3.0 specification while maintaining compatibility with version 2.0.

### Response Formats

All API responses are in JSON-LD (JavaScript Object Notation for Linked Data) format, which is a method for encoding linked data using JSON.

## Main Endpoints

### Issuers

```
GET /api/v3/issuers/
GET /api/v3/issuers/{id}/
POST /api/v3/issuers/
PUT /api/v3/issuers/{id}/
DELETE /api/v3/issuers/{id}/
```

### Badge Classes

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

## OpenBadge v3.0 Data Structure

### Main Classes

- **OpenBadgeCredential**: Base credential for a badge
- **Achievement**: Description of the achievement/competency
- **AchievementSubject**: Subject who obtained the badge
- **Profile**: Profile of the issuer or recipient
- **Evidence**: Evidence justifying the achievement
- **Alignment**: Alignment with external frameworks

### Example JSON-LD Response

```json
{
  "@context": "https://w3id.org/openbadges/v3",
  "type": "OpenBadgeCredential",
  "id": "urn:uuid:e79a029c-1488-4866-8499-3a5abbca0c81",
  "name": "Digital Competency Badge",
  "issuer": {
    "type": "Profile",
    "id": "https://example.org/issuers/1",
    "name": "Digital University",
    "url": "https://example.org",
    "image": "https://example.org/logo.png"
  },
  "issuanceDate": "2023-09-15T00:00:00Z",
  "achievement": {
    "id": "https://example.org/achievements/1",
    "type": "Achievement",
    "name": "Advanced Digital Skills",
    "description": "This badge validates advanced digital skills.",
    "criteria": {
      "narrative": "To obtain this badge, the learner must pass the final assessment with a minimum score of 80%."
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

## Authentication

The API uses token authentication to secure endpoints. To access protected resources, include your API token in the HTTP headers:

```
Authorization: Token <your_token>
```

## Filtering and Pagination

All list endpoints support filtering and pagination.

### Pagination Parameters

- `page`: page number
- `page_size`: number of items per page

### Filtering Parameters

For badges:
- `issuer`: filter by issuer
- `category`: filter by category
- `skills`: filter by skill

For assertions:
- `badge_class`: filter by badge class
- `recipient`: filter by recipient
- `revoked`: filter by revocation status

## Version Management

The API supports both OpenBadge v2 and v3. You can specify the version in the API path:

- `/api/v2/` for v2 endpoints
- `/api/v3/` for v3 endpoints

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request.

Common codes:
- `200 OK`: Request successful
- `201 Created`: Resource successfully created
- `400 Bad Request`: Incorrect request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

# Librobadge Technical Documentation

This page presents the technical aspects of Librobadge, including the architecture, data models, and implementation processes.

## System Architecture

Librobadge is built on a Django MVT (Model-View-Template) architecture with Django Rest Framework integration for the API.

```
├── core/                  # Main application
│   ├── models/            # Data models
│   │   ├── badge.py       # Models for badges and issuers
│   │   └── user.py        # User model
│   ├── views.py           # Views and viewsets
│   ├── urls.py            # URL configuration
│   ├── templatetags/      # Custom tags and filters
│   └── tests/             # Unit and integration tests
├── templates/             # HTML templates
│   └── core/              # Application-specific templates
│       ├── issuer/        # Templates for issuers
│       └── badge/         # Templates for badges
└── docs/                  # Documentation
    ├── fr/                # French documentation
    └── en/                # English documentation
```

## Data Models

### Relationship Diagram

The main models and their relationships:

```
Issuer (1) ---> (*) BadgeClass (1) ---> (*) Assertion (1) ---> (1) User
                     |
                     v
                 (*) Alignment
```

### Issuer Model

The `Issuer` model represents an organization that issues badges. It can be used for both versions 2 and 3 of OpenBadge.

Main attributes:
- `version`: OpenBadge standard version (v2 or v3)
- `name`: Organization name
- `url`: Organization website
- `email`: Contact email
- `description`: Organization description
- `image`: Organization logo (URL)
- `public_key`: Public key for signed badge verification
- `key_type`: Signature algorithm type (RSA, ED25519, SECP256K1)
- `verification`: Badge verification methods (JSON)

### BadgeClass Model

The `BadgeClass` model defines a badge class that can be awarded. For OpenBadge v3, it corresponds to an Achievement.

Main attributes:
- `version`: OpenBadge standard version (v2 or v3)
- `name`: Badge name
- `type`: Achievement type (Badge, Certificate, Diploma)
- `description`: Detailed badge description
- `image`: Representative badge image
- `criteria_url`: URL of award criteria
- `issuer`: Issuing organization (ForeignKey)
- `category`: Badge category
- `skills`: Skills validated by the badge
- `level`: Difficulty or mastery level

### Assertion Model

The `Assertion` model represents the awarding of a badge to a specific user.

Main attributes:
- `version`: OpenBadge standard version (v2 or v3)
- `badge_class`: Awarded badge (ForeignKey for v2)
- `achievement`: Awarded achievement (ForeignKey for v3)
- `recipient_identifier`: Recipient identifier (hashed email or DID)
- `recipient_type`: Identifier type (email, url, telephone, did)
- `recipient_hashed`: Indicates if the identifier is hashed
- `issuance_date`: Issuance date
- `evidence`: Evidence of achievement (JSON)
- `expires_at`: Expiration date (optional)
- `revoked`: Indicates if the badge has been revoked
- `revocation_reason`: Revocation reason
- `verification_type`: Verification type (hosted, signed)
- `verification`: Verification data (JSON)

### Alignment Model

The `Alignment` model represents the alignment of a badge with an external competency framework.

Main attributes:
- `badge_class`: Aligned badge (ForeignKey)
- `target_name`: Framework name
- `target_url`: Framework URL
- `target_description`: Framework description
- `target_framework`: Competency framework name
- `target_code`: Competency code in the framework

## OpenBadge Version Management

Librobadge manages both v2 and v3 badges through a flexible architecture:

1. Each model (Issuer, BadgeClass, Assertion) has a `version` field
2. Default version: v2 to ensure compatibility
3. v3-specific fields are nullable for v2 objects
4. v3 assertions use `achievement` instead of `badge_class`

For migrating from v2 to v3:
- An existing v2 assertion is preserved
- A new v3 assertion is created
- Common fields are automatically mapped
- v3-specific fields are generated

## User Interfaces

### Main Views

- `PublicIssuerListView`: Public display of issuers
- `IssuerViewSet`: Issuer management
- `BadgeClassViewSet`: Badge management
  - `public_list`: Badges grouped by issuer (public)
  - `my_issuers_badges`: Badges from the connected user's issuers

### HTMX Integration

The application uses HTMX for dynamic interactions:

1. Optimized partial rendering:
   - Separate views for display and processing
   - Partial templates for issuer and badge lists
   - Use of code 286 to indicate a refresh

2. Optimization examples:
   - `hx-swap="none"` for actions triggering a complete refresh
   - `hx-swap="outerHTML"` for partial updates
   - HX-Trigger trigger to trigger events without reloading

## Tests

Tests are organized by functionality:

1. Unit tests:
   - Custom template filters
   - Model creation and validation
   - Relationships between models

2. Integration tests:
   - Public and protected views
   - Badge creation and editing
   - API JSON-LD format

All tests are run with pytest and are documented in the TEST.md file.

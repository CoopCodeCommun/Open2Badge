# Librobadge Documentation

Welcome to the Librobadge documentation, an application for managing OpenBadges compatible with versions 2.0 and 3.0 of the specification.

## Introduction

Librobadge is an open-source application that allows you to manage digital badges according to the Open Badge standard. It enables the creation, management, and issuance of digital badges that are verifiable, portable, and contain detailed information about skills and achievements.

## Implemented Features

### Issuer Management

Librobadge allows you to manage badge-issuing organizations with the following features:

- Creation and configuration of issuing organizations
- Management of issuer profiles (logo, description, website, privacy policy)
- Support for cryptographic keys to sign badges (compliance with Verifiable Credentials)
- Compatibility with OpenBadge versions 2.0 and 3.0

### Badge Creation and Management

- Creation of badge classes with definition of criteria for obtaining them
- Support for v2 badges (BadgeClass) and v3 badges (Achievement)
- Management of skills associated with each badge
- Categorization and badge levels
- Association with issuers

### Badge Display

- Public view to display all badges grouped by issuer
- View for badges from the connected user's issuers
- Responsive interface with Bootstrap for an optimal user experience
- Formatting of skills in the view for clear display

### Alignment with Frameworks

- Association of badges with external competency frameworks
- Definition of frameworks, codes, and descriptions for each alignment
- Links to frameworks (URLs)

### Badge Assertions

- Creation of assertions to award badges to users
- Management of badge lifecycle (issuance, expiration, revocation)
- Support for v2 and v3 assertions
- Storage of evidence of achievement

### HTMX Integration

- Use of HTMX for dynamic interactions without page reloading
- Optimization of partial rendering to improve performance
- Management of modals for badge creation and editing

### Security and Access Control

- Protection of views requiring authentication
- Redirection of unauthenticated users with warning messages
- Server-side form data validation
- Email authentication (passwordless)

## Technical Architecture

Librobadge is developed with:

### Backend
- Django and Django Rest Framework
- Viewset as base views
- SQLite database
- Poetry for dependency management
- django-solo, django-allauth, django-tenant
- Cryptography with Fernet

### Frontend
- Django Templates
- Bootstrap 5 with Material Design
- HTMX for interactivity
- Hyperscript for client-side logic

### Design
- Responsive interface
- FALC (Easy to read and understand)
- Optimized HTMX partial rendering
- "Less JavaScript" approach

## Main Models

### Issuer

An issuer represents an organization that creates and issues badges. It is compatible with v2 and v3 profiles of the OpenBadge specification.

Main attributes:
- Name, URL, email, description
- Logo (image)
- Public key and key type for cryptographic signature
- Privacy policy
- Verification method

### BadgeClass

A badge class defines a specific type of badge that can be awarded. It is compatible with v3 achievements in the specification.

Main attributes:
- Name, description, image
- Criteria for obtaining
- Associated issuer
- Category and level
- Validated skills

### Assertion

An assertion represents the awarding of a badge to a specific user.

Main attributes:
- Badge or achievement awarded
- Recipient
- Issuance and expiration date
- Evidence of achievement
- Revocation status

### Alignment

An alignment associates a badge with an external competency framework.

Main attributes:
- Associated badge
- Name and URL of the framework
- Description and framework
- Competency code

## Languages

- [🇫🇷 Documentation en français](../fr/index.md)
- [🇬🇧 English documentation](index.md)

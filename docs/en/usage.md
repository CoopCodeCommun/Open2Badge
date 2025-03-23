# Librobadge User Guide

This guide presents the main features of Librobadge and explains how to use them.

## Logging into the Application

Librobadge uses a passwordless authentication system based on email:

1. On the login page, enter your email address
2. You will receive a login link by email
3. Click on the link to log in to the application

If you haven't received the email, you can request a new one by using the "Resend login link" link on the login page.

## Managing Issuers

### Viewing Issuers

1. All users can see the list of public issuers by accessing the "Public Issuers" page
2. Logged-in users can see the list of their own issuers by accessing "My Issuers"

### Creating a New Issuer

1. Go to the "My Issuers" section
2. Click on the "Create Issuer" button
3. Fill out the form with the following information:
   - Organization name
   - Website URL
   - Contact email
   - Description
   - Logo URL
   - Version (v2 or v3)
   - For v3 issuers, you can also add:
     - Public key
     - Key type
     - Privacy policy URL
4. Click "Save"

### Editing an Issuer

1. Go to the "My Issuers" section
2. Find the issuer you want to edit
3. Click on the "Edit" button
4. Update the information in the form
5. Click "Save"

## Managing Badges

### Viewing Badges

1. All users can see the list of public badges by accessing the "Public Badges" page
2. Badges are organized by issuer for easier navigation
3. Logged-in users can see the badges of their issuers by accessing "My Badges"

### Creating a New Badge

1. Go to the "My Badges" section
2. Click on the "Create Badge" button
3. Fill out the form with the following information:
   - Badge name
   - Description
   - Image (upload an image for the badge)
   - Criteria URL
   - Issuer (select from your issuers)
   - Category (optional)
   - Skills (comma-separated list)
   - Level (optional)
   - Version (v2 or v3)
4. Click "Save"

### Managing Badge Skills

Skills associated with a badge are entered as comma-separated text. For example:

```
HTML, CSS, JavaScript, Responsive Design
```

These skills will be automatically formatted and displayed in an organized way on the badge page.

### Adding Skill Alignments

To align a badge with an external competency framework:

1. Go to the badge detail page
2. Click "Add Alignment"
3. Fill out the form with:
   - Framework name
   - Framework URL
   - Description (optional)
   - Framework (optional)
   - Competency code (optional)
4. Click "Save"

## Creating Badge Assertions

An assertion represents the awarding of a badge to a recipient.

1. Go to the badge detail page
2. Click "Issue this Badge"
3. Fill out the form with:
   - Recipient identifier (email, URL, phone, or DID)
   - Identifier type
   - Hashing option (to protect privacy)
   - Issuance date
   - Expiration date (optional)
   - Evidence (optional)
4. Click "Issue"

## Verifying a Badge

To verify the authenticity of a badge:

1. Go to the "Verify Badge" page
2. Upload the badge JSON file or enter the badge URL
3. Click "Verify"
4. The system will check:
   - Format validity
   - Signature authenticity (for v3 badges)
   - Revocation status
   - Expiration date

## HTMX Interface

The Librobadge interface uses HTMX to provide a smooth experience:

- Badge and issuer lists update without page reloading
- Creation and editing forms open in modals
- Confirmation and error messages display dynamically

For the best experience, ensure that JavaScript is enabled in your browser.

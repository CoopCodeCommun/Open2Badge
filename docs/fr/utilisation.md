# Guide d'utilisation de Librobadge

Ce guide présente les principales fonctionnalités de Librobadge et explique comment les utiliser.

## Connexion à l'application

Librobadge utilise un système d'authentification sans mot de passe basé sur l'email:

1. Sur la page de connexion, entrez votre adresse email
2. Vous recevrez un lien de connexion par email
3. Cliquez sur le lien pour vous connecter à l'application

Si vous n'avez pas reçu l'email, vous pouvez demander un nouvel envoi en utilisant le lien "Renvoyer le lien de connexion" sur la page de connexion.

## Gestion des émetteurs

### Consulter les émetteurs

1. Tous les utilisateurs peuvent voir la liste des émetteurs publics en accédant à la page "Émetteurs publics"
2. Les utilisateurs connectés peuvent voir la liste de leurs propres émetteurs en accédant à "Mes émetteurs"

### Créer un nouvel émetteur

1. Accédez à la section "Mes émetteurs"
2. Cliquez sur le bouton "Créer un émetteur"
3. Remplissez le formulaire avec les informations suivantes:
   - Nom de l'organisation
   - URL du site web
   - Email de contact
   - Description
   - URL du logo
   - Version (v2 ou v3)
   - Pour les émetteurs v3, vous pouvez également ajouter:
     - Clé publique
     - Type de clé
     - URL de la politique de confidentialité
4. Cliquez sur "Enregistrer"

### Modifier un émetteur

1. Accédez à la section "Mes émetteurs"
2. Trouvez l'émetteur que vous souhaitez modifier
3. Cliquez sur le bouton "Modifier"
4. Mettez à jour les informations dans le formulaire
5. Cliquez sur "Enregistrer"

## Gestion des badges

### Consulter les badges

1. Tous les utilisateurs peuvent voir la liste des badges publics en accédant à la page "Badges publics"
2. Les badges sont organisés par émetteur pour une navigation plus facile
3. Les utilisateurs connectés peuvent voir les badges de leurs émetteurs en accédant à "Mes badges"

### Créer un nouveau badge

1. Accédez à la section "Mes badges"
2. Cliquez sur le bouton "Créer un badge"
3. Remplissez le formulaire avec les informations suivantes:
   - Nom du badge
   - Description
   - Image (téléchargez une image pour le badge)
   - URL des critères d'obtention
   - Émetteur (sélectionnez parmi vos émetteurs)
   - Catégorie (optionnel)
   - Compétences (liste séparée par des virgules)
   - Niveau (optionnel)
   - Version (v2 ou v3)
4. Cliquez sur "Enregistrer"

### Gérer les compétences des badges

Les compétences associées à un badge sont entrées sous forme de texte séparé par des virgules. Par exemple:

```
HTML, CSS, JavaScript, Responsive Design
```

Ces compétences seront automatiquement formatées et affichées de manière organisée sur la page du badge.

### Ajouter des alignements de compétences

Pour aligner un badge avec un référentiel de compétences externe:

1. Accédez à la page de détail du badge
2. Cliquez sur "Ajouter un alignement"
3. Remplissez le formulaire avec:
   - Nom du référentiel
   - URL du référentiel
   - Description (optionnel)
   - Framework (optionnel)
   - Code de la compétence (optionnel)
4. Cliquez sur "Enregistrer"

## Créer des assertions de badge

Une assertion représente l'attribution d'un badge à un destinataire.

1. Accédez à la page de détail du badge
2. Cliquez sur "Émettre ce badge"
3. Remplissez le formulaire avec:
   - Identifiant du destinataire (email, URL, téléphone ou DID)
   - Type d'identifiant
   - Option de hachage (pour protéger la vie privée)
   - Date d'émission
   - Date d'expiration (optionnel)
   - Preuves (optionnel)
4. Cliquez sur "Émettre"

## Vérifier un badge

Pour vérifier l'authenticité d'un badge:

1. Accédez à la page "Vérifier un badge"
2. Téléchargez le fichier JSON du badge ou entrez l'URL du badge
3. Cliquez sur "Vérifier"
4. Le système vérifiera:
   - La validité du format
   - L'authenticité de la signature (pour les badges v3)
   - Le statut de révocation
   - La date d'expiration

## Interface HTMX

L'interface de Librobadge utilise HTMX pour offrir une expérience fluide:

- Les listes de badges et d'émetteurs se mettent à jour sans rechargement de page
- Les formulaires de création et de modification s'ouvrent dans des modales
- Les messages de confirmation et d'erreur s'affichent dynamiquement

Pour une meilleure expérience, assurez-vous que JavaScript est activé dans votre navigateur.

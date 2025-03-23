# OpenBadge 🏆

OpenBadge est une plateforme Django moderne pour la création, l'émission et la gestion de badges numériques conformes aux standards OpenBadges v2 et v3. Elle permet aux organisations de créer et de délivrer des badges numériques vérifiables qui attestent des compétences, des réalisations et des certifications.

[🇬🇧 English version](README.en.md)

## ✨ Fonctionnalités

- 🎯 Support complet des standards OpenBadges v2 et v3
- 🔒 Émission de badges numériques vérifiables et sécurisés
- 🎨 Interface utilisateur moderne et intuitive
- 🔄 API REST complète avec documentation OpenAPI
- 📱 Design responsive pour une utilisation sur tous les appareils
- 🌐 Support multilingue (i18n)
- 🔍 Alignement avec les référentiels de compétences
- 📊 Tableaux de bord pour le suivi des badges émis

## 🚀 Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/openbadge.git
cd openbadge
```

2. Installez les dépendances avec Poetry :
```bash
poetry install
```

3. Configurez les variables d'environnement :
```bash
cp .env.example .env
# Éditez .env avec vos paramètres
```

4. Appliquez les migrations :
```bash
poetry run python manage.py migrate
```

5. Créez un superutilisateur :
```bash
poetry run python manage.py createsuperuser
```

6. Lancez le serveur de développement :
```bash
poetry run python manage.py runserver
```

## 🧪 Tests

Le projet utilise pytest et coverage.py pour les tests. Pour exécuter la suite de tests :

```bash
# Exécuter les tests
poetry run python manage.py test

# Exécuter les tests avec couverture
poetry run coverage run manage.py test
poetry run coverage report
```

## 📖 Documentation

La documentation complète est disponible dans le dossier `docs/` et inclut :

- Guide de démarrage rapide
- Documentation de l'API
- Guide de contribution
- Spécifications techniques

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout de ma fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [Django](https://www.djangoproject.com/) - Le framework web utilisé
- [Django REST framework](https://www.django-rest-framework.org/) - Pour l'API REST
- [Poetry](https://python-poetry.org/) - Pour la gestion des dépendances
- [OpenBadges](https://openbadges.org/) - Pour les spécifications des badges numériques

## 📞 Contact

- Site web : [https://votre-site.com](https://votre-site.com)
- Email : contact@votre-site.com
- Twitter : [@votre-compte](https://twitter.com/votre-compte)

---

Fait avec ❤️ par [Votre Nom/Organisation]

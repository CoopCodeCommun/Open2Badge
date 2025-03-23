# OpenBadge 🏆

OpenBadge is a modern Django platform for creating, issuing, and managing digital badges compliant with OpenBadges v2 and v3 standards. It enables organizations to create and deliver verifiable digital badges that certify skills, achievements, and certifications.

[🇫🇷 Version française](README.md)

## ✨ Features

- 🎯 Full support for OpenBadges v2 and v3 standards
- 🔒 Issue secure and verifiable digital badges
- 🎨 Modern and intuitive user interface
- 🔄 Complete REST API with OpenAPI documentation
- 📱 Responsive design for all devices
- 🌐 Multilingual support (i18n)
- 🔍 Alignment with competency frameworks
- 📊 Dashboards for issued badges tracking

## 🚀 Getting Started

1. Clone the repository:
```bash
git clone https://github.com/your-username/openbadge.git
cd openbadge
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Apply migrations:
```bash
poetry run python manage.py migrate
```

5. Create a superuser:
```bash
poetry run python manage.py createsuperuser
```

6. Run the development server:
```bash
poetry run python manage.py runserver
```

## 🧪 Testing

The project uses pytest and coverage.py for testing. To run the test suite:

```bash
# Run tests
poetry run python manage.py test

# Run tests with coverage
poetry run coverage run manage.py test
poetry run coverage report
```

## 📖 Documentation

Complete documentation is available in the `docs/` folder and includes:

- Quick Start Guide
- API Documentation
- Contribution Guide
- Technical Specifications

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -am 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - The web framework used
- [Django REST framework](https://www.django-rest-framework.org/) - For the REST API
- [Poetry](https://python-poetry.org/) - For dependency management
- [OpenBadges](https://openbadges.org/) - For digital badges specifications

## 📞 Contact

- Website: [https://your-website.com](https://your-website.com)
- Email: contact@your-website.com
- Twitter: [@your-handle](https://twitter.com/your-handle)

---

Made with ❤️ by [Your Name/Organization]

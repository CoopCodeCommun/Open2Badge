from django.test import TestCase
from core.templatetags.string_filters import split, trim

class StringFiltersTests(TestCase):
    """Tests pour les filtres de template personnalisés"""
    
    def test_split_filter(self):
        """Test du filtre split qui divise une chaîne selon un délimiteur"""
        # Test avec une chaîne valide
        result = split("Python,Django,HTMX", ",")
        self.assertEqual(result, ["Python", "Django", "HTMX"])
        
        # Test avec une chaîne vide
        result = split("", ",")
        self.assertEqual(result, [])
        
        # Test avec None
        result = split(None, ",")
        self.assertEqual(result, [])
        
        # Test avec un autre délimiteur
        result = split("Python|Django|HTMX", "|")
        self.assertEqual(result, ["Python", "Django", "HTMX"])
    
    def test_trim_filter(self):
        """Test du filtre trim qui supprime les espaces blancs"""
        # Test avec des espaces au début et à la fin
        result = trim("  Python  ")
        self.assertEqual(result, "Python")
        
        # Test avec une chaîne sans espaces
        result = trim("Python")
        self.assertEqual(result, "Python")
        
        # Test avec une chaîne vide
        result = trim("")
        self.assertEqual(result, "")
        
        # Test avec None
        result = trim(None)
        self.assertEqual(result, "")

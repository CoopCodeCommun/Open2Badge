from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """
    Divise une chaîne de caractères selon un délimiteur.
    Exemple d'utilisation: {{ value|split:',' }}
    """
    if value:
        return value.split(delimiter)
    return []

@register.filter
def trim(value):
    """
    Supprime les espaces blancs au début et à la fin d'une chaîne.
    Exemple d'utilisation: {{ value|trim }}
    """
    if value:
        return value.strip()
    return ''

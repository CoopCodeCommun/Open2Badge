"""Filtres personnalisés pour manipuler des dictionnaires dans les templates Django.

Ce module fournit des filtres utiles pour accéder aux éléments de dictionnaires
et vérifier leurs valeurs dans les templates Django.

Exemple d'utilisation dans un template:
    {% load dict_filters %}
    {% if my_dict|get_item:key %}
        La clé existe et sa valeur est truthy
    {% endif %}

    {% if my_dict|dict_values_all %}
        Toutes les valeurs du dictionnaire sont True
    {% endif %}
"""

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Récupère un élément d'un dictionnaire par sa clé.
    Exemple d'utilisation: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(str(key))

@register.filter
def dict_values_all(dictionary):
    """
    Vérifie si toutes les valeurs d'un dictionnaire sont True.
    Exemple d'utilisation: {{ dictionary|dict_values_all }}
    """
    if not dictionary:
        return False
    return all(dictionary.values())

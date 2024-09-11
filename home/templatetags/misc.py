from django import template

from home.generators import random_password_generator

register = template.Library()


@register.filter(name='concat')
def concat(value, arg):
    """Concatenates the value with the argument."""
    return f"{value}{arg}"


@register.filter(name="generate_password")
def generate_password(size):
    return random_password_generator(size)
#postgresql://grace_care_user:th13hpr8TloIG8eyOK8Mir0gdggnI8YR@/grace_care

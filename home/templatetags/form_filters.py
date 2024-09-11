from django import template
from django.forms import TextInput, CheckboxSelectMultiple, Textarea, CheckboxInput, RadioSelect, Select, SelectMultiple

register = template.Library()


@register.filter
def is_text(widget):
    return isinstance(widget, TextInput)


@register.filter
def is_textarea(widget):
    return isinstance(widget, Textarea)


@register.filter
def is_checkbox(widget):
    return isinstance(widget, CheckboxInput)


@register.filter
def is_select(widget):
    return isinstance(widget, Select)


@register.filter
def is_radio(widget):
    return isinstance(widget, RadioSelect)


@register.filter
def is_select_multiple(widget):
    return isinstance(widget, CheckboxSelectMultiple)

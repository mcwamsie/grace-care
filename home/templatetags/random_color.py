import random

from django import template

register = template.Library()
# colors = [
#         'bg-red-400', 'bg-red-500',
#         'bg-red-600', 'bg-red-700', 'bg-red-800', 'bg-red-900',
#         'bg-orange-400', 'bg-orange-500',
#         'bg-orange-600', 'bg-orange-700', 'bg-orange-800', 'bg-orange-900', 'bg-yellow-400', 'bg-yellow-500',
#         'bg-yellow-600', 'bg-yellow-700', 'bg-yellow-800', 'bg-yellow-900',
#         'bg-green-400', 'bg-green-500',
#         'bg-green-600', 'bg-green-700', 'bg-green-800', 'bg-green-900',
#         'bg-teal-400', 'bg-teal-500',
#         'bg-teal-600', 'bg-teal-700', 'bg-teal-800', 'bg-teal-900',
#         'bg-blue-400', 'bg-blue-500',
#         'bg-blue-600', 'bg-blue-700', 'bg-blue-800', 'bg-blue-900',
#         'bg-indigo-400', 'bg-indigo-500',
#         'bg-indigo-600', 'bg-indigo-700', 'bg-indigo-800', 'bg-indigo-900',
#         'bg-purple-400', 'bg-purple-500',
#         'bg-purple-600', 'bg-purple-700', 'bg-purple-800', 'bg-purple-900',
#         'bg-pink-400', 'bg-pink-500',
#         'bg-pink-600', 'bg-pink-700', 'bg-pink-800', 'bg-pink-900',
#     ]
TAILWIND_BG_COLORS = [
    'bg-red-500', 'bg-blue-500', 'bg-green-500',
    'bg-yellow-500', 'bg-indigo-500', 'bg-purple-500',
    'bg-pink-500', 'bg-gray-500'
]

@register.simple_tag
def random_color():
    return random.choice(TAILWIND_BG_COLORS)

@register.simple_tag(takes_context=True)
def random_user_color(context):
    request = context['request']

    # Check if the color is already in the session
    if 'bg_color' not in request.session:
        # If not, select a random color and store it in the session
        bg_color = random.choice(TAILWIND_BG_COLORS)
        request.session['bg_color'] = bg_color
    else:
        # Retrieve the color from the session
        bg_color = request.session['bg_color']
    return bg_color

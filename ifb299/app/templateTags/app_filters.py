from django import template

register = template.Library()

@register.filter(name='category_image')
def category_image(value):
    return 'images/' + value.lower() + '.png'

@register.filter(name='category_banner')
def category_banner(value):
	return 'images/' + value.lower() + '_banner1.png'

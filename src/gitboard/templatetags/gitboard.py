from django import template
import re

register = template.Library()

@register.filter(name="extract_page_num")
def page_num_from_params(value):
    page_pattern = re.compile("&page=(\d{1,4})")
    match = page_pattern.search(value)
    if match:
        return match.group(1)

@register.filter(name="minus")
def minus(value, args):
    return int(args) - int(value)
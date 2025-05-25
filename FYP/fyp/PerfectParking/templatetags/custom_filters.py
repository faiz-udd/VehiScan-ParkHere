from django import template

register = template.Library()

@register.filter
def divided_by(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def floatmul(value, arg):
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0

@register.filter
def percentage(value, total):
    try:
        return (float(value) / float(total)) * 100
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
    
@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return ''
    
@register.filter
def abs(value):
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value

@register.filter
def yesno(value, arg):
    """
    Enhanced yesno filter that can handle:
    - Boolean values
    - Numeric comparisons
    - Default Django yesno behavior
    """
    if isinstance(value, bool):
        true_val, false_val = arg.split(',')
        return true_val if value else false_val
    try:
        # Handle comparison cases
        true_val, false_val = arg.split(',')
        return true_val if value else false_val
    except (ValueError, AttributeError):
        return ''
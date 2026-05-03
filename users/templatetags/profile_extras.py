from django import template

register = template.Library()


@register.filter
def ru_age(value):
    try:
        age = int(value)
    except (TypeError, ValueError):
        return value

    if 11 <= age % 100 <= 14:
        word = "лет"
    elif age % 10 == 1:
        word = "год"
    elif 2 <= age % 10 <= 4:
        word = "года"
    else:
        word = "лет"

    return f"{age} {word}"
from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css):
    """
    Append CSS classes to a bound field's widget.
    Usage: {{ form.field|add_class:"form-control is-invalid" }}
    """
    if not hasattr(field, "field"):
        return field
    existing = field.field.widget.attrs.get("class", "")
    classes = f"{existing} {css}".strip() if existing else css
    attrs = {**field.field.widget.attrs, "class": classes}
    return field.as_widget(attrs=attrs)


@register.filter(name="split")
def split(value, sep=","):
    """Split a string in templates: {{ 'a,b'|split:',' }}"""
    return [s.strip() for s in str(value).split(sep)]
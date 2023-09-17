from mypy.plugin import Plugin
from mypy_django_plugin.transformers import fields

_get_current_field_from_assignment = fields._get_current_field_from_assignment


def patched_get_current_field_from_assignment(ctx, django_context):
    try:
        return _get_current_field_from_assignment(ctx, django_context)
    except Exception as e:
        return None


def plugin(version: str):
    fields._get_current_field_from_assignment = patched_get_current_field_from_assignment
    return Plugin

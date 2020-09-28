"""
API helpers for django-rest-framework.
"""

from django.contrib.auth.models import AnonymousUser, Permission

from rest_framework import serializers


class FieldPermissionSerializerMixin:
    """
    ModelSerializer logic for marking fields as ``read_only=True`` when a user is found not to have
    change permissions.
    """

    def __init__(self, *args, **kwargs):
        super(FieldPermissionSerializerMixin, self).__init__(*args, **kwargs)

        request = self.context.get('request', None)
        user = request.user if hasattr(request, 'user') else AnonymousUser()
        model = self.Meta.model
        model_name = model._meta.model_name
        app_label = model._meta.app_label

        # this might be too broad
        model_field_names = [f.name for f in model._meta.get_fields()]
        for name in model_field_names:
            in_fields = name in self.fields
            permission_exists = Permission.objects.filter(
                codename=f'can_view_{model_name}_{name}'
            ).exists()
            has_view = user.has_perm(
                f'{app_label}.can_view_{model_name}_{name}')
            if in_fields and permission_exists and not has_view:
                self.fields.remove(name)
                continue

            has_change = user.has_perm(
                f'{app_label}.can_change_{model_name}_{name}')
            if in_fields and not has_change:
                self.fields[name].read_only = True


class FieldPermissionSerializer(FieldPermissionSerializerMixin, serializers.ModelSerializer):
    pass

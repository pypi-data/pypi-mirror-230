from django.conf import settings as django_settings

settings = getattr(django_settings, "DJANGO_NEXT_AUTH_ADAPTER", {})

permission_classes = settings.get("PERMISSION_CLASSES")
remote_auth_token = settings.get("REMOTE_AUTH_TOKEN", None)

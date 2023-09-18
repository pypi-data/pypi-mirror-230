from django.dispatch import Signal

# Signal sent when a user is created.
user_created = Signal()
# Signal when a user is updated.
user_updated = Signal()

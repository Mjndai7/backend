from django.apps import AppConfig


class DirectMessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'direct_messages'

    def ready(self):
        import direct_messages.signals  # noqa

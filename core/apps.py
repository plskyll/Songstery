from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self) -> None:
        import core.models.profile  # noqa: F401 — registers User post_save signals
        import core.signals  # noqa: F401 — registers Like / Comment notification signals

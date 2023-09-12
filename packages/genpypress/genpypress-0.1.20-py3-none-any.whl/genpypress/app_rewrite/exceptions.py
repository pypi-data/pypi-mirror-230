class AppRewriteError(Exception):
    """Generická chyba aplikace."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ConfigError(AppRewriteError):
    """Chyba konfigurace aplikace"""

    pass


class ConfigInvalidContentError(ConfigError):
    """Chyba obsahu konfigurace"""

    pass


class ConfigEmptyContent(ConfigError):
    """Neexistující konfigurace"""

    pass


class LimitError(AppRewriteError):
    """Příliš velký počet souborů"""

    pass

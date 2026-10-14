"""Settings package.

Select the settings module by setting the `DJANGO_SETTINGS_MODULE` env var
to `house_cleaner.settings.dev` or `house_cleaner.settings.prod`.

This package intentionally doesn't set any settings itself; it only
organizes the files. Use the submodules directly.
"""

__all__ = ["base", "dev", "prod"]

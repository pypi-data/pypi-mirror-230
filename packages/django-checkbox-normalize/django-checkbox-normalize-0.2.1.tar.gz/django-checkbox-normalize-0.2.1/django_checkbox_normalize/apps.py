
from django.apps import AppConfig


class DjangoCheckboxNormalizeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_checkbox_normalize'

    def ready(self):
        from django.conf import settings
        if getattr(settings, "DJANGO_CHECKBOX_NORMALIZE_FOR_ALL", False):
            self.normalize_for_all()

    def normalize_for_all(self):
        from django import forms
        from django.contrib.admin import ModelAdmin
        from django_checkbox_normalize.admin import DjangoCheckboxNormalizeAdmin

        ModelAdmin._django_checkbox_normalize_old_media = ModelAdmin.media
        @property
        def media(self):
            result = self._django_checkbox_normalize_old_media
            result += forms.Media(media=DjangoCheckboxNormalizeAdmin.Media)
            return result
        ModelAdmin.media = media

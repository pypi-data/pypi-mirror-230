from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DjangoSiteWarningsConfig(AppConfig):
    name = 'django_site_warnings'
    verbose_name = _("Django Site Warnings")

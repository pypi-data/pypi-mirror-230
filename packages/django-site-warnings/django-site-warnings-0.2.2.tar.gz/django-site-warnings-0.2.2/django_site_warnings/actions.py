
from django.utils.translation import gettext_lazy as _

from .models import Warning


def django_site_warnings_acknowledge(modeladmin, request, queryset):
    items = []
    for item in queryset.all():
        if not item.ack:
            item.acknowledge(save=False)
            items.append(item)
    Warning.objects.bulk_update(items, fields=["ack", "ack_time"])
    message = _("{count} warnings acknowledged.").format(count=len(items))
    modeladmin.message_user(request, message)
django_site_warnings_acknowledge.short_description = _("Acknowledge selected {model_name}").format(model_name=Warning._meta.verbose_name)

def django_site_warnings_deny(modeladmin, request, queryset):
    items = []
    for item in queryset.all():
        if item.ack:
            item.deny(save=False)
            items.append(item)
    Warning.objects.bulk_update(items, fields=["ack", "ack_time"])
    message = _("{count} warnings denied.").format(count=len(items))
    modeladmin.message_user(request, message)
django_site_warnings_deny.short_description = _("Deny selected {model_name}").format(model_name=Warning._meta.verbose_name)

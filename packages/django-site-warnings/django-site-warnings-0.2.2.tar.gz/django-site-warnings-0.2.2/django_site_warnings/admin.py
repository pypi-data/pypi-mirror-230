
from magic_import import import_from_string

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from django_simpletask2.actions import reset_selected_tasks as reset_selected_tasks_core
from django_simpletask2.actions import force_do_selected_tasks as force_do_selected_tasks_core
from django_simpletask2.actions import mark_selected_tasks_done as mark_selected_tasks_done_core

from .models import Warning
from .models import WaringCategory

from .actions import django_site_warnings_acknowledge
from .actions import django_site_warnings_deny

DjangoSiteWarningsBaseAdminName = getattr(settings, "DJANGO_SITE_WARNINGS_ADMIN_BASE", "django.contrib.admin.ModelAdmin")
DjangoSiteWarningsBaseAdmin = import_from_string(DjangoSiteWarningsBaseAdminName)
if not DjangoSiteWarningsBaseAdmin:
    DjangoSiteWarningsBaseAdmin = admin.ModelAdmin

def reset_selected_tasks(*args, **kwargs):
    return reset_selected_tasks_core(*args, **kwargs)
reset_selected_tasks.short_description = _("Reset Warning Message Sending Status")

def force_do_selected_tasks(*args, **kwargs):
    return force_do_selected_tasks_core(*args, **kwargs)
force_do_selected_tasks.short_description = _("Force To Send Warning Message")

def mark_selected_tasks_done(*args, **kwargs):
    return mark_selected_tasks_done_core(*args, **kwargs)
mark_selected_tasks_done.short_description = _("Mark Select Warning Message Already Sent")

class WaringCategoryAdmin(DjangoSiteWarningsBaseAdmin):
    list_display = ["name", "code"]
    ordering = ["display_order"]

class WarningAdmin(DjangoSiteWarningsBaseAdmin):
    list_display = ["title", "add_time", "status", "success", "ack"]
    list_filter = ["category", "status", "ack"]
    readonly_fields = [] + Warning.SIMPLE_TASK_FIELDS

    actions = [
        django_site_warnings_acknowledge,
        django_site_warnings_deny,
        reset_selected_tasks,
        force_do_selected_tasks,
        mark_selected_tasks_done,
    ]

admin.site.register(WaringCategory, WaringCategoryAdmin)
admin.site.register(Warning, WarningAdmin)

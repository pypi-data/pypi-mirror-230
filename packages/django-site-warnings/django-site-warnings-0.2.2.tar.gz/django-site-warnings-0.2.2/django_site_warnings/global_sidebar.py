from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse

django_site_warnings_menu_item_of_applist = {
    "title": _("Warnings"),
    "icon": "fas fa-radiation",
    "url": reverse("admin:app_list", args=["django_site_warnings"]),
    "active_patterns": ".*\/django_site_warnings\/.*",
    "permissions": ["django_site_warnings.view_warning", "django_site_warnings.view_warningcategory"],
}

django_site_warnings_menu_item_of_warning = {
    "title": _("Warnings"),
    "icon": "fas fa-radiation",
    "model": "django_site_warnings.warning",
    "permissions": ["django_site_warnings.view_warning"],
}

django_site_warnings_menu_item_of_category = {
    "title": _("Warning Categories"),
    "icon": "fa fa-boxes",
    "model": "django_site_warnings.waringcategory",
    "permissions": ["django_site_warnings.view_waringcategory"],
}

def get_default_global_sidebar(request=None):
    return [
        {
            "title": _("Home"),
            "icon": "fa fa-home",
            "url": getattr(settings, "ADMIN_SITE_HOME_URL", "/admin/"),
        },
        {
            "title": _("System Settings"),
            "icon": "fas fa-cogs",
            "children": [
                {
                    "title": _("User Manage"),
                    "icon": "fas fa-user",
                    "model": "auth.user",
                    "permissions": ["auth.view_user"],
                },
                {
                    "title": _("Group Manage"),
                    "icon": "fas fa-users",
                    "model": "auth.group",
                    "permissions": ["auth.view_group"],
                },
                django_site_warnings_menu_item_of_warning,
                django_site_warnings_menu_item_of_category,
            ]
        }
    ]

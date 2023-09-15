import typing
from django.conf import settings

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.template.loader import render_to_string

from django_simpletask2.models import SimpleTask
from django_safe_fields.fields import SafeCharField
from django_safe_fields.fields import SafeTextField

from django_site_warnings.send_notify import sendmail_notify

SIMPLE_TASK_INSTANCE = SimpleTask
PAYLOAD_TYPE = typing.Dict[str, typing.Any]
FORCE_TYPE = bool
SEND_NOTIFY_CALLBACK_TYPE = typing.Callable[[SIMPLE_TASK_INSTANCE, typing.Optional[PAYLOAD_TYPE], typing.Optional[FORCE_TYPE]], None]

class WaringCategory(models.Model):
    code = models.CharField(max_length=255, unique=True, verbose_name=_("Warning Category Code"))
    name = models.CharField(max_length=255, verbose_name=_("Warning Category Name"))
    display_order = models.IntegerField(default=0, null=True, blank=True, verbose_name=_("Display Order"))

    class Meta:
        verbose_name = _("Warning Category")
        verbose_name_plural = _("Warning Categories")

    def __str__(self):
        return self.name

    @classmethod
    def get(cls, code):
        if isinstance(code, WaringCategory):
            return code
        try:
            return cls.objects.get(code=code)
        except cls.DoesNotExist:
            category = cls()
            category.code = code
            category.name = code
            category.display_order = 99999
            category.save()
            return category

class Warning(SimpleTask):

    FAILED = 50

    STATUS = [
        (SimpleTask.READY, _("Message Not sent yet")),
        (SimpleTask.DOING, _("Message is sending")),
        (SimpleTask.DONE, _("Messgage Sent")),
    ]
    
    send_notify_callbacks = []

    status = models.IntegerField(choices=STATUS, default=SimpleTask.READY, verbose_name=_("Notify Status"), editable=False)
    success = models.BooleanField(null=True, verbose_name=_("Notify Sent Success"), editable=False)

    category = models.ForeignKey(WaringCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Warning Category"))
    title = SafeCharField(max_length=1024, verbose_name=_("Warning Title"))
    data = SafeTextField(null=True, blank=True, verbose_name=_("Warning Data"))
    ack = models.BooleanField(default=False, verbose_name=_("Acknowledged"))
    ack_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Acknowledged Time"))

    class Meta:
        verbose_name = _("Warning")
        verbose_name_plural = _("Warnings")

    def __str__(self):
        return self.title

    def get_notify_email_subject(self):
        site_name = getattr(settings, "DJANGO_SITE_WARNING_SITE_NAME", "Site Warning")
        template = getattr(settings, "DJANGO_SITE_WARNING_NOTIFY_MAIL_SUBJECT", _("[{site_name}]{title}"))
        return template.format(site_name=site_name, title=self.title)

    def get_notify_email_content(self):
        site_name = getattr(settings, "DJANGO_SITE_WARNING_SITE_NAME", "Site Warning")
        return render_to_string("django_site_warnings/notify.html", {
            "title": site_name,
            "subtitle": _("Site Warning"),
            "category": self.category.name,
            "content": self.title,
            "extra_data": self.data,
            "create_time": self.add_time,
        })

    @classmethod
    def register_send_notify(cls, send_notify:SEND_NOTIFY_CALLBACK_TYPE):
        if not send_notify in cls.send_notify_callbacks:
            cls.send_notify_callbacks.append(send_notify)

    def do_task_main(self, payload=None, force=False):
        for send_notify in self.send_notify_callbacks:
            send_notify(self, payload, force)
        return True

    @classmethod
    def make(cls, category, title, data=None, save=False):
        category = WaringCategory.get(category)
        try:
            instance = cls.objects.get(ack=False, category=category, title=title)
            return None
        except cls.DoesNotExist:
            instance = cls()
            instance.category = category
            instance.title = title
            instance.data = data
            if save:
                instance.save()
            return instance

    @classmethod
    def makemany(cls, category, warnings, save=False):
        warning_instances = []
        for warning in warnings:
            if isinstance(warning, (list, tuple)):
                data = warning[1]
                warning = warning[0]
            else:
                data = None
            instance = Warning.make(category, warning, data=data, save=False)
            if instance:
                instance.ready(save=False)
                warning_instances.append(instance)
        if save:
            Warning.objects.bulk_create(warning_instances)
        return warning_instances

    def acknowledge(self, save=True):
        self.ack = True
        self.ack_time = timezone.now()
        if save:
            self.save()
    
    def deny(self, save=True):
        self.ack = False
        self.ack_time = None
        if save:
            self.save()

Warning.register_send_notify(sendmail_notify)

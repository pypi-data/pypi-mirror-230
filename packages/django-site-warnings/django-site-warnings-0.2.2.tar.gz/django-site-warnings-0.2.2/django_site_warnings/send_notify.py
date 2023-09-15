import logging

from django.conf import settings

from sendmail import sendmail

logger = logging.getLogger(__name__)

def sendmail_notify(warning, payload, force):
    from_address = getattr(settings, "DJANGO_SITE_WARNING_NOTIFY_MAIL_FROM")
    to_addresses = getattr(settings, "DJANGO_SITE_WARNING_NOTIFY_MAIL_TO")
    server = getattr(settings, "DJANGO_SITE_WARNING_NOTIFY_MAIL_SERVER")
    port = getattr(settings, "DJANGO_SITE_WARNING_NOTIFY_MAIL_PORT")
    ssl = getattr(settings, "DJANGO_SITE_WARNING_NOTIFY_MAIL_SSL")
    user = getattr(settings, "DJANGO_SITE_WARNING_NOTIFY_MAIL_USER")
    password = getattr(settings, "DJANGO_SITE_WARNING_NOTIFY_MAIL_PASSWORD")

    subject = warning.get_notify_email_subject()
    content = warning.get_notify_email_content()

    sendmail(
        from_address,
        to_addresses,
        content,
        subject,
        attachs=None,
        is_html_content=True,
        encoding="utf-8",
        charset="utf-8",
        host=server,
        port=port,
        ssl=ssl,
        user=user,
        password=password,
        )

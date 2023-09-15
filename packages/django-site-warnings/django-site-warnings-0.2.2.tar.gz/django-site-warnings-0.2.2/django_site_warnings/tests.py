from distutils.log import warn
from django.test import TestCase
from queue import Queue

from .models import Warning
from .models import WaringCategory
from .global_sidebar import get_default_global_sidebar

notify_queue = Queue()
def send_notify(task, payload=None, force=False):
    notify_queue.put(task.pk)

Warning.register_send_notify(send_notify)

class TestDjangoSiteWarnings(TestCase):

    def setUp(self):
        self.category = WaringCategory()
        self.category.code = "category"
        self.category.name = "category"
        self.category.save()
        self.warning = Warning.make(
            category=self.category,
            title="Account not exists...",
            data="Account: test01",
            save=True,
            )

    def test01(self):
        assert len(Warning.objects.all()) == 1
        assert self.warning.category.pk == self.category.pk

    def test02(self):
        self.warning.do_task()
        assert notify_queue.get(timeout=1) == self.warning.pk

    def test03(self):
        self.warning.acknowledge()
        assert Warning.objects.all()[0].ack

        self.warning.deny()
        assert Warning.objects.all()[0].ack is False

    def test04(self):
        menus = get_default_global_sidebar()
        assert menus
        assert isinstance(menus, list)

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class SimplePublishModel(models.Model):

    published = models.BooleanField(default=False, verbose_name=_("Published"))
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Add Time"))
    publish_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Publish Time"))
    unpublish_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Unpublish Time"))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.published and not self.publish_time:
            self.publish_time = timezone.now()
            self.unpublish_time = None
        elif self.pk and (not self.published):
            self.unpublish_time = timezone.now()
            self.publish_time = None
        return super().save(*args, **kwargs)

    def is_published(self):
        return self.published

    def do_publish(self, save=False):
        self.published = True
        self.publish_time = timezone.now()
        self.unpublish_time = None
        if save:
            self.save()
        return self

    def do_unpublish(self, save=False):
        self.published = False
        self.publish_time = None
        self.unpublish_time = timezone.now()
        if save:
            self.save()
        return self

    def toggle_publish(self, save=False):
        if self.published:
            self.do_unpublish(save=save)
        else:
            self.do_publish(save=save)
        return self


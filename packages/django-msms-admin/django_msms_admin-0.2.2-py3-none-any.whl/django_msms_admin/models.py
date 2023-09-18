from django.db import models
from django.urls import reverse
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

class DjangoMsmsModelAbstractBase(models.Model):
    app_label = models.CharField(max_length=64, blank=True, editable=False, verbose_name=_("App Label"))
    model_name = models.CharField(max_length=64, blank=True, editable=False, verbose_name=_("Model Name"))
    type_name = models.CharField(max_length=64, blank=True, editable=False, verbose_name=_("Type Name"))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.app_label != self._meta.app_label:
            self.app_label = self._meta.app_label
        if self.model_name != self._meta.model_name:
            self.model_name = self._meta.model_name
        if self.type_name != self._meta.verbose_name:
            self.type_name = self._meta.verbose_name
        return super().save(*args, **kwargs)

    def get_real_object(self):
        model = self.get_real_model()
        if not model:
            return None
        else:
            return model.objects.get(pk=self.pk)

    def get_real_model(self):
        model = apps.get_model(self.app_label, self.model_name)
        if model == self.__class__:
            # real model can NOT be the base model
            # we prefer None instead of the base model
            return None
        else:
            return model

    def get_change_url(self):
        view_name = "admin:%s_%s_change" % (self.app_label, self.model_name)
        url = reverse(view_name, kwargs={"object_id": self.pk})
        return url

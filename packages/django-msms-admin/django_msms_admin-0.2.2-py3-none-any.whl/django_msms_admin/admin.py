from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.urls import path
from django.urls import reverse
from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.admin.options import csrf_protect_m


def subclass_model_key(obj):
    return getattr(obj, "msms_priority", id(obj))


class DjangoSubclassAdmin(admin.ModelAdmin):
    base_model = None

    class Media:
        css = {
            "all": [
                "admin/css/forms.css",
                "django-msms-admin/css/django-msms-admin.css",
            ]
        }
        js = [
            "admin/js/vendor/jquery/jquery.js",
            "django-msms-admin/js/django-msms-admin.js",
            "admin/js/jquery.init.js",
        ]

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        opts = self.get_base_model()._meta
        view_name = "admin:%s_%s_changelist" % (opts.app_label, opts.model_name)
        url = reverse(view_name)
        return HttpResponseRedirect(url)

    def get_base_model(self):
        if self.base_model:
            return self.base_model
        else:
            for m, p in self.model._meta.parents.items():
                return m
        return self.model

class DjangoMsmsAdmin(admin.ModelAdmin):


    class Media:
        css = {
            "all": [
                "admin/css/forms.css",
                "django-msms-admin/css/django-msms-admin.css",
            ]
        }
        js = [
            "admin/js/vendor/jquery/jquery.js",
            "django-msms-admin/js/django-msms-admin.js",
            "admin/js/jquery.init.js",
        ]


    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path('add/select-subclass-model/', self.admin_site.admin_view(self.select_subclass_model_view), name='%s_%s_select_subclass_model' % info),
        ]
        return custom_urls + urls

    def select_subclass_model_view(self, request):
        subclass_model = request.GET.get("subclass_model")
        if subclass_model and subclass_model != "0":
            model = apps.get_model(subclass_model)
            if model:
                view_name = "admin:%s_%s_add" % (model._meta.app_label, model._meta.model_name)
                url = reverse(view_name)
                return HttpResponseRedirect(url)
        else:
            if subclass_model == "0":
                error_message = _("Please select a subclass.")
            else:
                error_message = ""
            opts = self.model._meta
            return render(request, "admin/select-subclass-model-view.html", {
                "opts": opts,
                "title": _("Please select subclass of %s") % (opts.verbose_name),
                "media": self.media,
                "subclasses": self.get_subclasses(),
                "error_message": error_message,
            })

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if object_id:
            instance = self.model.objects.get(pk=object_id).get_real_model().objects.get(pk=object_id)
            url = instance.get_change_url()
            return HttpResponseRedirect(url)
        else:
            return super().changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        info = self.model._meta.app_label, self.model._meta.model_name
        url = reverse('admin:%s_%s_select_subclass_model' % info)
        return HttpResponseRedirect(url)

    def get_subclasses(self):
        if hasattr(self, "subclasses"):
            return getattr(self, "subclasses")
        else:
            subclasses = []
            for model in self.get_all_subclass_models():
                self._register_subclass_model(subclasses, model)
            return subclasses

    def get_all_subclass_models(self):
        models = []
        for model in apps.get_models():
            if self.model in model._meta.parents:
                models.append(model)
        return models

    def _register_subclass_model(self, subclasses, model):
        category = getattr(model, "msms_category", None) or _("Default")
        if not subclasses:
            subclasses.append({
                "title": category,
                "children": [{
                    "children": [],
                }]
            })
        found = False
        for subclass in subclasses:
            if subclass["title"] == category:
                found = True
                subclass["children"][0]["children"].append(model)
                subclass["children"][0]["children"].sort(key=subclass_model_key)
        if not found:
            subclasses.append({
                "title": category,
                "children": [{
                    "children": [model]
                }]
            })
        return subclass

import json

from fastutils import strutils

from django.urls import path
from django.urls import reverse
from django.urls import reverse_lazy
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from django.template.loader import render_to_string

from django.contrib import admin


from django_object_toolbar_admin.admin import DjangoObjectToolbarAdmin

from .settings import DJANGO_REDIS_DATA_MANAGER_AUTO_REGISTER


class RedisInstanceAdmin(DjangoObjectToolbarAdmin, admin.ModelAdmin):
    open_children_limit = 20

    list_display = ["title", "django_object_toolbar"]
    list_display_links = None
    search_fields = ["title", "connection"]

    django_object_toolbar_buttons = [
        "data_manager_link",
        "instance_edit_link",
    ]

    def data_manager_link(self, obj):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return reverse("admin:{}_{}_data_manager".format(app_label, model_name), kwargs={"instance_id": obj.pk}) 
    data_manager_link.title = _("Data Manager")
    data_manager_link.icon = "fa fa-life-ring"

    def instance_edit_link(self, obj):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return reverse("admin:{}_{}_change".format(app_label, model_name), args=[obj.pk]) 
    instance_edit_link.title = _("Edit")
    instance_edit_link.icon = "fa fa-edit"


    def get_urls(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return [
            path("data-manager-api/<int:instance_id>/delete", self.admin_site.admin_view(self.data_manager_delete), name="{0}_{1}_delete".format(app_label, model_name)),
            path("data-manager-api/<int:instance_id>/flushdb", self.admin_site.admin_view(self.data_manager_flushdb), name="{0}_{1}_flushdb".format(app_label, model_name)),
            path("data-manager-api/<int:instance_id>/getDetail", self.admin_site.admin_view(self.data_manager_getDetail), name="{0}_{1}_getDetail".format(app_label, model_name)),
            path("data-manager-api/<int:instance_id>/getKeys", self.admin_site.admin_view(self.data_manager_getKeys), name="{0}_{1}_getKeys".format(app_label, model_name)),
            path("data-manager/<int:instance_id>/", self.admin_site.admin_view(self.data_manager_view), name="{0}_{1}_data_manager".format(app_label, model_name)),
        ] + super().get_urls()

    def data_manager_delete(self, request, instance_id):
        instance = self.model.objects.get(pk=instance_id)
        key = request.GET.get("key", None)
        if key:
            db = instance.get_db()
            keys = db.keys(key + "*")
            if keys:
                db.delete(*keys)
            result = True
        else:
            result = False
        return JsonResponse({
            "result": result,
        })

    def data_manager_flushdb(self, request, instance_id):
        instance = self.model.objects.get(pk=instance_id)
        db = instance.get_db()
        db.flushdb()
        return JsonResponse({
            "result": True,
        })

    def data_manager_view(self, request, instance_id):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        instance = self.model.objects.get(pk=instance_id)
        config = {
            "data-api-url": reverse("admin:{}_{}_getKeys".format(app_label, model_name), kwargs={"instance_id": instance_id}),
            "detail-api-url": reverse("admin:{}_{}_getDetail".format(app_label, model_name), kwargs={"instance_id": instance_id}),
            "flushdb-api-url": reverse("admin:{}_{}_flushdb".format(app_label, model_name), kwargs={"instance_id": instance_id}),
            "delete-api-url": reverse("admin:{}_{}_delete".format(app_label, model_name), kwargs={"instance_id": instance_id}),
            "title": instance.title,
        }
        return render(request,  "django-redis-data-manager/data-manager.html", {
           "opts": self.model._meta,
           "object": instance,
           "media": self.media,
           "config_json": json.dumps(config),
           "q": request.GET.get("q", ""),
        })

    def data_manager_getDetail(self, request, instance_id):
        instance = self.model.objects.get(pk=instance_id)
        key = request.GET.get("key", "")
        db = instance.get_db()
        if not key:
            return self.data_manager_get_root_detail_table(request, db)
        elif db.exists(key):
            return self.data_manager_get_key_detail_table(request, db, key)
        else:
            return self.data_manager_get_namespace_detail_table(request, db, key)

    def data_manager_get_key_detail_table(self, request, db, key):
        value_type = db.type(key)
        if value_type == "string":
            value = db.get(key)
            try:
                value = json.dumps(json.loads(value), ensure_ascii=False, indent=4, sort_keys=True)
            except:
                pass
        elif value_type == "list":
            value = {
                "llen": db.llen(key),
                "lrange": db.lrange(key, 0, -1),
            }
        elif value_type == "hash":
            fields = db.hgetall(key)
            value = {
                "field_count": len(fields),
                "fields": fields,
            }
        elif value_type == "set":
            smembers = db.smembers(key)
            value = {
                "smembers_count": len(smembers),
                "smembers": smembers,
            }
        else:
            value = "Unknown Type"
        value_ttl = db.ttl(key)
        html = render_to_string("django-redis-data-manager/key-detail-table-{0}.html".format(value_type), {
            "key": key,
            "value_type": value_type,
            "value": value,
            "value_ttl": value_ttl,
        }).strip().replace("\n", "")
        return JsonResponse({
            "html": html,
        })

    def data_manager_get_namespace_detail_table(self, request, db, key):
        keys = db.keys(key + "*")
        html = render_to_string("django-redis-data-manager/namespace-detail-table.html", {
            "key": key,
            "count": len(keys)
        }).strip().replace("\n", "")
        return JsonResponse({
            "html": html,
        })

    def data_manager_getKeys(self, request, instance_id):
        instance = self.model.objects.get(pk=instance_id)
        q = request.GET.get("q")
        db = instance.get_db()
        if q:
            keys = db.keys("*" + q + "*")
        else:
            keys = db.keys()
        keys.sort()
        sep = instance.key_separator
        nodes = {}
        for key in keys:
            parent = None
            ks = key.split(sep)
            ks_len = len(ks)
            for index in range(ks_len):
                if index == ks_len - 1:
                    leaf = True
                else:
                    leaf = False
                id = sep.join(ks[:index+1])
                if not id in nodes:
                    node = {
                        "text": ks[index],
                        "id": id,
                        "icon": leaf and "jstree-file" or "jstree-folder",
                        "state": {
                            "opened": True,
                        },
                        "children": [],
                    }
                    nodes[id] = node
                    if parent:
                        parent["children"].append(node)
                else:
                    node = nodes[id]
                parent = node
        data = []
        for key, node in nodes.items():
            if len(node["children"]) > self.open_children_limit:
                node["state"]["opened"] = False
            if not sep in key:
                data.append(node)
        return JsonResponse(data, safe=False)

    class Media:
        css = {
            "all": [
                "jquery/plugins/jquery.jstree/themes/default/style.css",
                "fontawesome/css/all.min.css",
                "admin/css/changelists.css",
                "admin/css/forms.css",
                "django-redis-data-manager/django-redis-data-manager.css",
            ]
        }
        js = [
            "admin/js/vendor/jquery/jquery.js",
            "jquery/plugins/jquery.jstree/jstree.js",
            "django-redis-data-manager/django-redis-data-manager.js",
            "admin/js/jquery.init.js"
        ]




if DJANGO_REDIS_DATA_MANAGER_AUTO_REGISTER:
    from .models import RedisInstance
    admin.site.register(RedisInstance, RedisInstanceAdmin)

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class DjangoRedisDataManagerConfig(AppConfig):
    name = 'django_redis_data_manager'
    verbose_name = _("Django Redis Data Manager")

import redis

from django.db import models
from django.utils.translation import ugettext as _

from django_safe_fields.fields import SafeCharField

from .settings import DJANGO_REDIS_DATA_MANAGER_REDIS_INSTANCE_CONNECTION_SAFE_FIELD_PASSWORD
from .settings import DJANGO_REDIS_DATA_MANAGER_AUTO_REGISTER
from .settings import DJANGO_REDIS_DATA_MANAGER_APP_LABEL

class RedisInstanceBase(models.Model):
    title = models.CharField(max_length=64, verbose_name=_("Title"))
    connection = SafeCharField(max_length=4096, password=DJANGO_REDIS_DATA_MANAGER_REDIS_INSTANCE_CONNECTION_SAFE_FIELD_PASSWORD, verbose_name=_("Connection"))
    key_separator = models.CharField(max_length=16, default=":", verbose_name=_("Key Separator"))

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def get_db(self):
        return redis.from_url(self.connection, decode_responses=True)




if DJANGO_REDIS_DATA_MANAGER_AUTO_REGISTER:

    class RedisInstance(RedisInstanceBase):
        class Meta:
            app_label = DJANGO_REDIS_DATA_MANAGER_APP_LABEL
            verbose_name = _("Redis Instance")
            verbose_name_plural = _("Redis Instances")

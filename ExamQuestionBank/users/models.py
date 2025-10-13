from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    使用者
    """
    email = models.EmailField(unique=True, verbose_name="電子郵件")
    is_admin = models.BooleanField(default=False, verbose_name="是否為管理員")

    class Meta:
        db_table = 'user'
        verbose_name = '使用者'
        verbose_name_plural = '使用者'

    def __str__(self):
        return self.username
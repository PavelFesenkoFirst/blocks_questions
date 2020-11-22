from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.urls import reverse
# Create your models here.

from core.polls.models import Block


class Users(AbstractUser):
    """МОдель пользователя, переопределенная"""
    username = models.CharField(max_length=20, unique=True)
    image = models.ImageField(verbose_name='изображение', upload_to='photo', blank=True, null=True, )
    birth_date = models.DateField(null=True, blank=True, help_text='Введите дату следующим образом "год-месяц-число"')
    description = models.TextField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('users:profile')


class ResultsUsers(models.Model):
    """Модель результатов Пользователя"""
    r_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='r_user')
    r_block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='r_block')
    count_try = models.IntegerField(default=0)
    results = models.IntegerField(default=0)
    done = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'

    def check_done(self):
        if self.results >= self.r_block.pass_mark:
            self.done = True
        return self.done

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

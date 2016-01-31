# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20160116_1411'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='idea',
            name='repository',
        ),
        migrations.RemoveField(
            model_name='idea',
            name='subscribers',
        ),
        migrations.DeleteModel(
            name='Idea',
        ),
        migrations.DeleteModel(
            name='Subscriber',
        ),
    ]

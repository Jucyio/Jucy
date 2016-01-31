# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_idea'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='contact_email',
            field=models.CharField(default=b'contact@jucy.io', max_length=256),
            preserve_default=True,
        ),
    ]

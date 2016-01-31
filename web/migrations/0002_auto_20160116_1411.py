# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Repo',
            new_name='Repository',
        ),
        migrations.RemoveField(
            model_name='idea',
            name='github_id',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Idea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('github_id', models.PositiveIntegerField()),
                ('subscribers', models.ManyToManyField(related_name='ideas', to='web.Subscriber')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

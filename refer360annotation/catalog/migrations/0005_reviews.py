# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-11-26 16:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_annotation_ann_rnd'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('category_list', models.CharField(max_length=100000)),
                ('session', models.CharField(default='c00', max_length=3)),
                ('annotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='catalog.Annotation')),
                ('turker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review', to='catalog.Turker')),
            ],
        ),
    ]

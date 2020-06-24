# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-06 11:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

  initial = True

  dependencies = [
  ]

  operations = [
      migrations.CreateModel(
          name='Actions',
          fields=[
              ('id', models.AutoField(auto_created=True,
                                      primary_key=True, serialize=False, verbose_name='ID')),
              ('date', models.DateTimeField(auto_now_add=True)),
              ('action_list', models.CharField(max_length=100000)),
              ('pred_latitude', models.FloatField()),
              ('pred_longitude', models.FloatField()),
              ('start_latitude', models.FloatField()),
              ('start_longitude', models.FloatField()),
              ('session', models.CharField(default='s00', max_length=3)),
          ],
      ),
      migrations.CreateModel(
          name='Annotation',
          fields=[
              ('id', models.AutoField(auto_created=True,
                                      primary_key=True, serialize=False, verbose_name='ID')),
              ('date', models.DateTimeField(auto_now_add=True)),
              ('session', models.CharField(default='s00', max_length=3)),
              ('ann_cat', models.CharField(default='M', max_length=1)),
              ('refexp', models.CharField(max_length=700)),
              ('latitude', models.FloatField()),
              ('longitude', models.FloatField()),
          ],
      ),
      migrations.CreateModel(
          name='Feedback',
          fields=[
              ('date', models.DateTimeField(auto_now_add=True)),
              ('feedback_text', models.CharField(
                  max_length=50, primary_key=True, serialize=False)),
              ('feedback_detail', models.CharField(max_length=10000)),
              ('validation', models.IntegerField()),
          ],
      ),
      migrations.CreateModel(
          name='Image',
          fields=[
              ('date', models.DateTimeField(auto_now_add=True)),
              ('imageurl', models.URLField(primary_key=True, serialize=False)),
          ],
      ),
      migrations.CreateModel(
          name='Turker',
          fields=[
              ('date', models.DateTimeField(auto_now_add=True)),
              ('turkerid', models.CharField(
                  max_length=100, primary_key=True, serialize=False)),
          ],
      ),
      migrations.AddField(
          model_name='annotation',
          name='feedback',
          field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                  related_name='annotations', to='catalog.Feedback'),
      ),
      migrations.AddField(
          model_name='annotation',
          name='image',
          field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                  related_name='annotations', to='catalog.Image'),
      ),
      migrations.AddField(
          model_name='annotation',
          name='turker',
          field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                  related_name='annotations', to='catalog.Turker'),
      ),
      migrations.AddField(
          model_name='actions',
          name='annotation',
          field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                  related_name='actions', to='catalog.Annotation'),
      ),
      migrations.AddField(
          model_name='actions',
          name='feedback',
          field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                  related_name='actions', to='catalog.Feedback'),
      ),
      migrations.AddField(
          model_name='actions',
          name='turker',
          field=models.ForeignKey(
              on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='catalog.Turker'),
      ),
  ]
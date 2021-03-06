# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-01-23 19:09
from __future__ import unicode_literals

from django.db import migrations


def create_initial_annotations(apps, schema_editor):
  Image = apps.get_model('catalog', 'Image')

  image4 = Image(
      imageurl='https://s3.amazonaws.com/refer360javascript/pano_test/pano_agcipzbgtgisoi.jpg')

  image5 = Image(
      imageurl='https://s3.amazonaws.com/refer360javascript/pano_test/pano_azqpvcqkquhudq.jpg')
  image5.save()

  image6 = Image(
      imageurl='https://s3.amazonaws.com/refer360javascript/pano_test/pano_atikcwhwilslkl.jpg')
  image6.save()

  image7 = Image(
      imageurl='https://s3.amazonaws.com/refer360javascript/pano_test/pano_akojetqaokgbhk.jpg')
  image7.save()


class Migration(migrations.Migration):

  initial = False
  dependencies = [('catalog', '0001_initial'), ]
  operations = [
      migrations.RunPython(create_initial_annotations),

  ]

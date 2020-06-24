from __future__ import unicode_literals
from django.db import models
from datetime import datetime


class Image(models.Model):
  date = models.DateTimeField(auto_now_add=True)

  imageurl = models.URLField(primary_key=True)


class Turker(models.Model):
  date = models.DateTimeField(auto_now_add=True)

  turkerid = models.CharField(primary_key=True, max_length=100)


class Feedback(models.Model):
  date = models.DateTimeField(auto_now_add=True)

  feedback_text = models.CharField(
      primary_key=True, max_length=50, null=False)
  feedback_detail = models.CharField(max_length=10000)
  validation = models.IntegerField()


class Annotation(models.Model):
  date = models.DateTimeField(auto_now_add=True)
  ann_rnd = models.CharField(default='r00', max_length=3)  # Verification Round
  session = models.CharField(default='s00', max_length=3)  #
  ann_cat = models.CharField(default='M', max_length=1)  # (M)anual or (R)andom
  refexp = models.CharField(max_length=700)
  latitude = models.FloatField()
  longitude = models.FloatField()
  image = models.ForeignKey(Image, related_name='annotations')
  turker = models.ForeignKey(Turker, related_name='annotations')
  feedback = models.ForeignKey(Feedback, related_name='annotations')

  @property
  def imageurl(self):
    return self.image.imageurl

  @property
  def turkerid(self):
    return self.turker.turkerid

  @property
  def feedback_text(self):
    return self.feedback.feedback_text

  @property
  def annotationid(self):
    return self.id


class Actions(models.Model):
  date = models.DateTimeField(auto_now_add=True)

  action_list = models.CharField(max_length=100000)
  pred_latitude = models.FloatField()
  pred_longitude = models.FloatField()

  start_latitude = models.FloatField()
  start_longitude = models.FloatField()

  turker = models.ForeignKey(Turker, related_name='actions')
  annotation = models.ForeignKey(Annotation, related_name='actions')
  feedback = models.ForeignKey(Feedback, related_name='actions')
  session = models.CharField(default='s00', max_length=3)  #
  ann_cat = models.CharField(default='M', max_length=1)  # Easy Medium Hard Bad
  ann_clr = models.CharField(default='C', max_length=1)

  @property
  def turkerid(self):
    return self.turker.turkerid

  @property
  def actionid(self):
    return self.id

  @property
  def annotationid(self):
    return self.annotation.id

  @property
  def refexp(self):
    return self.annotation.refexp

  @property
  def imageurl(self):
    return self.annotation.imageurl

  @property
  def gt_latitude(self):
    return self.annotation.latitude

  @property
  def gt_longitude(self):
    return self.annotation.longitude

  @property
  def feedback_text(self):
    return self.feedback.feedback_text


class Reviews(models.Model):
  date = models.DateTimeField(auto_now_add=True)
  category_list = models.CharField(max_length=100000)
  annotation = models.ForeignKey(Annotation, related_name='reviews')
  turker = models.ForeignKey(Turker, related_name='review')
  session = models.CharField(default='c00', max_length=3)

  @property
  def turkerid(self):
    return self.turker.turkerid

  @property
  def reviewid(self):
    return self.id

  @property
  def annotationid(self):
    return self.annotation.id

  @property
  def refexp(self):
    return self.annotation.refexp

  @property
  def imageurl(self):
    return self.annotation.imageurl

  @property
  def gt_latitude(self):
    return self.annotation.latitude

  @property
  def gt_longitude(self):
    return self.annotation.longitude

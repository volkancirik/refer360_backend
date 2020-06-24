from .models import Annotation, Image, Turker, Feedback, Actions, Reviews
from rest_framework import serializers


class ActionsForAnnSerializer(serializers.ModelSerializer):
  turkerid = serializers.ReadOnlyField()

  class Meta:
    model = Actions
    fields = ('action_list', 'pred_latitude', 'pred_longitude',
              'ann_cat', 'ann_clr', 'turkerid', 'annotationid', 'date', 'actionid', 'session')


class AnnotationSerializer(serializers.ModelSerializer):
  imageurl = serializers.ReadOnlyField()
  turkerid = serializers.ReadOnlyField()
  feedback_text = serializers.ReadOnlyField(
      required=False, allow_null=True)
  actions = ActionsForAnnSerializer(many=True, read_only=True)
  follow_count = serializers.SerializerMethodField()

  def get_follow_count(self, annotation):
    return Actions.objects.filter(annotation=annotation).count()

  class Meta:
    model = Annotation
    fields = ('imageurl', 'turkerid', 'refexp',
              'latitude', 'longitude', 'feedback_text', 'actions', 'follow_count', 'annotationid', 'ann_cat', 'ann_rnd', 'session', 'date',)


class AnnotationShallowSerializer(serializers.ModelSerializer):
  imageurl = serializers.ReadOnlyField()
  follows_count = serializers.SerializerMethodField()

  def get_follows_count(self, annotation):
    return Actions.objects.filter(annotation=annotation).count()

  class Meta:
    model = Annotation
    fields = ('imageurl', 'follows_count', 'refexp', 'latitude',
              'longitude', 'annotationid', 'session', 'date')


class TurkerShallowSerializer(serializers.ModelSerializer):
  class Meta:
    model = Turker
    fields = ('turkerid',)


class TurkerSerializer(serializers.ModelSerializer):
  annotations = AnnotationSerializer(many=True, read_only=True)
  actions = ActionsForAnnSerializer(many=True, read_only=True)

  class Meta:
    model = Turker
    fields = ('turkerid', 'annotations', 'actions', 'date')


class ImageShallowSerializer(serializers.ModelSerializer):

  annotations_count = serializers.SerializerMethodField()
  follows_count = serializers.SerializerMethodField()

  def get_follows_count(self, image):
    return Actions.objects.filter(annotation__image=image).count()

  def get_annotations_count(self, image):
    return Annotation.objects.filter(image=image).count()

  class Meta:
    model = Image
    fields = ('imageurl', 'annotations_count', 'follows_count', 'date')


class ImageSerializer(serializers.ModelSerializer):
  annotations = AnnotationSerializer(many=True, read_only=True)

  annotations_count = serializers.SerializerMethodField()
  follows_count = serializers.SerializerMethodField()

  def get_follows_count(self, image):
    return Actions.objects.filter(annotation__image=image).count()

  def get_annotations_count(self, image):
    return Annotation.objects.filter(image=image).count()

  class Meta:
    model = Image
    fields = ('imageurl', 'annotations_count',
              'follows_count', 'annotations', 'date')


class FeedbackShallowSerializer(serializers.ModelSerializer):
  class Meta:
    model = Feedback
    fields = ('feedback_text', 'feedback_detail', 'validation',
              'date')


class FeedbackSerializer(serializers.ModelSerializer):
  annotations = AnnotationSerializer(many=True, read_only=True)
  actions = ActionsForAnnSerializer(many=True, read_only=True)

  class Meta:
    model = Feedback
    fields = ('feedback_text', 'feedback_detail', 'validation',
              'annotations', 'actions', 'date')


class ActionsShallowSerializer(serializers.ModelSerializer):

  turkerid = serializers.ReadOnlyField()

  class Meta:
    model = Actions
    fields = ('action_list', 'pred_latitude',
              'start_latitude', 'start_longitude',
              'pred_longitude', 'turkerid', 'feedback_text', 'ann_cat', 'ann_clr',
              'actionid,' 'date')


class ActionsSerializer(serializers.ModelSerializer):
  turkerid = serializers.ReadOnlyField()
  annotationid = serializers.ReadOnlyField()
  refexp = serializers.ReadOnlyField()
  imageurl = serializers.ReadOnlyField()
  gt_latitude = serializers.ReadOnlyField()
  gt_longitude = serializers.ReadOnlyField()
  turkerid = serializers.ReadOnlyField()
  feedback_text = serializers.ReadOnlyField(
      required=False, allow_null=True)

  class Meta:
    model = Actions
    fields = ('action_list', 'turkerid', 'annotationid',
              'refexp', 'imageurl', 'gt_latitude', 'gt_longitude',
              'pred_latitude', 'pred_longitude',
              'start_latitude', 'start_longitude',
              'ann_cat', 'ann_clr',
              'turkerid', 'feedback_text', 'actionid', 'session', 'date',)


class ReviewsSerializer(serializers.ModelSerializer):
  turkerid = serializers.ReadOnlyField()
  annotationid = serializers.ReadOnlyField()
  refexp = serializers.ReadOnlyField()
  imageurl = serializers.ReadOnlyField()
  gt_latitude = serializers.ReadOnlyField()
  gt_longitude = serializers.ReadOnlyField()
  turkerid = serializers.ReadOnlyField()

  class Meta:
    model = Reviews
    fields = ('category_list', 'turkerid', 'annotationid',
              'refexp', 'imageurl', 'gt_latitude', 'gt_longitude',
              'reviewid', 'session', 'date')

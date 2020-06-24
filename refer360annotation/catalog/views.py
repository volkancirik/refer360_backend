import json
from rest_framework import generics, permissions

from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from rest_framework import status
from .models import Annotation, Image, Turker
from .serializers import AnnotationSerializer, AnnotationShallowSerializer
from .serializers import ImageSerializer, ImageShallowSerializer
from .serializers import TurkerSerializer, TurkerShallowSerializer

from .models import Feedback
from .serializers import FeedbackSerializer, FeedbackShallowSerializer
from .models import Actions
from .serializers import ActionsSerializer
from .models import Reviews
from .serializers import ReviewsSerializer

from random import choice, uniform

import string
from django.utils import timezone
from django.db.models import Count


def new_feedback(self, feedback_text=''):
  if not feedback_text:
    feedback_text = "".join(
        [choice(string.letters) for i in xrange(50)])
  feedback = Feedback(feedback_text=feedback_text,
                      date=timezone.now(), validation=0)
  feedback.save()
  return feedback


class IsCreationOrIsAuthenticated(permissions.BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated():
      if request.method == 'POST':
        return True
      else:
        return False
    else:
      return True


class AnnotationList(generics.ListCreateAPIView):
  permission_classes = [IsCreationOrIsAuthenticated]
  queryset = Annotation.objects.all()
  serializer_class = AnnotationSerializer
  print('AnnotationList(): Total # of annotations:', len(queryset))

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    res_dict = self.perform_create(serializer)

    turkerid = request.data['turkerid']
    imagelist = Image.objects.exclude(annotations__turker=turkerid).values_list(
        'pk', flat=True).order_by('imageurl')

    random_pk = choice(imagelist)
    image = Image.objects.get(pk=random_pk)
    serializer = ImageShallowSerializer(image)

    d = serializer.data
    d['new_annotation'] = res_dict['identifier']
    d['feedback_text'] = res_dict['feedback_text']
    return Response(d)

  def perform_create(self, serializer):

    imagelist = Image.objects.filter(imageurl=self.request.data['imageurl'])
    turkerid = self.request.data['turkerid']

    if self.request.data['feedback_text'] == '':
      feedback = new_feedback('')
    else:
      feedbacklist = Feedback.objects.filter(
          feedback_text=self.request.data['feedback_text'])
      if not len(feedbacklist):
        feedback = new_feedback(self.request.data['feedback_text'])
      else:
        feedback = feedbacklist[0]

    feedback.validation = feedback.validation + 1
    feedback.save()

    identifier = 0
    if len(imagelist):
      image = imagelist[0]

      turkerlist = Turker.objects.filter(
          turkerid=self.request.data['turkerid'])
      # if there is no such turker create one
      if len(turkerlist) > 0:
        turker = turkerlist[0]
      else:
        turker = Turker(turkerid=turkerid, date=timezone.now())
        turker.save()
      ann = serializer.save(image=image, turker=turker,
                            feedback=feedback, date=timezone.now())
      identifier = ann.id
    return {"identifier": identifier, "feedback_text": feedback.feedback_text}


class ImageDetail(APIView):
  permission_classes = [IsCreationOrIsAuthenticated]

  def get_object(self, suffix, prefix='https://s3.amazonaws.com/refer360/sun360images_4552x2276/pano_'):
    try:
      return Image.objects.get(imageurl=prefix + suffix + '.jpg')
    except Image.DoesNotExist:
      raise Http404

  def get(self, request, suffix, format=None):
    image = self.get_object(suffix)
    serializer = ImageSerializer(image)
    return Response(serializer.data)

  def put(self, request, suffix, format=None):
    image = self.get_object(suffix)
    serializer = ImageSerializer(image, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, suffix, format=None):
    image = self.get_object(suffix)
    image.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class ChangeRound(APIView):
  permission_classes = [IsCreationOrIsAuthenticated]

  def get(self, request, *args, **kwargs):
    annotationid = self.kwargs['annotationid']
    ann_rnd = self.kwargs['round']

    annotation = Annotation.objects.get(pk=annotationid)
    annotation.ann_rnd = ann_rnd
    annotation.save()
    serializer = AnnotationSerializer(annotation)
    return Response(serializer.data)


class ImageList(generics.ListCreateAPIView):
  permission_classes = [IsCreationOrIsAuthenticated]
  queryset = Image.objects.all()
  serializer_class = ImageSerializer
  print('ImageList(): Total # of Images:', len(queryset))

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    res_dict = self.perform_create(serializer)

    return Response(res_dict)

  def perform_create(self, serializer):

    imagelist = Image.objects.filter(imageurl=self.request.data['imageurl'])
    if len(imagelist):
      return {'message': 'image {} is already there!'.format(self.request.data['imageurl'])}
    else:
      image = Image(
          imageurl=self.request.data['imageurl'], date=timezone.now())
      image.save()
      return {"message": 'image added successfuly!'}


class TurkerList(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated, ]
  queryset = Turker.objects.all().distinct()
  print('TurkerList(): Total # of turkers:', len(queryset))
  serializer_class = TurkerSerializer
  lookup_field = 'turkerid'


# class CleanTurkerList(generics.ListAPIView):
#   permission_classes = [permissions.IsAuthenticated, ]
#   before_queryset = Turker.objects.all()
#   print('CleanTurkerList() before total # of turkers:', len(before_queryset))
#   delete_queryset = Turker.objects.annotate(follows=Count('actions')).annotate(
#       annotates=Count('annotations')).filter(follows__lte=1).filter(annotates__lte=0).delete()
#   queryset = Turker.objects.all()
#   print('CleanTurkerList() after total # of turkers:', len(queryset))
#   serializer_class = TurkerSerializer
#   lookup_field = 'turkerid'


class FeedbackDetail(APIView):
  permission_classes = [permissions.IsAuthenticated, ]
  queryset = Annotation.objects.all()
  serializer_class = AnnotationSerializer

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    res_dict = self.perform_create(serializer)

    turkerid = request.data['turkerid']
    imagelist = Image.objects.exclude(annotations__turker=turkerid).values_list(
        'pk', flat=True).order_by('imageurl')

    random_pk = choice(imagelist)
    image = Image.objects.get(pk=random_pk)
    serializer = ImageShallowSerializer(image)

    d = serializer.data
    d['new_annotation'] = res_dict['identifier']
    d['feedback_text'] = res_dict['feedback_text']
    return Response(d)

  def perform_create(self, serializer):

    imagelist = Image.objects.filter(imageurl=self.request.data['imageurl'])
    turkerid = self.request.data['turkerid']

    if self.request.data['feedback_text'] == '':
      feedback = new_feedback('')
    else:
      feedbacklist = Feedback.objects.filter(
          feedback_text=self.request.data['feedback_text'])
      if not len(feedbacklist):
        feedback = new_feedback(self.request.data['feedback_text'])
      else:
        feedback = feedbacklist[0]

    feedback.validation = feedback.validation + 1
    feedback.save()

    identifier = 0
    if len(imagelist):
      image = imagelist[0]

      turkerlist = Turker.objects.filter(
          turkerid=self.request.data['turkerid'])
      # if there is no such turker create one
      if len(turkerlist) > 0:
        turker = turkerlist[0]
      else:
        turker = Turker(turkerid=turkerid, date=timezone.now())
        turker.save()
      ann = serializer.save(image=image, turker=turker,
                            feedback=feedback, date=timezone.now())
      identifier = ann.id
    return {"identifier": identifier, "feedback_text": feedback.feedback_text}


class FeedbackList(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated]
  queryset = Feedback.objects.all()
  serializer_class = FeedbackSerializer
  lookup_field = 'feedback_text'


class TurkerShallowList(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated, ]

  def get_object(self, pk):
    try:
      return Feedback.objects.get(feedback_text=pk)
    except Feedback.DoesNotExist:
      raise Http404

  def get(self, request, pk, format=None):
    feedback = self.get_object(pk)
    serializer = FeedbackSerializer(feedback)
    return Response(serializer.data)

  def put(self, request, pk, format=None):
    feedback = self.get_object(pk)
    serializer = FeedbackSerializer(
        feedback, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pk, format=None):
    feedback = self.get_object(pk)
    feedback.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class ValidatePassphrase(APIView):

  def get_object(self, pk):
    try:
      return Feedback.objects.get(feedback_text=pk)
    except Feedback.DoesNotExist:
      pass
    return 3  # NOT EXIST

  def get(self, request, *args, **kwargs):  # request, pk, format=None):

    pk = self.kwargs['pk']
    explanation = {0: "incomplete",
                   1: "validated now",
                   2: "already used",
                   3: "other error"}
    constraints = {'annotation': 4,
                   'validation': 10}

    if 'constraint' in self.kwargs:
      constraint = self.kwargs['constraint']
    else:
      constraint = 'annotation'
    max_val = constraints[constraint]
    feedback_obj = self.get_object(pk)
    if type(feedback_obj) == type(3):
      return Response({"validation": 3, "explanation": "does not exist!"})

    feedback = FeedbackShallowSerializer(feedback_obj)
    feedback_validation = feedback.data["validation"]
    if feedback_validation == max_val:  # Validate NOW!
      validation = 1
      serializer = FeedbackShallowSerializer(
          feedback_obj, data={"validation": -1}, partial=True)
      if serializer.is_valid():
        serializer.save()
    elif 0 <= feedback_validation < max_val+1:  # INCOMPLETE
      validation = 0
    elif feedback_validation == -1:  # ALREADY USED!
      validation = 2
    else:
      validation = 3  # UNKNOWN or NOT EXIST
    print('RESPONSE FOR VALIDATION OF {} >>> {} , value {} CONSTRAINT was {} MAX_VAL was {}'.format(
        pk, validation, feedback_validation, constraint, max_val))

    return Response({"validation": validation, "explanation": explanation[validation]})


class AnnotationUnfollowed(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated, ]
  queryset = Annotation.objects.all()
  print('AnnotationUnfollowed(): Total # of annotations:', len(queryset))
  serializer_class = AnnotationSerializer

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    res_dict = self.perform_create(serializer)

    turkerid = request.data['turkerid']
    imagelist = Image.objects.exclude(annotations__turker=turkerid).values_list(
        'pk', flat=True).order_by('imageurl')

    random_pk = choice(imagelist)
    image = Image.objects.get(pk=random_pk)
    serializer = ImageShallowSerializer(image)

    d = serializer.data
    d['new_annotation'] = res_dict['identifier']
    d['feedback_text'] = res_dict['feedback_text']
    return Response(d)

  def perform_create(self, serializer):

    imagelist = Image.objects.filter(imageurl=self.request.data['imageurl'])
    turkerid = self.request.data['turkerid']

    if self.request.data['feedback_text'] == '':
      feedback = new_feedback('')
    else:
      feedbacklist = Feedback.objects.filter(
          feedback_text=self.request.data['feedback_text'])
      if not len(feedbacklist):
        feedback = new_feedback(self.request.data['feedback_text'])
      else:
        feedback = feedbacklist[0]

    feedback.validation = feedback.validation + 1
    feedback.save()

    identifier = 0
    if len(imagelist):
      image = imagelist[0]

      turkerlist = Turker.objects.filter(
          turkerid=self.request.data['turkerid'])
      # if there is no such turker create one
      if len(turkerlist) > 0:
        turker = turkerlist[0]
      else:
        turker = Turker(turkerid=turkerid, date=timezone.now())
        turker.save()
      ann = serializer.save(image=image, turker=turker,
                            feedback=feedback, date=timezone.now())
      identifier = ann.id
    return {"identifier": identifier, "feedback_text": feedback.feedback_text}


class AnnotationDetail(APIView):
  permission_classes = [permissions.IsAuthenticated, ]

  def get_object(self, pk):
    try:
      return Annotation.objects.get(pk=pk)
    except Annotation.DoesNotExist:
      raise Http404

  def get(self, request, pk, format=None):
    annotation = self.get_object(pk)
    serializer = AnnotationSerializer(annotation)
    return Response(serializer.data)

  def put(self, request, pk, format=None):
    annotation = self.get_object(pk)
    serializer = AnnotationSerializer(
        annotation, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pk, format=None):
    annotation = self.get_object(pk)
    annotation.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class TurkerDetail(APIView):
  permission_classes = [permissions.IsAuthenticated, ]

  def get_object(self, turkerid):
    try:
      return Turker.objects.get(turkerid=turkerid)
    except Turker.DoesNotExist:
      raise Http404

  def get(self, request, *args, **kwargs):
    turkerid = kwargs['turkerid']

    if 'session' in kwargs:
      d = {}
      session = kwargs['session']
      d['turkerid'] = turkerid
      d['annotations'] = len(
          Annotation.objects.filter(turker=turkerid, session=session))
      d['actions'] = len(
          Actions.objects.filter(turker=turkerid, session=session))
    else:
      turker = self.get_object(turkerid)
      serializer = TurkerSerializer(turker)
      d = serializer.data

      sessions = ['s00', 's01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09',
                  's10', 's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19']

      d['sessions'] = {'annotations': {}, 'actions': {}}
      for session in sessions:
        d['sessions']['annotations'][session] = len(
            Annotation.objects.filter(turker=turkerid, session=session))

      for session in sessions:
        d['sessions']['actions'][session] = len(
            Actions.objects.filter(turker=turkerid, session=session))

      d['reviews'] = len(
          Reviews.objects.filter(turker=turkerid))

    return Response(d)

  def put(self, request, turkerid, format=None):
    turker = self.get_object(turkerid)
    serializer = TurkerSerializer(
        turker, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, turkerid, format=None):
    turker = self.get_object(turkerid)
    turker.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class TurkerRank(APIView):
  permission_classes = [permissions.IsAuthenticated, ]

  def get_object(self, turkerid):
    try:
      return Turker.objects.get(turkerid=turkerid)
    except Turker.DoesNotExist:
      raise Http404

  def get(self, request, turkerid, session, format=None):
    turker = self.get_object(turkerid)
    serializer = TurkerSerializer(turker)
    d = serializer.data

    sessions = ['s00', 's01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09',
                's10', 's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19']

    d['sessions'] = {}
    for session in sessions:
      d['sessions'][session] = len(
          Annotation.objects.filter(turker=turkerid, session=session))

    return Response(d)

  def put(self, request, turkerid, format=None):
    turker = self.get_object(turkerid)
    serializer = TurkerSerializer(
        turker, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, turkerid, format=None):
    turker = self.get_object(turkerid)
    turker.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class RandomImage(APIView):
  def get(self, _):
    pks = Image.objects.values_list('pk', flat=True).order_by('imageurl')
    random_pk = choice(pks)
    image = Image.objects.get(pk=random_pk)
    serializer = ImageShallowSerializer(image)
    return Response(serializer.data)


class RandomLocationImage(APIView):
  def get(self, request, turkerid, format=None):

    imagelist = Image.objects.exclude(annotations__turker=turkerid).values_list(
        'pk', flat=True).order_by('imageurl')
    random_pk = choice(imagelist)
    image = Image.objects.get(pk=random_pk)
    serializer = ImageShallowSerializer(image)
    d = serializer.data
    d["latitude"] = uniform(0, 6.25)
    d["longitude"] = uniform(-0.8, 0.5)
    return Response(d)

  def delete(self, request, suffix, format=None):
    image = self.get_object(suffix)
    image.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class ImageListByCategory(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = ImageSerializer

  def get_queryset(self):
    category = self.kwargs['category']
    return Image.objects.filter(imageurl__contains=category)


class ImageStatsByCategories(APIView):
  permission_classes = [permissions.IsAuthenticated, ]
  def get(self, request, category, format=None):

    imagelist = Image.objects.filter(imageurl__contains=category).values_list(
        'pk', flat=True).order_by('imageurl')

    d = {'category': category, 'num_images': len(imagelist)}
    return Response(d)


class AnnotationByCategory(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = AnnotationSerializer

  def get_queryset(self):
    ann_cat = self.kwargs['ann_cat']
    filtered = Annotation.objects.filter(ann_cat=ann_cat)
    print('AnnotationByCategory {} {}'.format(ann_cat, len(filtered)))
    return filtered


class AnnotationBySession(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = AnnotationSerializer

  def get_queryset(self):
    session = self.kwargs['session']
    filtered = Annotation.objects.filter(session=session)
    print('AnnotationBySession {} {}'.format(session, len(filtered)))
    return filtered


class AnnotationByRound(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = AnnotationSerializer

  def get_queryset(self):
    rounds = self.kwargs['round'].split('|')
    filtered = Annotation.objects.filter(ann_rnd__in=rounds)
    print('AnnotationByRound {} {}'.format(rounds, len(filtered)))
    return filtered


class ImageAllCategories(APIView):
  permission_classes = [permissions.IsAuthenticated]
  def get(self, request, format=None):

    d = {'indoor': {'total': 0},
         'outdoor': {'total': 0},
         'total': 0,
         'in_db': 0}
    indoor_categories = ['restaurant',
                         'bedroom',
                         'shop',
                         'expo_showroom',
                         'living_room']
    outdoor_categories = ['plaza_courtyard',
                          'street',
                          'field']
    for v, category_list in zip(['indoor', 'outdoor'], [indoor_categories, outdoor_categories]):
      for c in category_list:
        count = len(Image.objects.filter(imageurl__contains=c).values_list(
            'pk', flat=True).order_by('imageurl'))
        d[v][c] = count
        d[v]['total'] += d[v][c]
        d['total'] += d[v][c]

    d['in_db'] = len(Image.objects.all())
    self.check_object_permissions(self.request, d)
    return Response(d)


class TurkersBySession(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = TurkerShallowSerializer

  def get_queryset(self):
    session = self.kwargs['session']
    task = self.kwargs['task']
    if task == 'annotation':
      return Turker.objects.filter(annotations__session=session).distinct()
    else:
      return Turker.objects.filter(actions__session=session).distinct()


class TurkersStat(APIView):
  permission_classes = [permissions.IsAuthenticated]
  def get(self, request, format=None):

    d = {}
    n_turkers = len(Turker.objects.all().distinct())
    d['n_turkers'] = n_turkers
    self.check_object_permissions(self.request, d)
    return Response(d)


class SessionsStat(APIView):
  permission_classes = [permissions.IsAuthenticated]
  def get(self, request, format=None):

    d = {}
    sessions = ['s00', 's01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09',
                's10', 's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19']
    total_actions = 0
    total_annotations = 0
    for session in sessions:
      d[session] = {}
      n_instances = len(Annotation.objects.filter(session=session))
      d[session]['annotations'] = n_instances
      total_annotations += n_instances

      n_instances = len(Actions.objects.filter(session=session))
      d[session]['actions'] = n_instances
      total_actions += n_instances

      n_turkers = len(Turker.objects.filter(
          annotations__session=session).distinct().order_by('turkerid'))
      d[session]['turkers'] = n_turkers
    d['total_annotations'] = total_annotations
    d['total_actions'] = total_actions

    self.check_object_permissions(self.request, d)
    return Response(d)


class NextTurker(APIView):
  # permission_classes = [permissions.IsAuthenticated]
  serializer_class = AnnotationShallowSerializer
  def get(self, request, *args, **kwargs):

    session = self.kwargs['session']
    order = int(self.kwargs['order'])
    reviewerid = self.kwargs['reviewerid']

    turkers = Turker.objects.filter(
        annotations__session=session).distinct().order_by('turkerid')
    if order >= len(turkers) or reviewerid not in ['nicki']:
      print('NextTurker() failed to return review items',
            order >= len(turkers), reviewerid not in ['nicki'])
      return Response({'imageurl': ''})
    print('NextTurker() # of  review items', len(turkers))

    turker = turkers[order]
    nturkers = len(turkers)
    annotationlist = Annotation.objects.filter(
        turker_id=turker).values_list('pk', flat=True)
    random_pk = choice(annotationlist)
    annotation = Annotation.objects.get(pk=random_pk)
    serializer = AnnotationShallowSerializer(annotation)
    d = serializer.data
    url = d['imageurl']
    imageid = '_'.join(url.split('/')[-1].split('.')[0].split('_')[1:])
    d['link'] = 'https://vulcan.multicomp.cs.cmu.edu:9001/images/'+imageid
    d['nturkers'] = nturkers
    d['turker'] = turker.turkerid
    return Response(d)


class NextImage(APIView):
  def get(self, request, turkerid, format=None):

    # imagelist = Image.objects.exclude(annotations__turker=turkerid).values_list('pk', flat=True).order_by('imageurl')
    imagelist = Image.objects.annotate(numannotations=Count('annotations')).all().annotate(numfollows=Count('annotations__actions')).all().exclude(
        annotations__turker=turkerid).exclude(numannotations__gte=10).exclude(numfollows__gte=10).values_list('pk', flat=True).order_by('imageurl')

    random_pk = choice(imagelist)
    image = Image.objects.get(pk=random_pk)

    print('NextImage():', turkerid,
          '<--describe-nextimage()--', random_pk)
    serializer = ImageShallowSerializer(image)
    return Response(serializer.data)


class NextFollowImage(APIView):
  #  def get(self, request, turkerid, format=None):
  def get(self, request, *args, **kwargs):
    turkerid = self.kwargs['turkerid']

    if 'round' in self.kwargs:
      # ann_rnd = self.kwargs['round']
      # annotationlist = Annotation.objects.exclude(turker_id=turkerid).exclude(
      #     turker_id="onboarding").exclude(
      #     turker_id="vcirik").exclude(
      #     turker_id="nicki").exclude(
      #     turker_id="demo").exclude(
      #     turker_id="A1QFJ9QG6U0A31").exclude(
      #     turker_id="A3HO7SJ2EG6JJF").values_list('pk', flat=True).exclude(
      #     actions__turker=turkerid).filter(ann_rnd=ann_rnd)
      ann_rnds = self.kwargs['round'].split('|')
      annotationlist = Annotation.objects.exclude(turker_id=turkerid).exclude(
          turker_id="onboarding").exclude(
          turker_id="vcirik").exclude(
          turker_id="nicki").exclude(
          turker_id="demo").exclude(
          turker_id="A1QFJ9QG6U0A31").exclude(
          turker_id="A3HO7SJ2EG6JJF").values_list('pk', flat=True).exclude(
          actions__turker=turkerid).filter(ann_rnd__in=ann_rnds)

      if len(annotationlist) == 0 and ann_rnds[0][0] in ['c', 'v']:
        annotationlist = Annotation.objects.exclude(turker_id=turkerid).exclude(
            turker_id="onboarding").exclude(
            turker_id="vcirik").exclude(
            turker_id="nicki").exclude(
            turker_id="demo").exclude(
            turker_id="A1QFJ9QG6U0A31").exclude(
            turker_id="A3HO7SJ2EG6JJF").values_list('pk', flat=True).exclude(
            actions__turker=turkerid).annotate(numfollows=Count('actions')).all().exclude(numfollows__gte=2)
        print('HERE1:', len(annotationlist))
    else:
      annotationlist = Annotation.objects.exclude(turker_id=turkerid).exclude(
          turker_id="onboarding").exclude(
          turker_id="vcirik").exclude(
          turker_id="nicki").exclude(
          turker_id="demo").exclude(
          turker_id="A1QFJ9QG6U0A31").exclude(
          turker_id="A3HO7SJ2EG6JJF").values_list('pk', flat=True).exclude(
          actions__turker=turkerid).annotate(numfollows=Count('actions')).all().exclude(numfollows__gte=2)

    print('HERE2:', len(annotationlist))
    random_pk = choice(annotationlist)
    annotation = Annotation.objects.get(pk=random_pk)
    serializer = AnnotationShallowSerializer(annotation)
    print('{} NextFollowImage():'.format(len(annotationlist)), turkerid,
          '<--follow-nextfollowimage()--', random_pk)
    d = serializer.data
    url = d['imageurl']
    # d['refexp'] = d['refexp'].replace('\n', '')
    imageid = '_'.join(url.split('/')[-1].split('.')[0].split('_')[1:])
    d['link'] = 'https://vulcan.multicomp.cs.cmu.edu:9001/images/'+imageid
    return Response(d)


class LeaderBoard(APIView):
  def get(self, request, turkerid, format=None):

    leaderboard = json.load(open('../data/leaderboard.json', 'r'))
    d = {'describing': {}, 'finding': {}}
    for session in leaderboard['describing']:
      if turkerid in leaderboard['describing'][session]:
        d['describing'][session] = leaderboard['describing'][session][turkerid]
    for session in leaderboard['finding']:
      if turkerid in leaderboard['finding'][session]:
        d['finding'][session] = leaderboard['finding'][session][turkerid]

    return Response(d)


class Onboarding(APIView):
  def get(self, request, turkerid, format=None):
    from django.db.models import Count

    annotationlist = Annotation.objects.annotate(follows=Count('actions')).all().exclude(
        turker_id="onboarding").exclude(
        turker_id="vcirik").exclude(
        turker_id="nicki").exclude(
        turker_id="demo").exclude(
        turker_id="A1QFJ9QG6U0A31").exclude(
        turker_id="A3HO7SJ2EG6JJF").exclude(follows__gte=1).values_list('pk', flat=True).exclude(actions__turker=turkerid)

    if not len(annotationlist):
      return Response({"imageurl": ""})
    random_pk = choice(annotationlist)
    annotation = Annotation.objects.get(pk=random_pk)
    serializer = AnnotationShallowSerializer(annotation)

    return Response(serializer.data)


class ActionsDetail(APIView):
  permission_classes = [permissions.IsAuthenticated, ]

  def get_object(self, pk):
    try:
      return Actions.objects.get(pk=pk)
    except Actions.DoesNotExist:
      raise Http404

  def get(self, request, pk, format=None):

    actions = self.get_object(pk)
    serializer = ActionsSerializer(actions)
    return Response(serializer.data)

  def put(self, request, pk, format=None):

    actions = self.get_object(pk)
    serializer = ActionsSerializer(
        actions, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pk, format=None):
    actions = self.get_object(pk)
    actions.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class ActionsList(generics.ListCreateAPIView):
  permission_classes = [IsCreationOrIsAuthenticated]
  queryset = Actions.objects.all()
  serializer_class = ActionsSerializer

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if 'round' in kwargs:
      ann_rnd = list(self.kwargs['round'])
      ann_rnd[0] = 'd'
      ann_rnd = ''.join(ann_rnd)
    else:
      ann_rnd = None
    res_dict = self.perform_create(serializer, ann_rnd)

    turkerid = request.data['turkerid']

    # exclude previously followed annotations or annotations by this turker
    annotationlist = Annotation.objects.exclude(turker_id=turkerid).exclude(
        turker_id="onboarding").exclude(
        turker_id="vcirik").exclude(
        turker_id="nicki").exclude(
        turker_id="demo").exclude(
        turker_id="A1QFJ9QG6U0A31").exclude(
        turker_id="A3HO7SJ2EG6JJF").values_list(
        'pk', flat=True).exclude(actions__turker=turkerid)

    random_pk = choice(annotationlist)
    annotation = Annotation.objects.get(pk=random_pk)
    serializer = AnnotationShallowSerializer(annotation)

    d = serializer.data
    d['new_actions'] = res_dict['identifier']
    d['feedback_text'] = res_dict['feedback_text']

    if 'round' in kwargs:
      feedback = Feedback.objects.get(
          feedback_text=d['feedback_text'])
      feedback.validation = feedback.validation + 1
      feedback.save()

    return Response(d)

  def perform_create(self, serializer, ann_rnd=None):

    annotation = Annotation.objects.get(pk=self.request.data['annotationid'])
    if ann_rnd:
      annotation.ann_rnd = ann_rnd
      annotation.save()
    turkerid = self.request.data['turkerid']

    identifier = 0
    turkerlist = Turker.objects.filter(
        turkerid=self.request.data['turkerid'])
    # if there is no such turker create one
    if len(turkerlist) > 0:
      turker = turkerlist[0]
    else:
      turker = Turker(turkerid=turkerid, date=timezone.now())
      turker.save()

    if self.request.data['feedback_text'] == '':
      feedback = new_feedback('')
    else:
      feedbacklist = Feedback.objects.filter(
          feedback_text=self.request.data['feedback_text'])
      if not len(feedbacklist):
        feedback = new_feedback(self.request.data['feedback_text'])
      else:
        feedback = feedbacklist[0]

    action = serializer.save(annotation=annotation,
                             turker=turker,
                             feedback=feedback,
                             date=timezone.now())
    identifier = action.id

    return {"identifier": identifier, "feedback_text": feedback.feedback_text}


class OnboardingActionsList(generics.ListCreateAPIView):
  queryset = Actions.objects.all()
  serializer_class = ActionsSerializer

  def create(self, request, *args, **kwargs):

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    res_dict = self.perform_create(serializer)

    turkerid = request.data['turkerid']

    # exclude previously followed annotations or annotations by this turker
    # annotationlist = Annotation.objects.filter(turker_id="onboarding").values_list(
    #    'pk', flat=True).exclude(actions__turker=turkerid)
    annotationlist = Annotation.objects.exclude(
        turker_id="onboarding").exclude(
        turker_id="vcirik").exclude(
        turker_id="nicki").exclude(
        turker_id="demo").exclude(
        turker_id="A1QFJ9QG6U0A31").exclude(
        turker_id="A3HO7SJ2EG6JJF").values_list(
        'pk', flat=True).exclude(actions__turker=turkerid)

    random_pk = choice(annotationlist)
    annotation = Annotation.objects.get(pk=random_pk)
    serializer = AnnotationShallowSerializer(annotation)

    d = serializer.data
    d['new_actions'] = res_dict['identifier']
    d['feedback_text'] = res_dict['feedback_text']
    return Response(d)

  def perform_create(self, serializer):

    annotation = Annotation.objects.get(pk=self.request.data['annotationid'])
    turkerid = self.request.data['turkerid']

    identifier = 0
    turkerlist = Turker.objects.filter(
        turkerid=self.request.data['turkerid'])
    # if there is no such turker create one
    if len(turkerlist) > 0:
      turker = turkerlist[0]
    else:
      turker = Turker(turkerid=turkerid, date=timezone.now())
      turker.save()

    if self.request.data['feedback_text'] == '':
      feedback = new_feedback('')
    else:
      feedbacklist = Feedback.objects.filter(
          feedback_text=self.request.data['feedback_text'])
      if not len(feedbacklist):
        feedback = new_feedback(self.request.data['feedback_text'])
      else:
        feedback = feedbacklist[0]

    session = self.request.data['session']
    action = serializer.save(annotation=annotation,
                             turker=turker,
                             feedback=feedback,
                             session=session,
                             date=timezone.now())
    identifier = action.id
    return {"identifier": identifier, "feedback_text": feedback.feedback_text}


class DebugDescribing(APIView):

  def get_object(self, pk):
    try:
      return Annotation.objects.get(pk=pk)
    except Annotation.DoesNotExist:
      raise Http404

  def get(self, request, pk, format=None):
    annotation = self.get_object(pk)
    serializer = AnnotationSerializer(annotation)
    return Response(serializer.data)

  # def put(self, request, pk, format=None):
  #   annotation = self.get_object(pk)
  #   serializer = AnnotationSerializer(
  #       annotation, data=request.data)
  #   if serializer.is_valid():
  #     serializer.save()
  #     return Response(serializer.data)
  #   return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  # def delete(self, request, pk, format=None):
  #   annotation = self.get_object(pk)
  #   annotation.delete()
  #   return Response(status=status.HTTP_204_NO_CONTENT)


class DebugActions(APIView):

  def get_object(self, pk):
    try:
      return Actions.objects.get(pk=pk)
    except Actions.DoesNotExist:
      raise Http404

  def get(self, request, pk, format=None):
    action = self.get_object(pk)
    serializer = ActionsSerializer(action)
    return Response(serializer.data)

  # def put(self, request, pk, format=None):
  #   action = self.get_object(pk)
  #   serializer = ActionsSerializer(
  #       action, data=request.data)
  #   if serializer.is_valid():
  #     serializer.save()
  #     return Response(serializer.data)
  #   return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  # def delete(self, request, pk, format=None):
  #   action = self.get_object(pk)
  #   action.delete()
  #   return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewsDetail(APIView):
  permission_classes = [permissions.IsAuthenticated, ]

  def get_object(self, pk):
    try:
      return Reviews.objects.get(pk=pk)
    except Reviews.DoesNotExist:
      raise Http404

  def get(self, request, pk, format=None):

    reviews = self.get_object(pk)
    serializer = ReviewsSerializer(reviews)
    return Response(serializer.data)

  def put(self, request, pk, format=None):

    reviews = self.get_object(pk)
    serializer = ReviewsSerializer(
        reviews, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pk, format=None):
    review = self.get_object(pk)
    review.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewsList(generics.ListCreateAPIView):
  permission_classes = [IsCreationOrIsAuthenticated]
  queryset = Reviews.objects.all()
  serializer_class = ReviewsSerializer

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if 'round' in kwargs:
      ann_rnd = list(self.kwargs['round'])
      ann_rnd[0] = 'v'
      ann_rnd = ''.join(ann_rnd)
    else:
      ann_rnd = None
    res_dict = self.perform_create(serializer, ann_rnd)

    turkerid = request.data['turkerid']

    # exclude previously followed annotations or annotations by this turker
    annotationlist = Annotation.objects.exclude(turker_id=turkerid).exclude(
        turker_id="onboarding").exclude(
        turker_id="vcirik").exclude(
        turker_id="nicki").exclude(
        turker_id="demo").exclude(
        turker_id="A1QFJ9QG6U0A31").exclude(
        turker_id="A3HO7SJ2EG6JJF").values_list(
        'pk', flat=True).exclude(reviews__turker=turkerid)

    random_pk = choice(annotationlist)
    annotation = Annotation.objects.get(pk=random_pk)
    serializer = AnnotationShallowSerializer(annotation)

    d = serializer.data
    d['new_reviews'] = res_dict['identifier']

    return Response(d)

  def perform_create(self, serializer, ann_rnd=None):

    annotation = Annotation.objects.get(pk=self.request.data['annotationid'])
    if ann_rnd:
      annotation.ann_rnd = ann_rnd
      annotation.save()
    turkerid = self.request.data['turkerid']

    identifier = 0
    turkerlist = Turker.objects.filter(
        turkerid=self.request.data['turkerid'])
    # if there is no such turker create one
    if len(turkerlist) > 0:
      turker = turkerlist[0]
    else:
      turker = Turker(turkerid=turkerid, date=timezone.now())
      turker.save()

    review = serializer.save(annotation=annotation,
                             turker=turker,
                             date=timezone.now())
    identifier = review.id

    return {"identifier": identifier}

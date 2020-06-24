from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^sessions_stat/$', views.SessionsStat.as_view()),
    url(r'^annotations_unfollowed/$', views.AnnotationUnfollowed.as_view()),
    url(r'^annotations/(?P<ann_cat>[A-Za-z])$',
        views.AnnotationByCategory.as_view()),
    url(r'^annotations/category/(?P<ann_cat>[A-Za-z0-9]+)$',
        views.AnnotationByCategory.as_view()),
    url(r'^annotations/session/(?P<session>[A-Za-z0-9]+)$',
        views.AnnotationBySession.as_view()),
    url(r'^annotations/round/(?P<round>[A-Za-z|0-9]+)$',
        views.AnnotationByRound.as_view()),

    url(r'^annotations/$', views.AnnotationList.as_view()),
    url(r'^annotations/(?P<pk>[0-9]+)/$', views.AnnotationDetail.as_view()),

    url(r'^image_categories$', views.ImageAllCategories.as_view()),
    url(r'^image_categories/(?P<category>[A-Za-z_]+)$',
        views.ImageStatsByCategories.as_view()),
    url(r'^images/$', views.ImageList.as_view()),
    url(r'^images/(?P<category>[A-Za-z]+)$',
        views.ImageListByCategory.as_view()),
    url(r'^images/(?P<suffix>[A-Za-z0-9_]+)$',
        views.ImageDetail.as_view()),

    url(r'^feedback/$', views.FeedbackList.as_view()),
    url(r'^feedback/(?P<pk>[A-Za-z0-9]+)/$', views.FeedbackDetail.as_view()),
    url(r'^validate_passphrase/(?P<pk>[A-Za-z0-9]+)/$',
        views.ValidatePassphrase.as_view()),
    url(r'^validate_passphrase/(?P<pk>[A-Za-z0-9]+)/(?P<constraint>[a-z]+)$',
        views.ValidatePassphrase.as_view()),

    #url(r'^clean_turkers/$', views.CleanTurkerList.as_view()),

    url(r'^turkers/$', views.TurkerList.as_view()),
    url(r'^turkers/(?P<turkerid>[A-Za-z0-9]+)/$',
        views.TurkerDetail.as_view()),
    url(r'^turkers/(?P<turkerid>[A-Za-z0-9]+)/(?P<session>[A-Za-z0-9]{3})$',
        views.TurkerDetail.as_view()),

    url(r'^turkers_list/$', views.TurkerShallowList.as_view()),
    url(r'^turkers_stat/$', views.TurkersStat.as_view()),
    url(r'^turkers_sessions/(?P<session>[A-Za-z0-9]+)/(?P<task>[A-Za-z0-9]+)$',
        views.TurkersBySession.as_view()),

    url(r'^turkers/(?P<turkerid>[A-Za-z0-9]+)/(?P<session>[A-Za-z0-9]+)$',
        views.TurkerRank.as_view()),

    url(r'^next_turker/(?P<reviewerid>[A-Za-z0-9]+)/(?P<session>[A-Za-z0-9]+)/(?P<order>[0-9]+)/$',
        views.NextTurker.as_view()),
    url(r'^next_image/(?P<turkerid>[A-Za-z0-9]+)/$',
        views.NextImage.as_view()),
    url(r'^next_follow_image/(?P<turkerid>[A-Za-z0-9]+)/$',
        views.NextFollowImage.as_view()),
    url(r'^next_follow_image/(?P<turkerid>[A-Za-z0-9]+)/(?P<round>[A-Za-z0-9|]+)/$',
        views.NextFollowImage.as_view()),
    url(r'^onboarding/(?P<turkerid>[A-Za-z0-9]+)/$',
        views.Onboarding.as_view()),
    url(r'^leaderboard/(?P<turkerid>[A-Za-z0-9]+)/$',
        views.LeaderBoard.as_view()),

    url(r'^actions/(?P<pk>[0-9]+)/$', views.ActionsDetail.as_view()),
    url(r'^actions/$', views.ActionsList.as_view()),
    url(r'^actions/(?P<round>[A-Za-z0-9|]+)/$',
        views.ActionsList.as_view()),
    url(r'^onboarding_actions/$', views.OnboardingActionsList.as_view()),

    url(r'^next_debug_annotation/(?P<pk>[A-Za-z0-9]+)/$',
        views.AnnotationDetail.as_view()),
    url(r'^next_debug_action/(?P<pk>[A-Za-z0-9]+)/$',
        views.ActionsDetail.as_view()),

    url(r'^debug/(?P<pk>[0-9]+)$',
        views.DebugDescribing.as_view()),
    url(r'^debug_actions/(?P<pk>[0-9]+)$',
        views.DebugActions.as_view()),
    url(r'^change_round/(?P<annotationid>[A-Za-z0-9]+)/(?P<round>[A-Za-z0-9]+)/$',
        views.ChangeRound.as_view()),

    url(r'^reviews/(?P<pk>[0-9]+)/$', views.ReviewsDetail.as_view()),
    url(r'^reviews/$', views.ReviewsList.as_view()),
    url(r'^reviews/(?P<round>[A-Za-z0-9]{3})/$',
        views.ReviewsList.as_view()),

]

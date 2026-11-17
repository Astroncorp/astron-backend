from django.urls import path

from .views import (
    CourseChannelListAPIView,
    claim_bonus,
    dismiss_channel_recommendation,
    get_announcement,
    get_channel_recommendation,
    increment_receivers,
    like_dislike,
    payme_callback,
    telemetry,
    record_subject_visit,
)

urlpatterns = [
    path("payme/", payme_callback),
    path("announcement/", get_announcement),
    path("channel-recommendation/", get_channel_recommendation),
    path("channel-recommendation/dismiss/", dismiss_channel_recommendation),
    path("telemetry/", telemetry),
    path("increment-receivers/", increment_receivers),
    path("course_channels/", CourseChannelListAPIView.as_view()),
    path("like_dislike/", like_dislike),
    path("bonus/", claim_bonus),
    path("subject-visit/", record_subject_visit),
]

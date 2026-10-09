from django.urls import path

from .views import (
    CourseChannelListAPIView,
    claim_bonus,
    count_test_subject_visit,
    get_announcement,
    increment_receivers,
    like_dislike,
    payme_callback,
    sync_test_subjects,
    telemetry,
)

urlpatterns = [
    path("payme/", payme_callback),
    path("announcement/", get_announcement),
    path("telemetry/", telemetry),
    path("increment-receivers/", increment_receivers),
    path("course_channels/", CourseChannelListAPIView.as_view()),
    path("like_dislike/", like_dislike),
    path("bonus/", claim_bonus),
    path("test-subjects/sync/", sync_test_subjects),
    path("test-subjects/visit/", count_test_subject_visit),
]

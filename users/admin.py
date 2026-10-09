from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin

from .models import (
    Advertisement,
    Announcement,
    Bonus,
    Channel,
    Count,
    CourseChannel,
    Post,
    SubjectVisitCount,
    Transaction,
    User,
)


@admin.register(User)
class UserModelAdmin(UserAdmin, ModelAdmin):
    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "balance",
    ]
    list_filter = [
        "date_joined",
    ]

    model = User
    form = UserChangeForm
    add_form = UserCreationForm

    add_fieldsets = (
        (
            "Ma'lumotlar",
            {
                "fields": (
                    "id",
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                )
            },
        ),
    )
    fieldsets = (
        (
            "Ma'lumotlar",
            {
                "fields": (
                    "id",
                    "username",
                    "first_name",
                    "last_name",
                )
            },
        ),
    )


@admin.register(CourseChannel)
class CourseChannelModelAdmin(ModelAdmin):
    list_display = [
        "handle",
        "name",
    ]


@admin.register(Count)
class CountModelAdmin(ModelAdmin):
    list_display = ["created", "count"]


@admin.register(Announcement)
class AnnouncementModelAdmin(ModelAdmin):
    list_display = ["content", "created"]


@admin.register(Transaction)
class TransactionModelAdmin(ModelAdmin):
    list_display = ["id", "author", "type", "state", "amount"]


@admin.register(Channel)
class ChannelModelAdmin(ModelAdmin):
    list_display = ["id", "title", "is_verified"]


@admin.register(Advertisement)
class AdvertisementModelAdmin(ModelAdmin):
    list_display = ["content", "status", "receivers"]


@admin.register(Post)
class PostModelAdmin(ModelAdmin):
    list_display = ["content"]


@admin.register(Bonus)
class BonusModelAdmin(ModelAdmin):
    list_display = ["user_id", "post_id"]


@admin.register(SubjectVisitCount)
class SubjectVisitCountAdmin(ModelAdmin):
    list_display = ["display_subject_name", "display_visit_count"]
    list_display_links = None
    ordering = ["sort_order", "id"]

    @admin.display(description="Fan", ordering="subject_name")
    def display_subject_name(self, obj):
        return obj.subject_name

    @admin.display(description="Kirishlar soni", ordering="visit_count")
    def display_visit_count(self, obj):
        return obj.visit_count

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

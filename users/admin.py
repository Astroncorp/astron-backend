from django.contrib import admin
from django.http import HttpResponse
from django.template import engines
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


# Faqat interfeys uchun proxy model: mavjud Count jadvalidan foydalanadi.
# Alohida SubjectVisitCount modeli yoki jadvali talab qilinmaydi.
class FanSanagich(Count):
    class Meta:
        proxy = True
        verbose_name = "Fan sanagich"
        verbose_name_plural = "Fan sanagich"


@admin.register(FanSanagich)
class FanSanagichAdmin(ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        if not self.has_view_or_change_permission(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

        context = {
            **self.admin_site.each_context(request),
            "title": "Fan sanagich (Test)",
            "opts": self.model._meta,
            "app_label": self.model._meta.app_label,
            "demo_subjects": [
                {"name": f"Fan {i}", "count": "1 000"}
                for i in range(1, 10)
            ],
        }
        if extra_context:
            context.update(extra_context)
        return HttpResponse(
            engines["django"].from_string(SUBJECT_COUNTER_TEMPLATE).render(context, request)
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


SUBJECT_COUNTER_TEMPLATE = '{% extends "admin/base_site.html" %}\n{% load i18n %}\n{% block content %}\n<style>\n  .astron-subjects-layout {display:block;width:100%;}\n  .astron-counter-panel {background:var(--color-base-0,#fff);border:1px solid #e5e7eb;border-radius:9px;overflow:hidden;}\n  .astron-counter-head {display:flex;justify-content:space-between;gap:12px;align-items:center;background:#f8f9fa;padding:17px 20px;font-size:17px;font-weight:600;color:#111827;}\n  .astron-counter-table {width:100%;border-collapse:collapse;font-size:15px;color:#111827;}\n  .astron-counter-table td {padding:12px 17px;border-bottom:1px solid #f0f1f3;}\n  .astron-counter-table tr:last-child td {border-bottom:0;}\n  .astron-counter-table td:last-child {text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;}\n  .astron-counter-actions {display:flex;justify-content:space-between;gap:16px;padding:22px 4px 4px;}\n  .astron-btn {display:inline-flex;align-items:center;justify-content:center;gap:8px;border-radius:6px;border:1px solid #cbd5e1;background:white;padding:10px 15px;font-weight:600;color:#111827;font-size:14px;cursor:default;}\n  .astron-btn, .astron-btn-primary {background:#2563EB;border-color:#2563EB;color:white;cursor:pointer;}\n  @media(max-width:560px){.astron-counter-head{font-size:14px;padding:14px 12px}.astron-counter-table td{padding:10px 12px}.astron-counter-actions{flex-wrap:wrap}.astron-btn{flex:1}}\n</style>\n<div class="astron-subjects-layout">\n  <div>\n    <div class="astron-counter-panel">\n      <div class="astron-counter-head"><span>Fan sanagich (Test)</span><span>Kirishlar soni</span></div>\n      <table class="astron-counter-table" aria-label="Fanlar kirishlar soni"><tbody>\n      {% for subject in demo_subjects %}\n        <tr><td>{{ subject.name }}</td><td>{{ subject.count }}</td></tr>\n      {% endfor %}\n      </tbody></table>\n    </div>\n    <div class="astron-counter-actions">\n      <button type="button" class="astron-btn" title="Funksiya keyin ulanadi">Kirishlarni yangilash</button>\n      <button type="button" class="astron-btn astron-btn-primary" title="Funksiya keyin ulanadi">Fanlarni sinxronlash</button>\n    </div>\n  </div>\n</div>\n{% endblock %}\n'

# Admin bosh sahifasidagi Users ro'yxatidan Fan sanagichni yashiramiz.
# Unfold chap menyusidagi havola va admin sahifasi saqlanadi.
from django.urls import reverse

_original_get_app_list = admin.site.get_app_list


def get_app_list_without_fan_sanagich(request, app_label=None):
    app_list = _original_get_app_list(request, app_label)
    if request.path == reverse("admin:index"):
        for app in app_list:
            app["models"] = [
                model for model in app["models"]
                if model.get("object_name") != "FanSanagich"
            ]
    return app_list


admin.site.get_app_list = get_app_list_without_fan_sanagich

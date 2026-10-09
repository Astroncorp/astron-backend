from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.exceptions import PermissionDenied
from urllib.request import urlopen
import json
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
    SubjectCounter,
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
# Proxy model Count jadvalini ishlatadi; fanlar SubjectCounter jadvalida saqlanadi.
class FanSanagich(Count):
    class Meta:
        proxy = True
        verbose_name = "Fan sanagich"
        verbose_name_plural = "Fan sanagich"


@admin.register(FanSanagich)
class FanSanagichAdmin(ModelAdmin):
    @method_decorator(csrf_protect)
    def changelist_view(self, request, extra_context=None):
        if not self.has_view_or_change_permission(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

        if request.method == "POST" and request.POST.get("action") == "reset_counts":
            if not request.user.is_superuser:
                raise PermissionDenied
            SubjectCounter.objects.all().update(count=0)
            messages.success(request, "Barcha fanlarning kirishlar soni 0 ga tushirildi.")
            return HttpResponseRedirect(request.path)

        sync_message = ""
        if request.method == "POST" and request.POST.get("action") == "sync_subjects":
            if not request.user.is_superuser:
                raise PermissionDenied
            try:
                with urlopen(
                    "https://astrontest.uz/mobile-api/api/fanlar_sync.php",
                    timeout=12,
                ) as response:
                    payload = json.load(response)
                if not isinstance(payload, list):
                    raise ValueError("API fanlar ro'yxatini qaytarmadi")
                subjects = []
                seen = set()
                for item in payload:
                    if not isinstance(item, dict) or int(item.get("t_status", 0)) != 1:
                        continue
                    subject_id = int(item["id"])
                    name = str(item["name"]).strip()
                    if subject_id <= 0 or not name or subject_id in seen:
                        continue
                    seen.add(subject_id)
                    subjects.append({"id": subject_id, "name": name})
                if not subjects:
                    raise ValueError("API faol test fanlarini qaytarmadi; mavjud ro'yxat saqlandi")
                with transaction.atomic():
                    synced_ids = []
                    for position, item in enumerate(subjects):
                        SubjectCounter.objects.update_or_create(
                            subject_id=item["id"],
                            defaults={
                                "name": item["name"],
                                "position": position,
                                "is_active": True,
                            },
                        )
                        synced_ids.append(item["id"])
                    SubjectCounter.objects.exclude(subject_id__in=synced_ids).update(is_active=False)
                messages.success(request, f"{len(subjects)} ta test fani sinxronlandi.")
                return HttpResponseRedirect(request.path)
            except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
                sync_message = f"Sinxronlash amalga oshmadi: {exc}"

        rows = [
            {"name": item.name, "count": f"{item.count:,}".replace(",", " ")}
            for item in SubjectCounter.objects.filter(is_active=True)
        ]
        context = {
            **self.admin_site.each_context(request),
            "title": "Fan sanagich (Test)",
            "opts": self.model._meta,
            "app_label": self.model._meta.app_label,
            "demo_subjects": rows,
            "sync_message": sync_message,
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


SUBJECT_COUNTER_TEMPLATE = '{% extends "admin/base_site.html" %}\n{% load i18n %}\n{% block content %}\n<style>\n  .astron-subjects-layout {display:block;width:100%;}\n  .astron-counter-panel {background:var(--color-base-0,#fff);border:1px solid #e5e7eb;border-radius:9px;overflow:hidden;}\n  .astron-counter-head {display:flex;justify-content:space-between;gap:12px;align-items:center;background:#f8f9fa;padding:17px 20px;font-size:17px;font-weight:600;color:#111827;}\n  .astron-counter-table {width:100%;border-collapse:collapse;font-size:15px;color:#111827;}\n  .astron-counter-table td {padding:12px 17px;border-bottom:1px solid #f0f1f3;}\n  .astron-counter-table tr:last-child td {border-bottom:0;}\n  .astron-counter-table td:last-child {text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;}\n  .astron-counter-actions {display:flex;justify-content:space-between;gap:16px;padding:22px 4px 4px;}\n  .astron-btn {display:inline-flex;align-items:center;justify-content:center;gap:8px;border-radius:6px;border:1px solid #cbd5e1;background:white;padding:10px 15px;font-weight:600;color:#111827;font-size:14px;cursor:default;}\n  .astron-btn, .astron-btn-primary {background:#2563EB;border-color:#2563EB;color:white;cursor:pointer;}\n  @media(max-width:560px){.astron-counter-head{font-size:14px;padding:14px 12px}.astron-counter-table td{padding:10px 12px}.astron-counter-actions{flex-wrap:wrap}.astron-btn{flex:1}}\n</style>\n<div class="astron-subjects-layout">\n  <div>\n    {% if sync_message %}<p role="status" style="margin-bottom:12px">{{ sync_message }}</p>{% endif %}\n    <div class="astron-counter-panel">\n      <div class="astron-counter-head"><span>Fan sanagich (Test)</span><span>Kirishlar soni</span></div>\n      <table class="astron-counter-table" aria-label="Fanlar kirishlar soni"><tbody>\n      {% for subject in demo_subjects %}\n        <tr><td>{{ subject.name }}</td><td>{{ subject.count }}</td></tr>\n      {% endfor %}\n      </tbody></table>\n    </div>\n    <div class="astron-counter-actions">\n      <form method="post" style="margin:0">{% csrf_token %}<input type="hidden" name="action" value="sync_subjects"><button type="submit" class="astron-btn astron-btn-primary">Fanlarni sinxronlash</button></form>\n      <form method="post" style="margin:0" onsubmit="return confirm(&quot;Barcha fanlarning kirishlar soni 0 ga tushirilsinmi?&quot;)">{% csrf_token %}<input type="hidden" name="action" value="reset_counts"><button type="submit" class="astron-btn">Kirishlarni yangilash</button></form>\n    </div>\n  </div>\n</div>\n{% endblock %}\n'

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

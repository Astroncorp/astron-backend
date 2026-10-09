import json
import time
from datetime import datetime

import requests
from django.http import HttpRequest
from django.db.models import F
from rest_framework.permissions import AllowAny
from rest_framework import decorators, generics
from rest_framework.response import Response

from .models import (
    Advertisement,
    Announcement,
    Bonus,
    Count,
    SubjectCounter,
    CourseChannel,
    Transaction,
    User,
)
from .serializers import CourseChannelSerializer


class CourseChannelListAPIView(generics.ListAPIView):
    queryset = CourseChannel.objects.all()
    serializer_class = CourseChannelSerializer


@decorators.api_view(http_method_names=["POST"])
def payme_callback(request: HttpRequest):
    user: User = None
    body = json.loads(request.body.decode())

    if body.get("method") == "CheckPerformTransaction":
        username = body.get("params", {}).get("account", {}).get("appid", "")

        user = User.objects.filter(username=username)

        if not user:
            return Response(
                {
                    "error": {
                        "code": -31050,
                        "message": {
                            "en": "User not found",
                            "ru": "User not found",
                            "uz": "Foydalanuvchi topilmadi",
                        },
                        "data": "id",
                    }
                }
            )

        user = user.first()

        return Response(
            {
                "jsonrpc": "2.0",
                "id": username,
                "result": {
                    "allow": True,
                    "additional": {
                        "id": username,
                        "name": f"{user.first_name} {user.last_name}"
                        if (user.first_name and user.last_name)
                        else "Astron foydalanuvchisi",
                        "balance": user.balance,
                    },
                },
            }
        )

    if body.get("method") == "CreateTransaction":
        username = body.get("params", {}).get("account", {}).get("appid", "")
        transaction_id = body.get("params", {}).get("id")
        amount = body.get("params", {}).get("amount", 1) / 100

        user = User.objects.filter(username=username).first()

        transaction = Transaction.objects.create(
            id=transaction_id, author=user, amount=amount, state=1
        )

        return Response(
            {
                "result": {
                    "create_time": body.get("params").get("time"),
                    "transaction": transaction.id,
                    "state": transaction.state,
                }
            }
        )

    if body.get("method") == "PerformTransaction":
        transaction_id = body.get("params", {}).get("id")

        transaction = Transaction.objects.filter(id=transaction_id)

        if not transaction:
            return Response({"error": {"code": -31003}})

        transaction = transaction.first()
        transaction.author.balance = transaction.author.balance + transaction.amount
        transaction.author.save()
        transaction.state = 2
        transaction.save()

        return Response(
            {
                "result": {
                    "transaction": transaction_id,
                    "perform_time": int(time.time()),
                    "state": 2,
                }
            }
        )

    return Response({})


@decorators.api_view(http_method_names=["GET"])
def get_announcement(request: HttpRequest):
    announcement = Announcement.objects.last()
    if announcement:
        return Response(
            {"content": announcement.content, "created": announcement.created}
        )
    return Response({"content": None, "created": None})


@decorators.api_view(http_method_names=["POST"])
def telemetry(request: HttpRequest):
    today = datetime.today()
    count = Count.objects.filter(created=today)

    if not count:
        count = Count.objects.create(count=1)
    else:
        count = count.first()
        count.count += 1
        count.save()

    data = request.data

    id = data.get("id", None)
    username = data.get("username", id)
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if not id:
        return Response({"status": "!ok"})

    user = User.objects.filter(id=id)

    if not user.exists():
        user = User.objects.create(
            id=id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            balance=0,
        )

    else:
        user = user.first()

        user.first_name = first_name
        user.last_name = last_name
        user.save()

    return Response({"status": "ok"})


@decorators.api_view(http_method_names=["GET"])
def increment_receivers(request: HttpRequest):
    ads = request.GET.get("ads")
    user_id = request.GET.get("user_id", None)

    if user_id:
        user = User.objects.filter(pk=user_id)
        if user:
            user = user.first()
            user.delete()
            return Response({"status": "ok"})

    if not ads:
        print(ads)
        return Response({"status": "!ok"})

    ads = Advertisement.objects.filter(pk=ads)

    if not ads:
        return Response({"status": "!ok"})

    ads = ads.first()

    ads.receivers = ads.receivers + 1
    ads.save()

    return Response({"status": "ok"})


@decorators.api_view(http_method_names=["POST"])
def like_dislike(request: HttpRequest):
    data = request.data

    user_id = data.get("user_id", None)
    course_id = data.get("course_id", None)

    print(user_id, course_id)

    if not user_id or not course_id:
        return Response({"status": "error"})

    user = User.objects.filter(id=user_id)
    course = CourseChannel.objects.filter(handle=course_id)

    if user and course:
        user = user.first()
        course = course.first()

        if user in course.likers.all():
            course.likers.remove(user)
        else:
            course.likers.add(user)

    return Response({"status": "ok"})


@decorators.api_view(http_method_names=["POST"])
def claim_bonus(request: HttpRequest):
    data = request.data
    user_id = data.get("user_id")
    post_id = data.get("post_id")

    if not user_id or not post_id:
        return Response({"claimed": False}, status=400)

    try:
        # Bazaga yangi bonus yozamiz
        Bonus.objects.create(user_id=user_id, post_id=post_id)

        res = requests.post(
            "https://astrontest.uz/mypage/users_balans_saqlash.php",
            data={
                "profile_id": user_id,
                "amount": 1000,
            },
        )

        print(res.text)

        return Response({"claimed": True})

    except:
        return Response({"claimed": False})


@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes([AllowAny])
def record_subject_visit(request: HttpRequest):
    """Count a Testlar subject opening; no visitor identity is stored."""
    try:
        # text/plain avoids a browser CORS preflight for this public event endpoint.
        data = json.loads(request.body.decode("utf-8"))
        subject_id = data.get("subject_id")
        if isinstance(subject_id, bool) or not isinstance(subject_id, int) or subject_id <= 0:
            return Response({"status": "error", "message": "Invalid subject_id"}, status=400)
    except (ValueError, UnicodeDecodeError, AttributeError, TypeError):
        return Response({"status": "error", "message": "Invalid JSON"}, status=400)

    changed = SubjectCounter.objects.filter(
        subject_id=subject_id, is_active=True
    ).update(count=F("count") + 1)
    if not changed:
        return Response({"status": "error", "message": "Subject not found"}, status=404)
    return Response({"status": "ok"})

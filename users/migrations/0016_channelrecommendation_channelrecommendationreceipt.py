from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0015_subjectcounter_fansanagich"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChannelRecommendation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(verbose_name="Matn")),
                (
                    "post_url",
                    models.URLField(
                        max_length=2000,
                        verbose_name="Telegram post havolasi",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created", "-id"],
                "verbose_name": "Kanaldan tavsiya",
                "verbose_name_plural": "Kanaldan tavsiya",
            },
        ),
        migrations.CreateModel(
            name="ChannelRecommendationReceipt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "recommendation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="receipts",
                        to="users.channelrecommendation",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="channel_recommendation_receipts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("recommendation", "user"),
                        name="unique_channel_recommendation_user",
                    ),
                ],
            },
        ),
    ]

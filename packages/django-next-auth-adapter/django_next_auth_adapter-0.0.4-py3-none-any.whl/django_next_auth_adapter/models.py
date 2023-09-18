from uuid import uuid4
from typing import Type
from django.db import models
from django.contrib.auth import get_user_model

User: Type[get_user_model()] = get_user_model()


def generate_db_id():
    return str(uuid4())


class Account(models.Model):
    id = models.CharField(
        primary_key=True, default=generate_db_id, editable=False, max_length=36
    )
    user: User = models.ForeignKey(
        to=User,
        related_name="accounts",
        on_delete=models.CASCADE,
    )
    type = models.CharField(max_length=50)
    provider = models.CharField(max_length=50)
    provider_account_id = models.CharField(max_length=255)
    refresh_token = models.TextField(blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    expires_at = models.PositiveIntegerField(blank=True, null=True)
    token_type = models.CharField(max_length=50, blank=True, null=True)
    scope = models.CharField(max_length=255, blank=True, null=True)
    id_token = models.TextField(blank=True, null=True)
    session_state = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "accounts"
        verbose_name = "account"
        verbose_name_plural = "accounts"
        unique_together = ("provider", "provider_account_id")

    def __str__(self):
        return f"{self.id} - {self.user.email}"


class Session(models.Model):
    id = models.CharField(
        primary_key=True, default=generate_db_id, editable=False, max_length=36
    )
    user: User = models.ForeignKey(
        to=User,
        related_name="sessions",
        on_delete=models.CASCADE,
    )
    session_token = models.CharField(max_length=255, unique=True)
    expires = models.DateTimeField()

    class Meta:
        db_table = "sessions"
        verbose_name = "session"
        verbose_name_plural = "sessions"

    def __str__(self):
        return self.id


class VerficationToken(models.Model):
    identifier = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    expires = models.DateTimeField()

    class Meta:
        db_table = "verification_tokens"
        verbose_name = "verification token"
        verbose_name_plural = "verification tokens"
        unique_together = ("identifier", "token")

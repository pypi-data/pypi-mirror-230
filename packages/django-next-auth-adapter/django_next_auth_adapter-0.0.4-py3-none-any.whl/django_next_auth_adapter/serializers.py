from django.utils.crypto import get_random_string
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Account, Session, VerficationToken
from .signals import user_created, user_updated

User = get_user_model()


class AdapterUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_null=True)
    image = serializers.URLField(required=False, allow_null=True)
    emailVerified = serializers.DateTimeField(
        required=False, allow_null=True, source="email_verified"
    )

    class Meta:
        model = User
        fields = ["id", "email", "emailVerified", "name", "image"]

    def get_names_pair(self, name: str) -> tuple[str, str]:
        name = name.split(" ")
        if len(name) == 2:
            return (name[0], name[1])
        elif len(name) == 1:
            return (name[0], "")
        else:
            return ("", "")

    def create(self, validated_data: dict) -> User:
        name = validated_data.pop("name", None)
        image = validated_data.pop("image", None)
        if name is not None:
            (
                validated_data["first_name"],
                validated_data["last_name"],
            ) = self.get_names_pair(name)

        instance = super().create(validated_data)
        if name is not None:
            instance.name = validated_data.get("name")
        if image is not None:
            instance.image = image

        validated_data["password"] = get_random_string(32)
        user_created.send(
            sender=self.__class__,
            user=instance,
            validated_data=validated_data,
            image=image,
            name=name,
        )

        return AdapterPublicUserSerializer(instance).data

    def update(self, instance: User, validated_data):
        if validated_data.get("name", None) is None:
            instance.name = instance.get_full_name()
        else:
            (
                validated_data["first_name"],
                validated_data["last_name"],
            ) = self.get_names_pair(validated_data.get("name"))
        user_updated.send(
            sender=self.__class__, user=instance, validated_data=validated_data
        )
        return super().update(instance, validated_data)


class AdapterPublicUserSerializer(AdapterUserSerializer):
    name = serializers.CharField(source="get_full_name")
    image = serializers.SerializerMethodField(method_name="get_profile_image")
    emailVerified = serializers.CharField(source="email_verified")

    def get_profile_image(self, obj: User) -> str:
        if hasattr(obj, "get_image") and callable(getattr(obj, "get_image")):
            img = getattr(obj, "get_image")()
            return img if isinstance(img, str) else ""
        return ""

    class Meta:
        model = User
        fields = ["id", "email", "emailVerified", "name", "image"]


class LinkAccountSerializer(serializers.ModelSerializer):
    providerAccountId = serializers.CharField(source="provider_account_id")
    userId = serializers.CharField(source="user_id")

    class Meta:
        model = Account
        fields = [
            "id",
            "userId",
            "type",
            "provider",
            "providerAccountId",
            "refresh_token",
            "access_token",
            "expires_at",
            "token_type",
            "scope",
            "id_token",
            "session_state",
        ]


class RemoteAdapterSessionSerializer(serializers.ModelSerializer):
    sessionToken = serializers.CharField(source="session_token")
    userId = serializers.CharField(source="user_id")

    class Meta:
        model = Session
        fields = [
            "id",
            "userId",
            "sessionToken",
            "expires",
        ]


class RemoteAdapterSessionAndUserSerializer(serializers.Serializer):
    session = RemoteAdapterSessionSerializer()
    user = AdapterPublicUserSerializer()


class RemoteAdapterVerificationTokensSerializers(serializers.ModelSerializer):
    class Meta:
        model = VerficationToken
        fields = "__all__"

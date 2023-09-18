from rest_framework import status
from rest_framework.response import Response as DRFResponse
from rest_framework import generics
from rest_framework.views import APIView
from .mixins import WrappedResponseMixin
from django.contrib.auth import get_user_model
from .settings import permission_classes as default_permission_classes
from .permissions import AllowRemoteAuthServer
from .models import Account, Session, VerficationToken

from . import serializers as auth_serializers

User = get_user_model()
permission_classes = default_permission_classes or [AllowRemoteAuthServer]


class RemoteAdapterSignupView(WrappedResponseMixin, APIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.AdapterUserSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data.get("email"))
            if user is not None:
                return DRFResponse(
                    data=auth_serializers.AdapterPublicUserSerializer(user).data,
                    status=status.HTTP_200_OK,
                )
        except User.DoesNotExist:
            pass
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = serializer.create(validated_data=serializer.validated_data)
        return DRFResponse(data=res, status=status.HTTP_201_CREATED)


class RetrieveUserByIdView(WrappedResponseMixin, generics.RetrieveAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.AdapterPublicUserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.queryset.get(id=self.kwargs.get("id"))


class RetrieveUserByEmailAPIView(WrappedResponseMixin, generics.RetrieveAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.AdapterPublicUserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.queryset.get(email=self.kwargs.get("email"))

    def handle_exception(self, exc):
        return DRFResponse(data=str(exc), status=status.HTTP_400_BAD_REQUEST)


class RetrieveUserByAccountAPIView(WrappedResponseMixin, generics.RetrieveAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.AdapterPublicUserSerializer
    queryset = Account.objects.all()

    def get_object(self):
        account_id = self.kwargs.get("account_id")
        provider = self.kwargs.get("provider")
        return self.queryset.get(provider_account_id=account_id, provider=provider).user

    def handle_exception(self, exc):
        return DRFResponse(data=str(exc), status=status.HTTP_400_BAD_REQUEST)


class UpdateUserAPIView(WrappedResponseMixin, generics.UpdateAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.AdapterUserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.queryset.get(email=self.request.data.get("email"))

    def handle_exception(self, exc):
        return DRFResponse(data=str(exc), status=status.HTTP_400_BAD_REQUEST)


class DeletUserAPIView(WrappedResponseMixin, generics.DestroyAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.AdapterUserSerializer
    queryset = User.objects.all()
    lookup_url_kwarg = "id"


class LinkAccountAPIView(WrappedResponseMixin, generics.CreateAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.LinkAccountSerializer
    queryset = Account.objects.all()


class UnlinkAccountAPIView(WrappedResponseMixin, generics.DestroyAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.LinkAccountSerializer
    queryset = Account.objects.all()

    def get_object(self):
        provider = self.request.data.get("provider")
        provider_account_id = self.request.data.get("providerAccountId")
        return self.queryset.get(
            provider=provider, provider_account_id=provider_account_id
        )


class CreateSessionAPIView(WrappedResponseMixin, generics.CreateAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.RemoteAdapterSessionSerializer
    queryset = User.objects.all()


class UpdateSessionAPIView(WrappedResponseMixin, generics.UpdateAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.RemoteAdapterSessionSerializer
    queryset = Session.objects.all()

    def get_object(self):
        return self.queryset.get(session_token=self.request.data.get("sessionToken"))

    def handle_exception(self, exc):
        return DRFResponse(data=str(exc), status=status.HTTP_400_BAD_REQUEST)


class GetSessionAndUserAPIView(WrappedResponseMixin, generics.RetrieveAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.RemoteAdapterSessionAndUserSerializer
    queryset = Session.objects.all()

    def get_object(self):
        session = self.queryset.get(session_token=self.kwargs.get("session_token"))
        return {"user": session.user, "session": session}

    def handle_exception(self, exc):
        return DRFResponse(data=str(exc), status=status.HTTP_400_BAD_REQUEST)


class DeleteSessionAPIView(WrappedResponseMixin, generics.DestroyAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.RemoteAdapterSessionSerializer
    queryset = Session.objects.all()

    def get_object(self):
        return self.queryset.get(session_token=self.kwargs.get("session_token"))

    def handle_exception(self, exc):
        return DRFResponse(data=str(exc), status=status.HTTP_400_BAD_REQUEST)


class CreateVerificationTokenAPIView(WrappedResponseMixin, generics.CreateAPIView):
    permission_classes = permission_classes
    serializer_class = auth_serializers.RemoteAdapterVerificationTokensSerializers
    queryset = VerficationToken.objects.all()


class RetrieveVerificationToken(
    WrappedResponseMixin, generics.RetrieveAPIView, generics.CreateAPIView
):
    permission_classes = permission_classes
    serializer_class = auth_serializers.RemoteAdapterVerificationTokensSerializers
    queryset = VerficationToken.objects.all()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_object(self):
        return self.queryset.get(
            identifier=self.request.data.get("identifier"),
            tokne=self.request.data.get("token"),
        )

    def handle_exception(self, exc):
        return super().handle_exception(exc)

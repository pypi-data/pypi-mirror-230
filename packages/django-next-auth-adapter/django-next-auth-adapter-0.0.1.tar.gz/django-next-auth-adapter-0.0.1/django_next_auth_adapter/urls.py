from . import views
from django.urls import path

urlpatterns = [
    # next auth http adapter custom methods
    path("signup/", views.RemoteAdapterSignupView.as_view(), name="signup"),
    path("get-user/<uuid:id>/", views.RetrieveUserByIdView.as_view(), name="get_user"),
    path(
        "get-user-by-email/<str:email>/",
        views.RetrieveUserByEmailAPIView.as_view(),
        name="get_user_by_email",
    ),
    path(
        "get-user-by-account/<str:provider>/<str:account_id>/",
        views.RetrieveUserByAccountAPIView.as_view(),
        name="get_user_by_account",
    ),
    path("update-user/", views.UpdateUserAPIView.as_view(), name="update_user"),
    path("delete-user/<str:id>/", views.DeletUserAPIView.as_view(), name="delete_user"),
    path("link-account/", views.LinkAccountAPIView.as_view(), name="link_account"),
    path(
        "unlink-account/<str:provider>/<str:account_id>/",
        views.UnlinkAccountAPIView.as_view(),
        name="unlink_account",
    ),
    path(
        "create-session/", views.CreateSessionAPIView.as_view(), name="create_session"
    ),
    path(
        "get-session-and-user/<str:session_token>",
        views.GetSessionAndUserAPIView.as_view(),
        name="get_session_and_user",
    ),
    path(
        "update-session/", views.UpdateSessionAPIView.as_view(), name="update_session"
    ),
    path(
        "delete-session/", views.DeleteSessionAPIView.as_view(), name="delete_session"
    ),
    path(
        "create-verification-token/",
        views.CreateVerificationTokenAPIView.as_view(),
        name="create_verification_token",
    ),
    path(
        "use-verification-token/",
        views.RetrieveVerificationToken.as_view(),
        name="use_verification_token",
    ),
]

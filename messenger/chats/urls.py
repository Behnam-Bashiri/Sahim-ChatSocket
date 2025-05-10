from django.urls import path
from .views import *

urlpatterns = [
    path("chat-list/", ChatListView.as_view(), name="chat-list"),
    path("chat-users/", ChatUserListView.as_view(), name="chat-users"),
    path("create-chat/", CreateChatView.as_view(), name="create-chat"),
    path(
        "previous-chat-users/",
        PreviousChatUsersView.as_view(),
        name="previous-chat-users",
    ),
    path(
        "chat/with/<str:phone_number>/",
        ChatMessagesWithUserView.as_view(),
        name="chat-with-user",
    ),
    path("upload-file/<int:chat_id>/", FileUploadAPIView.as_view(), name="upload-file"),
]

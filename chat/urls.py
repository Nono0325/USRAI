from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("api/chat/", views.chat_api, name="chat-api"),
    path("api/chat/reset/", views.reset_chat_api, name="reset-chat-api"),
]

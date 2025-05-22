
# from django.urls import path, include
# from .views import chat_view, home_chat_view, delete_chat,start_chat

# urlpatterns = [
#     path("", home_chat_view, name="index"),
#     path("chat/<int:session_id>/", chat_view, name="chat"),
#     path("chat/<int:session_id>/delete/", delete_chat, name="delete_chat"),
#     path("start/", start_chat, name="start_chat"),

#     path("accounts/", include("allauth.urls")),
# ]


from django.urls import path, include
from .views import chat_view, home_chat_view, delete_chat, start_chat

urlpatterns = [
    path("", home_chat_view, name="index"),
    path("chat/<uuid:slug>/", chat_view, name="chat"),                # 🔄 UUID slug kullanımı
    path("chat/<uuid:slug>/delete/", delete_chat, name="delete_chat"),# 🔄 UUID slug kullanımı
    path("start/", start_chat, name="start_chat"),
    path("accounts/", include("allauth.urls")),
]

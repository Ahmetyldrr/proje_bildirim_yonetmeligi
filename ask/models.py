

from django.db import models
from django.contrib.auth.models import User  # 👈 kullanıcı modeli
import uuid


from django.db import models
import uuid
from django.contrib.auth.models import User

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, default="(Yeni Sohbet)")
    slug = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Soru: {self.question[:50]}..."  # İlk 50 karakter gösterilir



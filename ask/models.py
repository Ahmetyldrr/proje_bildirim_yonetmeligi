from django.db import models



# ask/models.py

from django.db import models
from django.contrib.auth.models import User  # 👈 kullanıcı modeli

class ChatSession(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or "(Yeni Sohbet)"   





class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Soru: {self.question[:50]}..."  # İlk 50 karakter gösterilir

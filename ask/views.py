from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import ChatSession, ChatMessage
import requests
import re


def format_answer(text):
    """
    Madde başlıklarını bold yapar, numaralı madde haline getirir ve HTML'e çevirir.
    """
    
    return text

def chat_view(request, session_id=None):
    session = None
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            session = None

    new_question = ""
    new_answer = ""
    error_message = None

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        if not request.user.is_authenticated:
            anon_key = "anon_msg_count"
            msg_count = request.session.get(anon_key, 0)
            if msg_count >= 10:
                error_message = "🔒 Giriş yapmadan en fazla 10 mesaj sorabilirsiniz. Lütfen giriş yapın."
            else:
                request.session[anon_key] = msg_count + 1

        if question and not error_message:
            # ❗ İlk kez soru geliyorsa, session yoksa burada oluşturulur
            if not session:
                session = ChatSession.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    title=question[:60]
                )
                return redirect("chat", session_id=session.id)

            try:
                response = requests.post("http://164.92.241.80:8000/ask", json={"question": question}, timeout=10)
                answer = response.json().get("answer", "Cevap alınamadı.")
                
                formatted_answer = format_answer(answer)
                ChatMessage.objects.create(
                    session=session,
                    question=question,
                    answer=formatted_answer
)

            except Exception as e:
                formatted_answer = str(e)

            ChatMessage.objects.create(session=session, question=question, answer=formatted_answer)
            new_question = question
            new_answer = formatted_answer
            return redirect("chat", session_id=session.id)

    sessions = ChatSession.objects.filter(user=request.user) if request.user.is_authenticated else ChatSession.objects.filter(user__isnull=True)
    sessions = sessions.order_by("-created_at")
    messages = session.messages.all() if session else []

    return render(request, "ask/ask_chat.html", {
        "sessions": sessions,
        "selected_session": session,
        "messages": messages,
        "new_question": new_question,
        "new_answer": new_answer,
        "error_message": error_message,
    })



@login_required
def delete_chat(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id)
    if session.user != request.user:
        return HttpResponseForbidden("Bu sohbete erişim izniniz yok.")
    session.delete()
    return redirect("index")


from django.shortcuts import redirect

def home_chat_view(request):
    # Kullanıcıya özel veya anonim sohbetler
    sessions = ChatSession.objects.filter(user=request.user) if request.user.is_authenticated else ChatSession.objects.filter(user__isnull=True)
    sessions = sessions.order_by("-created_at")

    # Eğer en az 1 sohbet varsa, en sonuncusuna yönlendir
    if sessions.exists():
        latest_session = sessions.first()
        return redirect("chat", session_id=latest_session.id)

    # Hiç sohbet yoksa sayfayı boş aç
    return render(request, "ask/ask_chat.html", {
        "sessions": sessions,
        "selected_session": None,
        "messages": [],
        "new_question": "",
        "new_answer": "",
        "error_message": ""
    })


def start_chat(request):
    # Yeni session oluştur
    session = ChatSession.objects.create(
        user=request.user if request.user.is_authenticated else None,
        title="(Yeni Sohbet)"
    )
    return redirect("chat", session_id=session.id)

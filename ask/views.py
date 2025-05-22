import re
import uuid
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import ChatSession, ChatMessage

def format_answer(text):
    """Yanıt içeriğini HTML olarak biçimlendirir."""
    lines = text.strip().split("\n")
    if not lines:
        return text

    intro = lines[0]
    items = lines[1:]
    formatted = []

    for line in items:
        match = re.match(r"^\s*(\d+)\.\s*(.+?):\s*(.+)", line)
        if match:
            _, title, desc = match.groups()
            formatted.append(f"<li><strong>{title}</strong>: {desc}</li>")
        else:
            formatted.append(f"<li>{line.strip()}</li>")

    return f"<p>{intro}</p><ol>{''.join(formatted)}</ol>"

# 👇 Ana sohbet görünümü
def chat_view(request, slug=None):
    session = get_object_or_404(ChatSession, slug=slug) if slug else None
    new_question = ""
    new_answer = ""
    error_message = None

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        # Girişsiz kullanıcılar için mesaj sınırı
        if not request.user.is_authenticated:
            anon_key = "anon_msg_count"
            msg_count = request.session.get(anon_key, 0)
            if msg_count >= 10:
                error_message = "🔒 Giriş yapmadan en fazla 10 mesaj sorabilirsiniz. Lütfen giriş yapın."
            else:
                request.session[anon_key] = msg_count + 1

        if question and not error_message:
            # İlk soruda sohbet başlat
            if not session:
                session = ChatSession.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    title=question[:60],
                    slug=uuid.uuid4()
                )
                return redirect("chat", slug=session.slug)

            try:
                response = requests.post("http://164.92.241.80:8000/ask", json={"question": question}, timeout=10)
                answer = response.json().get("answer", "Cevap alınamadı.")
                formatted_answer = format_answer(answer)
            except Exception as e:
                formatted_answer = str(e)

            ChatMessage.objects.create(session=session, question=question, answer=formatted_answer)

            # Başlığı güncelle (ilk soruda başlıksız oluşturulmuşsa)
            if session.messages.count() == 1 and session.title == "(Yeni Sohbet)":
                session.title = question[:60]
                session.save()

            return redirect("chat", slug=session.slug)

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

# 👇 Giriş ekranı gibi davranan yönlendirme
def home_chat_view(request):
    sessions = ChatSession.objects.filter(user=request.user) if request.user.is_authenticated else ChatSession.objects.filter(user__isnull=True)
    sessions = sessions.order_by("-created_at")
    if sessions.exists():
        return redirect("chat", slug=sessions.first().slug)

    return render(request, "ask/ask_chat.html", {
        "sessions": sessions,
        "selected_session": None,
        "messages": [],
        "new_question": "",
        "new_answer": "",
        "error_message": ""
    })

# 👇 Yeni sohbet başlat
def start_chat(request):
    session = ChatSession.objects.create(
        user=request.user if request.user.is_authenticated else None,
        title="(Yeni Sohbet)",
        slug=uuid.uuid4()
    )
    return redirect("chat", slug=session.slug)

# 👇 Silme işlemi
@login_required
def delete_chat(request, slug):
    session = get_object_or_404(ChatSession, slug=slug)
    if session.user != request.user:
        return HttpResponseForbidden("Bu sohbete erişim izniniz yok.")
    session.delete()
    return redirect("index")

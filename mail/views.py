import imaplib
import email
from email.header import decode_header
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test


def is_staff(user):
    return user.is_staff


@user_passes_test(is_staff)
def mail_index(request):
    """Отображает список последних сообщений из папки INBOX."""
    emails = []
    error = None
    
    try:
        # Подключение к IMAP
        mail = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
        mail.login(settings.IMAP_USER, settings.IMAP_PASSWORD)
        mail.select("inbox")
        
        # Поиск последних 10 сообщений
        status, messages_ids = mail.search(None, "ALL")
        if status == "OK":
            id_list = messages_ids[0].split()
            # Берем последние 10
            latest_ids = id_list[-10:]
            latest_ids.reverse()
            
            for msg_id in latest_ids:
                res, msg_data = mail.fetch(msg_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Декодирование темы
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8", errors="replace")
                        
                        # Декодирование отправителя
                        from_, encoding = decode_header(msg.get("From"))[0]
                        if isinstance(from_, bytes):
                            from_ = from_.decode(encoding if encoding else "utf-8", errors="replace")
                        
                        date = msg.get("Date")
                        
                        emails.append({
                            "id": msg_id.decode(),
                            "subject": subject,
                            "from": from_,
                            "date": date,
                        })
        mail.logout()
    except imaplib.IMAP4.error as e:
        error_msg = str(e)
        if "AUTHENTICATIONFAILED" in error_msg:
            error = "Ошибка авторизации: неверный логин или пароль (AUTHENTICATIONFAILED). Проверьте настройки EMAIL_HOST_USER и EMAIL_HOST_PASSWORD в файле .env."
        else:
            # Пытаемся декодировать байтовый вывод, если он есть
            if isinstance(e.args[0], bytes):
                error_msg = e.args[0].decode('utf-8', errors='replace')
            error = f"Ошибка IMAP: {error_msg}"
    except Exception as e:
        error = str(e)

    context = {
        "emails": emails,
        "error": error,
        "imap_host": settings.IMAP_HOST,
        "smtp_host": settings.EMAIL_HOST,
        "user_email": settings.EMAIL_HOST_USER,
    }
    return render(request, "mail/index.html", context)


@user_passes_test(is_staff)
def send_test_email(request):
    """Отправляет тестовое письмо."""
    if request.method == "POST":
        recipient = request.POST.get("recipient")
        if recipient:
            try:
                send_mail(
                    "Тестовое письмо от DPIT-CMS",
                    "Это тестовое письмо, подтверждающее правильность настроек SMTP.",
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient],
                    fail_silently=False,
                )
                messages.success(request, f"Тестовое письмо успешно отправлено на {recipient}")
            except Exception as e:
                messages.error(request, f"Ошибка при отправке: {str(e)}")
        else:
            messages.warning(request, "Укажите email получателя")
            
    return redirect("mail:index")

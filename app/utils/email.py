import smtplib
from email.message import EmailMessage

from app.config import settings


def send_verification_email(to_email: str, code: str) -> None:
    """Send a 6-digit verification code via SMTP."""
    msg = EmailMessage()
    msg["Subject"] = "WhatToEat - Your Verification Code"
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg.set_content(f"Your verification code is: {code}\n\nThis code expires in 6 minutes.")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)

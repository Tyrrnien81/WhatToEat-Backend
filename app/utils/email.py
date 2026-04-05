import smtplib
from email.message import EmailMessage

from app.config import settings


def _send_email(to_email: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


def send_verification_email(to_email: str, code: str) -> None:
    """Send a 6-digit verification code via SMTP."""
    subject = "WhatToEat - Your Verification Code"
    body = (
        f"Your verification code is: {code}\n\n"
        "This code expires in 6 minutes."
    )
    _send_email(to_email, subject, body)


def send_reset_password_email(to_email: str, reset_link: str) -> None:
    """Send a password reset link via SMTP."""
    subject = "WhatToEat - Reset Your Password"
    body = (
        "We received a request to reset your password.\n\n"
        f"Click the link below to reset your password:\n{reset_link}\n\n"
        "This link expires in 30 minutes.\n\n"
        "If you did not request a password reset, you can ignore this email."
    )
    _send_email(to_email, subject, body)
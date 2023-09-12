import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from smail import sign_message

from perun.proxygui.jwt import JWTService


class EmailService:
    def __init__(self, cfg):
        self.__SMTP_SERVER = cfg["mfa_reset"]["smtp_server"]
        self.__SMTP_PORT = cfg["mfa_reset"]["smtp_port"]
        self.__CERT_FILE = cfg["mfa_reset"]["cert_filepath"]
        self.__HELPDESK_EMAIL = cfg["mfa_reset"]["helpdesk_mail"]
        self.__PRIVATE_KEY = cfg["mfa_reset"]["private_key_filepath"]
        self.__TRANSLATIONS = cfg["mfa_reset_translations"]["sections"]
        self.__JWT_SERVICE = JWTService(cfg)
        self.__LOGIN_EMAIL = None
        self.__LOGIN_PASS = None

        credentials_path = cfg["mfa_reset"].get("mail_login_credentials_filepath")
        if credentials_path and os.path.exists(credentials_path):
            with open(credentials_path, "r") as credentials:
                self.__LOGIN_EMAIL, self.__LOGIN_PASS = credentials.read().split("\n")

    def __send_email_message(self, message: MIMEMultipart) -> None:
        with smtplib.SMTP(self.__SMTP_SERVER, self.__SMTP_PORT) as smtp_server:
            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.ehlo()
            if self.__LOGIN_EMAIL and self.__LOGIN_PASS:
                smtp_server.login(self.__LOGIN_EMAIL, self.__LOGIN_PASS)
            smtp_server.send_message(message)

    def __send_signed_email_message(self, message: MIMEMultipart) -> None:
        signed_message = sign_message(message, self.__PRIVATE_KEY, self.__CERT_FILE)

        self.__send_email_message(signed_message)

    def send_mfa_reset_link(
        self, recipient_email: str, locale: str, mfa_reset_verify_url: str
    ) -> None:
        message = MIMEMultipart("related")
        message["From"] = self._LOGIN_EMAIL
        message["Subject"] = self.__TRANSLATIONS[locale]["reset_link_email_subject"]
        message["To"] = recipient_email
        jwt = self.__JWT_SERVICE.get_jwt({"requester_email": recipient_email})

        message_content = (
            self.__TRANSLATIONS[locale]["reset_link_email_content"]
            + f" {mfa_reset_verify_url}/{jwt}"
        )

        message.attach(MIMEText(message_content, "plain", _charset="UTF-8"))

        self.__send_signed_email_message(message)

    def send_mfa_reset_notification(
        self, recipient_emails: List[str], locale: str
    ) -> None:
        message = MIMEMultipart("related")
        message["From"] = self._LOGIN_EMAIL
        message["Subject"] = self.__TRANSLATIONS[locale][
            "reset_notification_email_subject"
        ]
        message["To"] = ", ".join(recipient_emails)
        message_content = self.__TRANSLATIONS[locale][
            "reset_notification_email_content"
        ]

        message.attach(MIMEText(message_content, "plain", _charset="UTF-8"))

        self.__send_signed_email_message(message)

    def send_mfa_reset_request(self, requester_email: str):
        message = MIMEMultipart("related")
        message["From"] = self._LOGIN_EMAIL
        message["Subject"] = "MFA reset request"
        message["To"] = self.__HELPDESK_EMAIL
        message_content = (
            f"Partly verified user with email '"
            f"{requester_email}' has requested a reset of "
            f"their Multi-Factor Authentication."
        )

        message.attach(MIMEText(message_content, "plain", _charset="UTF-8"))

        self.__send_signed_email_message(message)

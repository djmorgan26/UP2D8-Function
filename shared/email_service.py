import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional, List
import structlog

logger = structlog.get_logger()

class EmailMessage:
    """Standard email message structure"""

    def __init__(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ):
        self.to = to
        self.subject = subject
        self.html_body = html_body
        self.text_body = text_body
        self.from_email = from_email
        self.reply_to = reply_to
        self.cc = cc or []
        self.bcc = bcc or []

class SMTPProvider:
    """
    SMTP email provider (FREE - works with Gmail, etc.)
    Supports standard SMTP protocol
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        use_tls: bool = True
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.use_tls = use_tls

    def send_email(self, message: EmailMessage) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = message.from_email or self.smtp_username
            msg['To'] = message.to

            # Add both plain text and HTML parts
            if message.text_body:
                text_part = MIMEText(message.text_body, 'plain')
                msg.attach(text_part)

            html_part = MIMEText(message.html_body, 'html')
            msg.attach(html_part)

            # Connect and send
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)

            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(msg['From'], [message.to], msg.as_string())
            server.quit()

            logger.info("email_sent_via_smtp", to=message.to, subject=message.subject)
            return True

        except Exception as e:
            logger.error("smtp_send_failed", error=str(e), to=message.to)
            return False

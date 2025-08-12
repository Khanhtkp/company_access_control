import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
class EmailService:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
        self.server = smtp_server
        self.port = smtp_port
        self.user = smtp_user
        self.password = smtp_password

    def send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg['From'] = self.user
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.server, self.port) as server:
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)
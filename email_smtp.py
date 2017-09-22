import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# SMTP Email connection information
SMTP_SERVER_AND_PORT = 'smtp.server.com:587'
SMTP_USERNAME = 'youremailaccount'
SMTP_PASSWORD = 'youremailpassword'
FROM_EMAIL = 'youremailaddress@hotmail.com'


def send_email(to_email, to_name, from_email, subject, text_msg, html_msg):
    """
    Sends email using smtp.
    :param to_email:
    :param to_name:
    :param from_email:
    :param subject:
    :param text_msg:
    :param html_msg:
    :return: True to indicate that the email has been sent.
    """
    server = smtplib.SMTP(SMTP_SERVER_AND_PORT)
    server.ehlo()
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    text_part = MIMEText(text_msg, 'plain')
    html_part = MIMEText(html_msg, 'html')

    msg.attach(text_part)
    msg.attach(html_part)

    server.send_message(msg, from_email, to_email)
    server.quit()
    return True

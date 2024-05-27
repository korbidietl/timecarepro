import smtplib
from email.mime.text import MIMEText


def send_email(email, subject, body):
    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = 'support@timecarepro.de'
    msg['To'] = email

    with smtplib.SMTP('132.231.36.210', 1103) as smtp:
        smtp.login('mailhog_grup3', 'Uni75Winfo17Master')
        smtp.sendmail('support@timecarepro.de', [email], msg.as_string())

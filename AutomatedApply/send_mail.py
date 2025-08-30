import smtplib
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

sender_email = os.getenv("FROM_MAIL")
receiver_email = os.getenv("TO_MAIL")
password = os.getenv("MAIL_PASSWORD")

def send_mail():
    """
    Sends a confirmation email via Gmail SMTP after successful form/API submission.
    - Uses environment variables for sender, receiver, and app password
    - Sends a short success message if credentials are valid
    - Logs success or failure accordingly
    Returns:
        None
    """
    if not all([sender_email, receiver_email, password]):
        logger.warning("❌️ Mail-Konfiguration unvollständig. Kein Versand.")
        return

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as connection:
            connection.starttls()
            connection.login(user=sender_email, password=password)
            connection.sendmail(
                from_addr=sender_email,
                to_addrs=receiver_email,
                msg="Subject:Zeilen erfolgreich\n\nYour Google Sheet is ready."
            )
        logger.info("Bestätigungsmail erfolgreich gesendet an %s", receiver_email)

    except smtplib.SMTPException:
        logger.exception("❌ Fehler beim Senden der E-Mail über SMTP")

    except Exception:
        logger.exception("❌ Unerwarteter Fehler beim E-Mail-Versand")









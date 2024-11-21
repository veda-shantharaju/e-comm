from twilio.rest import Client
from django.conf import settings

def send_sms(to, message):
    """
    Sends an SMS to the specified phone number using Twilio.
    :param to: Recipient's phone number (in E.164 format, e.g., +919876543210)
    :param message: Message content
    """
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.TWILIO_PHONE_NUMBER

    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=message,
            from_=from_number,
            to=to
        )
        print(f"SMS sent successfully to {to}")
    except Exception as e:
        print(f"Failed to send SMS to {to}: {e}")
        raise

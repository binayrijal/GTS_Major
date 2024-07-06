from django.core.mail import EmailMessage
import os
import hmac
import hashlib




class Util:
    @staticmethod
    def send_mail(data):
        email=EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=os.environ.get('EMAIL_FROM'),
            to=[data['to_email']]
        )

        email.send()
        

def generate_signature(data, secret_key):
    message = '&'.join([f"{key}={data[key]}" for key in sorted(data.keys())])
    signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature
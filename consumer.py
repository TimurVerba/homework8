import json
import pika
from mongoengine import connect, Document, StringField, BooleanField

# Підключення до бази даних MongoDB
connect(db="web16",
        host="mongodb+srv://verbatimur:Whyweneedsteam123@cluster0.le2ds3c.mongodb.net/?retryWrites=true&w=majority")


# Модель для контакту
class Contact(Document):
    full_name = StringField(required=True)
    email = StringField(required=True)
    phone_number = StringField()
    sent_email = BooleanField(default=False)
    sent_sms = BooleanField(default=False)


# З'єднання з RabbitMQ для email
connection_email = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel_email = connection_email.channel()
channel_email.queue_declare(queue='email_queue')

# З'єднання з RabbitMQ для SMS
connection_sms = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel_sms = connection_sms.channel()
channel_sms.queue_declare(queue='sms_queue')


def send_email(contact_id):
    # Заглушка для відправлення електронної пошти
    print(f"Відправлення електронної пошти контакту з ID {contact_id}")
    # Можете розширити цю функцію залежно від реальної логіки надсилання email
    return None


def send_sms(contact_id):
    # Заглушка для відправлення SMS
    print(f"Відправлення SMS контакту з ID {contact_id}")
    # Можете розширити цю функцію залежно від реальної логіки надсилання SMS
    return None


def callback_email(ch, method, properties, body):
    contact_data = json.loads(body)
    contact_id = contact_data['contact_id']
    contact = Contact.objects.get(id=contact_id)
    send_email(contact)


def callback_sms(ch, method, properties, body):
    contact_data = json.loads(body)
    contact_id = contact_data['contact_id']
    contact = Contact.objects.get(id=contact_id)
    send_sms(contact)


# Встановлення обробників для черг email та SMS
channel_email.basic_consume(queue='email_queue', on_message_callback=callback_email, auto_ack=True)
channel_sms.basic_consume(queue='sms_queue', on_message_callback=callback_sms, auto_ack=True)

print("Очікування повідомлень. Для виходу натисніть CTRL+C.")

# Запуск обробників в нескінченному циклі
try:
    channel_email.start_consuming()
except KeyboardInterrupt:
    channel_email.stop_consuming()
    connection_email.close()

try:
    channel_sms.start_consuming()
except KeyboardInterrupt:
    channel_sms.stop_consuming()
    connection_sms.close()

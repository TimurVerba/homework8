import json
import faker
import pika
from mongoengine import connect, Document, StringField, BooleanField

# Підключення до бази даних MongoDB
connect(db="web16", host="mongodb+srv://verbatimur:Whyweneedsteam123@cluster0.le2ds3c.mongodb.net/?retryWrites=true&w=majority")

# Модель для контакту
class Contact(Document):
    full_name = StringField(required=True)
    email = StringField(required=True)
    phone_number = StringField()
    sent_email = BooleanField(default=False)
    sent_sms = BooleanField(default=False)

# З'єднання з RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Оголошення черги для email
channel.queue_declare(queue='email_queue')

# Оголошення черги для SMS
channel.queue_declare(queue='sms_queue')

# Генератор фейкових контактів
fake = faker.Faker()

# Кількість контактів для створення
num_contacts = 10

for _ in range(num_contacts):
    # Генерація фейкового контакту
    contact = Contact(
        full_name=fake.name(),
        email=fake.email(),
        phone_number=fake.phone_number()
    )
    contact.save()

    # Отримання ID створеного контакту
    contact_id = str(contact.id)

    # Відправлення ID контакту у чергу для email
    channel.basic_publish(exchange='',
                          routing_key='email_queue',
                          body=json.dumps({'contact_id': contact_id}))

    # Відправлення ID контакту у чергу для SMS
    channel.basic_publish(exchange='',
                          routing_key='sms_queue',
                          body=json.dumps({'contact_id': contact_id}))

print(f"{num_contacts} контактів створено та відправлено у черги.")

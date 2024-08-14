import os
import django
import pika
import json
import time
from datetime import datetime

time.sleep(5)

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interpolData.settings')

# Initialize Django
django.setup()

from interpolApp.models import Notice

def consume():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='host.docker.internal'))
    channel = connection.channel()
    channel.queue_declare(queue='interpol_notices')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        update_notices(data)

    channel.basic_consume(queue='interpol_notices', on_message_callback=callback, auto_ack=True)
    print('Waiting for messages. To exit press CTRL+C or CONTROL+C')
    channel.start_consuming()

def update_notices(data):
    notices = data.get("notices", [])
    for notice in notices:
        entity_id = notice.get("entity_id")
        if not entity_id:
            continue

        date_of_birth = notice.get("date_of_birth")
        if date_of_birth:
            try:
                date_of_birth = datetime.strptime(date_of_birth, "%Y/%m/%d").date()
            except ValueError:
                date_of_birth = None

        nationalities = notice.get("nationalities")
        forename = notice.get("forename")
        name = notice.get("name")
        links = notice.get("_links", {})
        self_url = links.get("self", {}).get("href")
        images_url = links.get("images", {}).get("href")
        thumbnail_url = links.get("thumbnail", {}).get("href")

        # Update or create a new record
        notice_obj, created = Notice.objects.update_or_create(
            entity_id=entity_id,
            defaults={
                'date_of_birth': date_of_birth,
                'forename': forename,
                'name': name,
                'nationalities': nationalities,
                'self_url': self_url,
                'images_url': images_url,
                'thumbnail_url': thumbnail_url
            }
        )

        notice_obj.created = created
        notice_obj.save()

if __name__ == "__main__":
    consume()

import pika
import json

def send_notification(queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    print(f"Sent notification to {queue_name}: {message}")
    connection.close()


message = {'booking_id': 1, 'user_id': 'NVqPLXexIFUr3loYRl1GJgkfAep2'}
json_message = json.dumps(message)
print(json_message)
send_notification('booking_confirmations', json_message)
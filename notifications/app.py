import pika
import json

def send_notification(queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    print(f"Sent notification to {queue_name}: {message}")
    connection.close()

def booking_confirmation_callback(ch, method, properties, body):
    print("Received booking confirmation notification:", body)
    # Decode the body from bytes to string
    body_str = body.decode('utf-8')
    
    # Parse the JSON string into a Python dictionary
    booking_data = json.loads(body_str)
    
    # Now you can access the fields of the JSON object as dictionary keys
    print("Received booking confirmation notification:")
    print("Booking ID:", booking_data.get('booking_id'))
    # print("User ID:", booking_data.get('user_id'))
    # print("Status:", booking_data.get('status'))
    # Add more fields as needed

def car_ready_callback(ch, method, properties, body):
    print("Received car ready notification:", body)

def car_collected_callback(ch, method, properties, body):
    print("Received car collected notification:", body)

def booking_cancellation_callback(ch, method, properties, body):
    print("Received booking cancellation notification:", body)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Scenario 1: Booking Confirmation Notification
    channel.queue_declare(queue='booking_confirmations')
    channel.basic_consume(queue='booking_confirmations', on_message_callback=booking_confirmation_callback, auto_ack=True)

    # Scenario 2: Car Ready for Collection Notification
    channel.queue_declare(queue='car_ready_notifications')
    channel.basic_consume(queue='car_ready_notifications', on_message_callback=car_ready_callback, auto_ack=True)

    # Scenario 3: Car Collected Notification
    channel.queue_declare(queue='car_collected_notifications')
    channel.basic_consume(queue='car_collected_notifications', on_message_callback=car_collected_callback, auto_ack=True)

    # Scenario 4: Booking Cancellation Notification
    channel.queue_declare(queue='booking_cancellation_notifications')
    channel.basic_consume(queue='booking_cancellation_notifications', on_message_callback=booking_cancellation_callback, auto_ack=True)

    print('Waiting for notifications...')
    channel.start_consuming()

if __name__ == "__main__":
    main()

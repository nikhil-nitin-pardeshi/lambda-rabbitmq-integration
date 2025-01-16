import json
import pika
import os
from dotenv import load_dotenv
load_dotenv()

def lambda_handler(event, context):
    rmq_password = rabbitmq_details_using_vault()
    try:
        if 'body' in event :
            message = json.loads(event['body'])
            if publish_to_rabbitmq(message, rmq_password):
                return {
                    'statusCode': 200,
                    'body': 'Message successfully sent to RabbitMQ.'
                }
            else:
                return {
                    'statusCode': 500,
                    'body': 'Failed to connect to RabbitMQ.'
                }
        else:
            return {
                'statusCode': 400,
                'body': 'No message body or source queue ARN found in the request.'
            }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': 'Invalid JSON in the request body.'
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f"An error occurred: {e}"
        }


def rabbitmq_details_using_vault():
    return os.getenv('RMQ_PASSWORD')

def publish_to_rabbitmq( message, rmq_password ):
    print("Message Body:", json.dumps(message))
    rabbitmq_host = os.getenv('RMQ_HOST')
    rabbitmq_port = int(os.getenv('RMQ_PORT'))
    rabbitmq_user = os.getenv('RMQ_USERNAME')
    rabbitmq_password = rmq_password
    rabbitmq_virtual_host = os.getenv('RMQ_VHOST')
    print(f"Host: {rabbitmq_host}, Port: {rabbitmq_port}, User: {rabbitmq_user}, VHost: {rabbitmq_virtual_host}")
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        virtual_host=rabbitmq_virtual_host,
        credentials=credentials
    )
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        rabbitmq_queue = os.getenv('RABBITMQ_QUEUE')
        exchange_name = os.getenv('QUEUE_EXCHANGE_NAME')
        channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)
        channel.queue_declare(queue=rabbitmq_queue, durable=True)
        channel.queue_bind(exchange=exchange_name, queue=rabbitmq_queue)
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=rabbitmq_queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print("Message published to RabbitMQ")
        channel.close()
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        return False
    except pika.exceptions.StreamLostError as e:
        print(f"StreamLostError: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
    return True



# For local testing
if __name__ == "__main__":
    with open("test_event.json", "r") as f:
        test_event = json.load(f)

    response = lambda_handler(test_event, None)
    print(json.dumps(response, indent=4))
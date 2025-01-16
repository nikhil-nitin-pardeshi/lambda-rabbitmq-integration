import json
import boto3
import botocore
import pika
import os
from dotenv import load_dotenv
load_dotenv()

def lambda_handler(event, context):
    try:
        if 'body' in event :
            message = json.loads(event['body'])
            if send_to_rabbitmq(message):
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


def rabbitmq_details_using_secrets_manager():
    try:
        secret_name = os.getenv['AWS_SECRET_MANAGER_KEY_NAME']
        region_name = os.getenv['AWS_REGION']

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
        else:
            secret = json.loads(get_secret_value_response['SecretBinary'])
        
        print("Retrieved secret:", secret)
        rabbitmq_details = {
            'host': secret['RMQ_HOST'],
            'port': int(secret['RMQ_PORT']),
            'username': secret['RMQ_USERNAME'],
            'password': secret['RMQ_PASSWORD'],
            'virtual_host': secret['RMQ_VHOST']
        }
        return rabbitmq_details
    except botocore.exceptions.ClientError as err:
        print(f'Error getting RabbitMQ details from Secrets Manager: {err}')
        return None
    except json.JSONDecodeError as err:
        print(f'Error decoding the secret value: {err}')
        return None
    except Exception as err:
        print(f'An unexpected error occurred: {err}')
        return None

def send_to_rabbitmq(message):
    print("Message Body:", json.dumps(message))
    rabbitmq_details = rabbitmq_details_using_secrets_manager()
    if not rabbitmq_details:
        return False
        
    print('Retrieved RabbitMQ details:')
    print(f"Host: {rabbitmq_details['host']}")
    print(f"Port: {rabbitmq_details['port']}")
    print(f"Username: {rabbitmq_details['username']}")
    print(f"Virtual Host: {rabbitmq_details['virtual_host']}")
    
    credentials = pika.PlainCredentials(rabbitmq_details['username'], rabbitmq_details['password'])
    parameters = pika.ConnectionParameters(
        host=rabbitmq_details['host'],
        port=rabbitmq_details['port'],
        virtual_host=rabbitmq_details['virtual_host'],
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
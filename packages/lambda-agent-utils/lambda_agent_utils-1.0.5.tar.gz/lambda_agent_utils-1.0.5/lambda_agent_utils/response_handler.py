import json
import os
from kafka import KafkaProducer
from dotenv import load_dotenv
load_dotenv()

def response(data, metadata):
    try:
        if metadata['trigger_source'] == 'api-gateway':
            return  {
                'statusCode': 200,
                'body': json.dumps({'data': data, 'source': metadata['trigger_source'] }),
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        elif metadata['trigger_source'] == 'aws-service-kafka':
            # send data to Kafka topic (You can implement this part)
            kafka_brokers = os.environ.get('KAFKA_BROKERS')
            try:
                producer = KafkaProducer(bootstrap_servers=kafka_brokers)
                producer.send(metadata['kafka_toic'], key=metadata['id'], value=data)

                # Wait for any outstanding messages to be delivered and delivery reports to be received
                producer.flush()
                return {
                    'statusCode': 200,
                    'body': 'Message sent to Kafka topic successfully.'
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'body': f'Error: {str(e)}'
                }

        elif metadata['trigger_source'] == 'cli':
            return {'data': data, 'source': metadata['trigger_source'] }
        else:
            raise Exception("Unexpected trigger source.")
    except Exception as e:
        raise Exception(e)
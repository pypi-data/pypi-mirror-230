import json

def get_input(event):
    try:
        trigger_source = None
        input_params = None

        if 'httpMethod' in event and event['httpMethod'] == 'POST':
            trigger_source = 'api-gateway'
            if 'body' in event:
                input_params = json.loads(event['body'])
        elif 'Records' in event and isinstance(event['Records'], list):
            trigger_source = 'aws-service-kafka'
            for record in event['Records']:
                if 'kafka' in record:
                    kafka_record = json.loads(record['kafka']['data'])
                    input_params = kafka_record['message']
        elif 'source' in event and event['source'] == 'cli':
            trigger_source = 'cli'
            input_params = event
        else:
            raise Exception("Input is not valid.")

        return { 'input': input_params, 'source': trigger_source }
    except Exception as e:
        raise Exception(e)

import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os

bucket_name = 'amichai-dfs-data'

aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

def increment_feed_version():
    dynamodb = boto3.resource('dynamodb', 
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name='us-east-1')

    # Specify the table
    table = dynamodb.Table('MLE_data')

    # Get the item
    response = table.get_item(
        Key={
            'key': 'v'
        }
    )

    item = response.get('Item', {})
    print(item)

    oldCount = int(item.get('ct', '0'))

    response = table.update_item(
        Key={
            'key': 'v'
        },
        UpdateExpression="SET ct = :val",
        ExpressionAttributeValues={
            ':val': str(oldCount + 1)
        },
        ReturnValues="UPDATED_NEW"
    )

    print(response)


s3 = boto3.client('s3',
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key,
                  region_name='us-east-1')

def write_file(content, name):
    try:
        result = s3.put_object(Body=content, Bucket=bucket_name, Key=name)
        print(result)
    except ClientError as e:
        print('ClientError writing file {}: {}'.format(name, e))
    except BotoCoreError as e:
        print('BotoCoreError writing file {}: {}'.format(name, e))
    except Exception as e:
        print('Unexpected error writing file {}: {}'.format(name, e))

def read_file(name):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=name)
        content = response['Body'].read().decode('utf-8')
        return content
    except ClientError as e:
        print('ClientError reading file {}: {}'.format(name, e))
        return ''
    except BotoCoreError as e:
        print('BotoCoreError reading file {}: {}'.format(name, e))
        return None
    except Exception as e:
        print('Unexpected error reading file {}: {}'.format(name, e))
        return None
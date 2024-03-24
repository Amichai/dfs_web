import json
import boto3
import os
from datetime import datetime, timedelta
from urllib.parse import unquote

ip_to_username = {
'108.21.80.185': 'aml2',
'108.31.232.24': 'objcehdk',
'108.41.137.35': 'momomchine',
'96.63.209.101': 'asmithii2287',
'136.50.116.194': 'apatelg',
'174.198.196.149': 'kinghaas43',
'206.75.108.62': 'korupt123',
}


aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# DynamoDB setup
dynamodb = boto3.resource('dynamodb', 
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name='us-east-1')
table = dynamodb.Table('MLE_analytics_v2')

# n = 2
# n_days_ago = int((datetime.now() - timedelta(days=n)).timestamp()) * 1000
# print(n_days_ago)

# response = table.scan()

# prefix = '17110'

event_date = '2024-03-23'
scan_kwargs = {
  # 'FilterExpression': 'begins_with(#ts, :val)',
  # 'ExpressionAttributeNames': {
  #     '#ts': 'timestamp',  # Maps '#ts' to the reserved keyword 'timestamp'
  # },
  # 'ExpressionAttributeValues': {
  #     ':val': prefix,
  # }
  'IndexName': 'date-index',
  'KeyConditionExpression': '#dt = :event_date',
  'ExpressionAttributeValues': {
    ':event_date': event_date,
  },
  'ExpressionAttributeNames': {
    '#dt': 'date',
  }
}

all_items = []
start_key = None
while True:
  if start_key:
    scan_kwargs['ExclusiveStartKey'] = start_key
    
  response = table.query(**scan_kwargs)
  items = response.get('Items', [])
  all_items.extend(items)
  start_key = response.get('LastEvaluatedKey', None)
  if not start_key:
    break
  
sorted_by_time = sorted(all_items, key=lambda x: x['Timestamp'])

for item in sorted_by_time:
  cip = item['ip']
  if cip in ip_to_username:
    cip = ip_to_username[cip]
  tp = item['type']
  ts = item['Timestamp']
  dt = datetime.fromtimestamp(int(ts) / 1000)
  val = item['value']
  # Format the datetime object to a string in a readable format
  human_readable = dt.strftime('%Y-%m-%d %H:%M:%S')
  print(f'{human_readable} - Client: {cip}, Type: {tp}')
  table = unquote(val)
  print(table)
  
  print('-----')
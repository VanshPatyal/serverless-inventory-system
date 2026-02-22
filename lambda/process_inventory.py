import json
import boto3
import csv
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

INVENTORY_TABLE = os.environ.get('INVENTORY_TABLE', 'inventory')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    """
    Process CSV file uploaded to S3 and update inventory in DynamoDB
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Get bucket and key from S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        print(f"Processing file: {key} from bucket: {bucket}")
        
        # Download CSV file from S3
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket, Key=key)
        csv_content = response['Body'].read().decode('utf-8').splitlines()
        
        # Parse CSV and update DynamoDB
        csv_reader = csv.DictReader(csv_content)
        inventory_table = dynamodb.Table(INVENTORY_TABLE)
        
        low_stock_items = []
        
        for row in csv_reader:
            item = {
                'product_id': row['product_id'],
                'product_name': row['product_name'],
                'quantity': int(row['quantity']),
                'reorder_level': int(row.get('reorder_level', 10)),
                'price': Decimal(str(row.get('price', '0.00')))
            }
            
            # Update inventory in DynamoDB
            inventory_table.put_item(Item=item)
            
            # Check if low stock
            if item['quantity'] < item['reorder_level']:
                low_stock_items.append(item)
        
        # Send SNS alerts for low stock items
        if low_stock_items and SNS_TOPIC_ARN:
            message = "Low Stock Alert!\n\n"
            for item in low_stock_items:
                message += f"Product: {item['product_name']} (ID: {item['product_id']})\n"
                message += f"Current Quantity: {item['quantity']}\n"
                message += f"Reorder Level: {item['reorder_level']}\n\n"
            
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='Inventory Low Stock Alert',
                Message=message
            )
            
            print(f"Sent low stock alerts for {len(low_stock_items)} items")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed {len(list(csv_reader))} items',
                'low_stock_count': len(low_stock_items)
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

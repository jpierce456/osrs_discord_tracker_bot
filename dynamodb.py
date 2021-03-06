import boto3
from decimal import Decimal

def describe_table(table_name, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.client('dynamodb')
    return dynamodb.describe_table(TableName=table_name)

def add_osrs_account_to_table(account_stats, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('osrs_account_stats')
    response = table.put_item(Item=account_stats)
    return response

def remove_osrs_account_from_table(account_name, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('osrs_account_stats')
    response = table.delete_item(Key={'account_name': account_name})
    return response

def get_all_accounts(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('osrs_account_stats')
    response = table.scan()
    return response

def get_account(account_name, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('osrs_account_stats')
    try:
        response = table.get_item(
            Key={
                'account_name': account_name
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response

def in_table(account_name, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('osrs_account_stats')
    response = table.get_item(
        Key={
            'account_name': account_name
        }
    )
    return 'Item' in response

def add_follower(account_name, follower, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('osrs_account_stats')

    response = table.update_item(
        Key={
            'account_name': account_name
        },
        UpdateExpression='SET followers = list_append(followers, :i)',
        ExpressionAttributeValues={
            ':i': [follower],
        },
        ReturnValues='UPDATED_NEW'
    )
    return response

def remove_follower(account_name, follower, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('osrs_account_stats')

    response = get_account(account_name, dynamodb)
    followers = response['Item']['followers']
    list_index = followers.index(follower)

    response = table.update_item(
        Key={
            'account_name': account_name
        },
        UpdateExpression=f'REMOVE followers[{list_index}]',
        ReturnValues='UPDATED_NEW'
    )
    return response

def update_attribute(account_name, attribute, data, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('osrs_account_stats')

    response = table.update_item(
        Key={
            'account_name', account_name
        },
        UpdateExpression=f'SET {attribute}'

    )

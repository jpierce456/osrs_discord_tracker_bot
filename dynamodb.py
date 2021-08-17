import boto3
from decimal import Decimal

def get_osrs_table():
    db = boto3.resource('dynamodb')
    table = db.Table('osrs_account_stats')
    return table

def add_to_table(account_stats):
    table = get_osrs_table()
    table.put_item(Item=account_stats)

def remove_from_table(account_name):
    table = get_osrs_table()
    table.delete_item(Key={'account_name': account_name})

def get_account(account_name):
    table =get_osrs_table()
    response = table.get_item(
        Key={
            'account_name': account_name
        }
    )
    return response

def in_table(account_name):
    table = get_osrs_table()
    response = table.get_item(
        Key={
            'account_name': account_name
        }
    )
    return 'Item' in response

def add_follower(account_name, follower):
    table = get_osrs_table()
    table.update_item(
        Key={
            'account_name': account_name
        },
        UpdateExpression='SET followers = list_append(followers, :i)',
        ExpressionAttributeValues={
            ':i': [follower],
        },
        ReturnValues='UPDATED_NEW'
    )

def remove_follower(account_name, follower):
    table = get_osrs_table()
    table.update_item(
        Key={
            'account_name': account_name
        },
        UpdateExpression=f'REMOVE followers[{list_index}]',
        ReturnValues='UPDATED_NEW'
    )

def get_attribute(account_name, attribute):
    table = get_osrs_table()
    response = get_account(account_name)
    if 'Item' not in response: # there is no account with that name
        return None
    elif attribute not in response['Item']: # account does not have that attribute
        return None
    else:
        return response['Item'][attribute]

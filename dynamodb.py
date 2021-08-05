import boto3

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
    account_stats = table.get_item(
        Key={
            'account_name': account_name
        },
        ProjectionExpression='followers'
    )
    followers_list = account_stats['Item']['followers']
    index = followers_list.index(follower)
    print(index)
    table.update_item(
        Key={
            'account_name': account_name
        },
        UpdateExpression='REMOVE followers[:i]',
        ExpressionAttributeValues={
            ':i': index,
        },
        ReturnValues='UPDATED_NEW'
    )

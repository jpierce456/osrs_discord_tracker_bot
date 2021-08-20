import http.client
import math
from sys import exit
import time
import boto3
from osrs_mapping import skills, activities, bosses
import dynamodb
import status



def format_account_stats_json(account_data):
    """
    Input is the ordered list of numbers from the Old School Runescape
    hiscores api
    Output is the same data formatted in a json with key values
    corresponding to the data.
    """
    counter = 0
    skills_mapping = {}
    activities_mapping = {}
    bosses_mapping = {}
    for i in range(len(skills)):
        if account_data[counter] != '-1':
            skills_mapping[skills[i]] = {'rank': int(account_data[counter]),
                                         'level': int(account_data[counter+1]),
                                         'experience': int(account_data[counter+2])
        }
        counter+=3

    for i in range(len(activities)):
        if account_data[counter] != '-1':
            activities_mapping[activities[i]] = {'rank': int(account_data[counter]),
                                                 'score': int(account_data[counter+1])
            }
        counter+=2

    for i in range(len(bosses)):
        if account_data[counter] != '-1':
            bosses_mapping[bosses[i]] = {'rank': int(account_data[counter]),
                                         'score': int(account_data[counter+1])
            }
        counter+=2
    return {'skills': skills_mapping,
            'activities': activities_mapping,
            'bosses': bosses_mapping
    }

def get_account_stats(account_name):
    """
    Input is the name of the account being looked up
    The method accesses the hiscores api and returns the scores of the account
    in a list and the status of the http request.
    """
    conn = http.client.HTTPSConnection('secure.runescape.com')
    conn.request("GET", "/m=hiscore_oldschool/index_lite.ws?player={}".format(account_name.replace(' ', '%20')))
    response = conn.getresponse()
    status = response.status

    data = response.read().decode('ascii')
    data = data.replace('\n', ',')
    data = data.split(',')

    conn.close()

    return {'status': status, 'data': data}

def get_account_skills_string(account_data):
    """
    Input is the json formatted account data
    Output is a string formatted table
    """
    out_string = '-----------------------------------------------\n'
    out_string += '-----------------------------------------------\n'
    out_string += '|Skill         |Rank      |Level|XP           |\n'
    out_string += '-----------------------------------------------\n'
    for element in account_data['skills']:
        rank_str = f"{int(account_data['skills'][element]['rank']):,}"
        level_str = f"{int(account_data['skills'][element]['level']):,}"
        experience_str = f"{int(account_data['skills'][element]['experience']):,}"
        line = (
            f'|{element:>14}'
            f'|{rank_str:>10}'
            f'|{level_str:>5}'
            f'|{experience_str:>13}|\n'
        )
        out_string += line
    out_string += '-----------------------------------------------\n'
    return out_string

def get_account_skills_message(account_name):
    """
    Input is the desired account name
    Output is the discord formatted message containing the accounts skill levels
    """
    print(account_name)
    stats_response = get_account_stats(account_name)
    if stats_response['status'] != 200:
        return 'Error.'
    stats_json = format_account_stats_json(stats_response['data'])
    s = get_account_skills_string(stats_json)
    return s

def add_account_to_db(account_name, db=None):
    """
    Input is the account name whos stats should be added to the db
    Output is if the operation was successful or not
    """
    stats_response = get_account_stats(account_name)
    if stats_response['status'] != 200:
        return status.ACCOUNT_DOES_NOT_EXIST
    stats_json = format_account_stats_json(stats_response['data'])
    stats_json['account_name'] = account_name
    stats_json['followers'] = []
    response = dynamodb.add_osrs_account_to_table(stats_json, db)
    return status.SUCCESS

def add_account_follower(account_name, follower, db=None):
    """
    Input is the name of the account and follower
    Output is if the operation was successful or not
    """
    if not dynamodb.in_table(account_name):
        # Add the account to the table if not already in the table
        response = add_account_to_db(account_name, db)
        if response != status.SUCCESS:
            return response

    # Add the follower if not already a follower
    response = dynamodb.get_account(account_name, db)
    followers_list = response['Item']['followers']
    if follower not in followers_list:
        response = dynamodb.add_follower(account_name, follower, db)
        return status.SUCCESS
    else:
        return status.ALREADY_FOLLOWING

def remove_account_follower(account_name, follower, db=None):
    """
    Input is the name of the account and follower
    Output is if the operation was successful or not
    """
    # Check if the account is in the db
    if not dynamodb.in_table(account_name):
        # Account is not followed by anyone
        return status.ACCOUNT_NOT_IN_DB

    # Check if the account is being followed by follower
    response = dynamodb.get_account(account_name, db)
    followers_list = response['Item']['followers']
    if follower not in followers_list:
        return status.NOT_FOLLOWING
    dynamodb.remove_follower(account_name, follower)

    # If the account has no more followers remove it from the db
    response = dynamodb.get_account(account_name, db)
    followers = response['Item']['followers']
    if len(followers) == 0:
        response = dynamodb.remove_osrs_account_from_table(account_name, db)
    return status.SUCCESS

def generate_updates(db=None):
    response = dynamodb.get_all_accounts(db)
    accounts = response['Items']
    for account_db in accounts:
        account_name = account_db['account_name']
        stats_response = get_account_stats(account_name)
        if stats_response['status'] != 200:
            # The account no longer exists??
            break
        account_api = format_account_stats_json(stats_response['data'])

        for boss in account_db['bosses']:
            diff = account_api['bosses'][boss]['score'] - int(account_db['bosses'][boss]['score'])
            if diff != 0:
                print(boss, '+', diff)

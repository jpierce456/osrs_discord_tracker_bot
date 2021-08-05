import http.client
import math
from sys import exit
import time
import boto3
from osrs_mapping import skills, activities, bosses
import dynamodb



def format_account_stats_json(account_data):
    """ Input is the ordered list of numbers from the Old School Runescape
    hiscores api
    Output is the same data formatted in a json with key values
    corresponding to the data.
    """
    counter = 0
    skills_mapping = {}
    activities_mapping = {}
    bosses_mapping = {}
    for i in range(len(skills)):
        skills_mapping[skills[i]] = {'rank': account_data[counter],
                                     'level': account_data[counter+1],
                                     'experience': account_data[counter+2]
        }
        counter+=3

    for i in range(len(activities)):
        activities_mapping[activities[i]] = {'rank': account_data[counter],
                                             'score': account_data[counter+1]
        }
        counter+=2

    for i in range(len(bosses)):
        bosses_mapping[bosses[i]] = {'rank': account_data[counter],
                                     'score': account_data[counter+1]
        }
        counter+=2

    return {'skills': skills_mapping,
            'activities': activities_mapping,
            'bosses': bosses_mapping
    }

def get_account_stats(account_name):
    """ Input is the name of the account being looked up
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
    """Input is the json formatted account data
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

def get_account_skills(account_name):

    print('getting account skills of account: ')
    print(account_name)
    stats_response = get_account_stats(account_name)
    print('Got account skills')
    if stats_response['status'] != 200:
        return 'Error.'
    print('no error, formatting')
    stats_json = format_account_stats_json(stats_response['data'])
    print('formatted into json, now formatting into string')
    s = get_account_skills_string(stats_json)
    print('formatted into string, string is: ')
    print(s)
    return s

def add_account_to_db(account_name):
    stats_response = get_account_stats(account_name)
    if stats_response['status'] != 200:
        return 'Error.'
    stats_json = format_account_stats_json(stats_response['data'])
    stats_json['account_name'] = account_name
    stats_json['followers'] = []
    dynamodb.add_to_table(stats_json)

def remove_account_from_db(account_name):
    dynamodb.remove_from_table(account_name)

def add_account_follower(account_name, follower):
    dynamodb.add_follower(account_name, follower)

def remove_account_follower(account_name, follower):
    dynamodb.remove_follower(account_name, follower)
# username = 'hey_jase'
# conn = http.client.HTTPSConnection('secure.runescape.com')
# conn.request("GET", "/m=hiscore_oldschool/index_lite.ws?player={}".format(username.replace(' ', '%20')))
# response = conn.getresponse()
# status = response.status
# # print(status)
#
# data = response.read().decode('ascii')
# data = data.replace('\n', ',')
# data = data.split(',')
# prev_subset = {}
#
# info = {}
# info['rank'] = data[0]
# info['level'] = data[1]
# info['experience'] = data[2]
# prev_subset['total'] = info
# skills = ['attack',
#           'defense',
#           'strength',
#           'hitpoints',
#           'ranged',
#           'prayer',
#           'magic',
#           'cooking',
#           'woodcutting',
#           'fletching',
#           'fishing',
#           'firemaking',
#           'crafting',
#           'smithing',
#           'mining',
#           'herblore',
#           'agility',
#           'thieving',
#           'slayer',
#           'farming',
#           'runecrafting',
#           'hunter',
#           'construction'
#            ]
#
# activities = [
#     'league_points',
#     'bounty_hunter_hunter',
#     'bounty_hunter_rogue',
#     'all_clues',
#     'beginner_clues',
#     'easy_clues',
#     'medium_clues',
#     'hard_clues',
#     'elite_clues',
#     'master_clues',
#     'last_man_standing',
#     'soul_wars_zeal',
# ]
#
# bosses = [
#     'abyssal_sire',
#     'alchemical_hydra',
#     'barrows',
#     'byrophyta',
#     'callisto',
#     'cerberus',
#     'chambers_of_xeric',
#     'chambers_of_xeric_challenge_mode',
#     'chaos_elemental',
#     'chaos_fanatic',
#     'commander_zilyana',
#     'corporeal_beast',
#     'crazy_archaeologist',
#     'dagannoth_prime',
#     'daggonoth_rex',
#     'dagonnoth_supreme',
#     'deranged_archaeologist',
#     'general_graardor',
#     'giant_mole',
#     'grotesque_guardians',
#     'hespori',
#     'kalaphite_queen',
#     'king_black_dragon',
#     'kraken',
#     'kreeArra',
#     'krilTsutsaroth',
#     'mimic',
#     'nightmare',
#     'phosanisNightmare',
#     'obor',
#     'sarachnis',
#     'scorpia',
#     'skotizo',
#     'tempoross',
#     'gauntlet',
#     'corrupted_gauntlet',
#     'theatre_of_blood',
#     'theatre_of_blood_hard_mode',
#     'thermonuclear_smoke_devil',
#     'tzKalZuk',
#     'tzTokJad',
#     'venenatis',
#     'vetion',
#     'vorkath',
#     'wintertodt',
#     'zalcano',
#     'zulrah'
# ]
#
# counter = 0
# skills_mapping = {}
# for i in range(len(skills)):
#     info = {}
#     info['rank'] = int(data[counter+3])
#     info['level'] = int(data[counter+4])
#     info['experience'] = int(data[counter+5])
#     skills_mapping[skills[i]] = info
#     counter += 3
#
# activities_mapping = {}
# for i in range(len(activities)):
#     info = {}
#     info['rank'] = int(data[counter+3])
#     info['score'] = int(data[counter+4])
#     activities_mapping[activities[i]] = info
#     counter += 2
#
# bosses_mapping = {}
# for i in range(len(bosses)):
#     info = {}
#     info['rank'] = int(data[counter+3])
#     info['score'] = int(data[counter+4])
#     bosses_mapping[bosses[i]] = info
#     counter += 2
#
# new_item = {
# 	'account_name': username,
#     'skills': skills_mapping,
#     'activities': activities_mapping,
#     'bosses': bosses_mapping,
#     'followers': ['discord_user_123']
# }
#
# db = boto3.resource('dynamodb')
# table = db.Table('osrs_account_stats')
#
# table.put_item(Item=new_item)
#
# response = table.get_item(Key={'account_name': username})
# print(response)
# item = response['Item']
# print(item)
#
# table.delete_item(Key={'account_name': username})



# for i in range(10):
#     time.sleep(120)
#
#     conn = http.client.HTTPSConnection('secure.runescape.com')
#     conn.request("GET", "/m=hiscore_oldschool/index_lite.ws?player={}".format(username.replace(' ', '%20')))
#     response = conn.getresponse()
#     status = response.status
#     print(status)
#
#     data = response.read().decode('ascii')
#     data = data.replace('\n', ',')
#     data = data.split(',')
#     curr_subset = {}
#
#     info = {}
#     info['rank'] = data[0]
#     info['level'] = data[1]
#     info['experience'] = data[2]
#     curr_subset['total'] = info
#
#     counter = 0
#     for i in range(len(skills)):
#         info = {}
#         info['rank'] = int(data[counter+3])
#         info['level'] = int(data[counter+4])
#         info['experience'] = int(data[counter+5])
#         curr_subset[skills[i]] = info
#         counter += 3
#
#     if prev_subset['total']['experience'] != curr_subset['total']['experience']:
#         for skill in skills:
#             if prev_subset[skill]['experience'] != curr_subset[skill]['experience']:
#                 diff = curr_subset[skill]['experience'] - prev_subset[skill]['experience']
#                 print('+ '+str(diff)+' '+skill)
#     else:
#         print('No change')
#
#     prev_subset = curr_subset
#

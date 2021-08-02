import http.client
import math
from sys import exit
import time
import boto3

username = 'hey_jase'
conn = http.client.HTTPSConnection('secure.runescape.com')
conn.request("GET", "/m=hiscore_oldschool/index_lite.ws?player={}".format(username.replace(' ', '%20')))
response = conn.getresponse()
status = response.status
# print(status)

data = response.read().decode('ascii')
data = data.replace('\n', ',')
data = data.split(',')
prev_subset = {}

info = {}
info['rank'] = data[0]
info['level'] = data[1]
info['experience'] = data[2]
prev_subset['total'] = info
skills = ['attack',
          'defense',
          'strength',
          'hitpoints',
          'ranged',
          'prayer',
          'magic',
          'cooking',
          'woodcutting',
          'fletching',
          'fishing',
          'firemaking',
          'crafting',
          'smithing',
          'mining',
          'herblore',
          'agility',
          'thieving',
          'slayer',
          'farming',
          'runecrafting',
          'hunter',
          'construction'
           ]

activities = [
    'league_points',
    'bounty_hunter_hunter',
    'bounty_hunter_rogue',
    'all_clues',
    'beginner_clues',
    'easy_clues',
    'medium_clues',
    'hard_clues',
    'elite_clues',
    'master_clues',
    'last_man_standing',
    'soul_wars_zeal',
]

bosses = [
    'abyssal_sire',
    'alchemical_hydra',
    'barrows',
    'byrophyta',
    'callisto',
    'cerberus',
    'chambers_of_xeric',
    'chambers_of_xeric_challenge_mode',
    'chaos_elemental',
    'chaos_fanatic',
    'commander_zilyana',
    'corporeal_beast',
    'crazy_archaeologist',
    'dagannoth_prime',
    'daggonoth_rex',
    'dagonnoth_supreme',
    'deranged_archaeologist',
    'general_graardor',
    'giant_mole',
    'grotesque_guardians',
    'hespori',
    'kalaphite_queen',
    'king_black_dragon',
    'kraken',
    'kreeArra',
    'krilTsutsaroth',
    'mimic',
    'nightmare',
    'phosanisNightmare',
    'obor',
    'sarachnis',
    'scorpia',
    'skotizo',
    'tempoross',
    'gauntlet',
    'corrupted_gauntlet',
    'theatre_of_blood',
    'theatre_of_blood_hard_mode',
    'thermonuclear_smoke_devil',
    'tzKalZuk',
    'tzTokJad',
    'venenatis',
    'vetion',
    'vorkath',
    'wintertodt',
    'zalcano',
    'zulrah'
]

counter = 0
skills_mapping = {}
for i in range(len(skills)):
    info = {}
    info['rank'] = int(data[counter+3])
    info['level'] = int(data[counter+4])
    info['experience'] = int(data[counter+5])
    skills_mapping[skills[i]] = info
    counter += 3

activities_mapping = {}
for i in range(len(activities)):
    info = {}
    info['rank'] = int(data[counter+3])
    info['score'] = int(data[counter+4])
    activities_mapping[activities[i]] = info
    counter += 2

bosses_mapping = {}
for i in range(len(bosses)):
    info = {}
    info['rank'] = int(data[counter+3])
    info['score'] = int(data[counter+4])
    bosses_mapping[bosses[i]] = info
    counter += 2

new_item = {
	'account_name': username,
    'skills': skills_mapping,
    'activities': activities_mapping,
    'bosses': bosses_mapping,
    'followers': ['discord_user_123']
}

db = boto3.resource('dynamodb')
table = db.Table('osrs_account_stats')

table.put_item(Item=new_item)

response = table.get_item(Key={'account_name': username})
print(response)
item = response['Item']
print(item)

table.delete_item(Key={'account_name': username})



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

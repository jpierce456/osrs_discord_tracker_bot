import http.client
import math
from sys import exit
import time

username = 'malfoy'
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
skills = [
			  'attack',
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
    'bounty_hunter_bounty',
    'bounty_hunter_rogue',
    'last_man_standing',
    'soul_wars_zeal',
    'all_clues',
    'beginner_clues',
    'easy_clues',
    'medium_clues',
    'hard_clues',
    'elite_clues',
    'master_clues'
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
for i in range(len(skills)):
    info = {}
    info['rank'] = int(data[counter+3])
    info['level'] = int(data[counter+4])
    info['experience'] = int(data[counter+5])
    prev_subset[skills[i]] = info
    counter += 3

skills_offset = len(skills)*3
for i in range(len(activities)):
    info = {}
    info['rank'] = int(data[counter+3])
    info['score'] = int(data[counter+4])
    prev_subset[activities[i]] = info
    counter += 2

activities_offset = len(skills)*3 + len(activities)*2
print(len(data))
for i in range(len(bosses)):
    info = {}
    info['rank'] = int(data[counter+3])
    info['score'] = int(data[counter+4])
    prev_subset[bosses[i]] = info
    counter += 2

print(data)
print(prev_subset)

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

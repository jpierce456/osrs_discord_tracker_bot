import unittest
import boto3
import moto
import dynamodb
import osrs
import status

@moto.mock_dynamodb2
class TestDatabaseFunctions(unittest.TestCase):

    def setUp(self):
        """
        Create database resource and mock table
        """
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.create_table(
            TableName='osrs_account_stats',
            KeySchema=[
                {
                    'AttributeName': 'account_name',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                'AttributeName': 'account_name',
                'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        self.test_osrs_account_stats = {
            'account_name': 'test_account_123',
            'followers': [],
            'skills': {
                'overall': {
                    'rank': 1,
                    'level': 2277,
                    'experience': 4600000000
                },
                'mining': {
                    'rank': 1,
                    'level': 99,
                    'experience': 200000000
                }
            },
            'activities': {
                'hard_clues': {
                    'rank': 100,
                    'score': 1000
                }
            },
            'bosses': {
                'inferno': {
                    'rank': 73,
                    'score': 7373
                }
            }
        }
        self.test_osrs_account_stats_second = {
            'account_name': 'second_test_account',
            'followers': [],
            'skills': {
                'overall': {
                    'rank': 73,
                    'level': 2277,
                    'experience': 4321000000
                },
                'attack': {
                    'rank': 1,
                    'level': 99,
                    'experience': 200000000
                }
            },
            'activities': {
                'last_man_standing': {
                    'rank': 22,
                    'score': 2222
                }
            },
            'bosses': {
                'barrows': {
                    'rank': 39,
                    'score': 3030
                }
            }
        }

    def tearDown(self):
        """
        Delete database resource and mock table
        """
        self.table.delete()
        self.dynamodb=None

    def test_table_exists(self):
        """
        Test if our mock table is ready
        """
        self.assertIn('osrs_account_stats', self.table.name)

    def test_get_real_account_stats_api(self):
        """
        Test getting an existing accounts stats from the osrs api
        """
        response = osrs.get_account_stats('Lynx Titan')
        self.assertEqual(200, response['status'])
        self.assertEqual('1', response['data'][0])
        self.assertEqual('2277', response['data'][1])
        self.assertEqual('4600000000', response['data'][2])

    def test_get_fake_account_stats_api(self):
        """
        Test getting a fake account stats from the osrs api
        """
        response = osrs.get_account_stats('FakeAccount12345')
        self.assertEqual(404, response['status'])

    def test_format_account_stats_json(self):
        """
        Test formatting the account stats into a json and removing unranked attributes
        """
        response = osrs.get_account_stats('Lynx Titan')
        self.assertEqual(200, response['status'])

        json = osrs.format_account_stats_json(response['data'])
        self.assertEqual(1, len(json['bosses']))
        self.assertEqual(2, len(json['activities']))
        self.assertTrue('fight_caves' in json['bosses'])
        self.assertFalse('inferno' in json['bosses'])
        self.assertTrue('hard_clues' in json['activities'])
        self.assertFalse('master_clues' in json['activities'])

    def test_add_osrs_account_to_table(self):
        """
        Test adding an osrs account to the table
        """
        response = dynamodb.add_osrs_account_to_table(self.test_osrs_account_stats, self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])

    def test_get_osrs_account_from_table(self):
        """
        Test getting an account from the table
        """
        response = dynamodb.add_osrs_account_to_table(self.test_osrs_account_stats, self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        response = dynamodb.get_account('test_account_123', self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])

        self.assertEqual(4600000000, response['Item']['skills']['overall']['experience'])
        self.assertEqual(200000000, response['Item']['skills']['mining']['experience'])
        self.assertEqual(100, response['Item']['activities']['hard_clues']['rank'])
        self.assertEqual(73, response['Item']['bosses']['inferno']['rank'])

        response = dynamodb.get_account('Fake_Account_12345', self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        self.assertFalse('Item' in response)

    def test_get_all_osrs_account_from_table(self):
        """
        Test getting all accounts from the table
        """
        response = dynamodb.add_osrs_account_to_table(self.test_osrs_account_stats, self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        response = dynamodb.add_osrs_account_to_table(self.test_osrs_account_stats_second, self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])

        response = dynamodb.get_all_accounts(self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        self.assertEqual(2, len(response['Items']))

    def test_remove_osrs_account_from_table(self):
        """
        Test removing an account from the table
        """
        response = dynamodb.add_osrs_account_to_table(self.test_osrs_account_stats, self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        response = dynamodb.get_account('test_account_123', self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        self.assertTrue(dynamodb.in_table('test_account_123', self.dynamodb))

        response = dynamodb.remove_osrs_account_from_table('test_account_123')
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        self.assertFalse(dynamodb.in_table('test_account_123', self.dynamodb))

    def test_add_follower_to_account(self):
        """
        Test adding a follower to an account in the table
        """
        response = dynamodb.add_osrs_account_to_table(self.test_osrs_account_stats, self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        response = dynamodb.get_account('test_account_123', self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        self.assertTrue(dynamodb.in_table('test_account_123', self.dynamodb))

        response = dynamodb.add_follower('test_account_123', 'test_follower_456', self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        response = dynamodb.get_account('test_account_123', self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        self.assertTrue('Item' in response)
        self.assertEqual(['test_follower_456'], response['Item']['followers'])

    def test_remove_follower_from_account(self):
        """
        Test removing a follower from an account in the table
        """
        response = dynamodb.add_osrs_account_to_table(self.test_osrs_account_stats, self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])

        response = dynamodb.add_follower('test_account_123', 'test_follower_456', self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])

        response = dynamodb.get_account('test_account_123', self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        self.assertTrue('test_follower_456' in response['Item']['followers'])

        response = dynamodb.remove_follower('test_account_123', 'test_follower_456', self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])

        response = dynamodb.get_account('test_account_123', self.dynamodb)
        self.assertEqual(200, response['ResponseMetadata']['HTTPStatusCode'])
        self.assertFalse('test_follower_456' in response['Item']['followers'])

    def test_add_non_existing_accout_request(self):
        """
        Test a call to add a non-existing accout to the database
        """
        response = osrs.add_account_to_db('Non_existing_account', self.dynamodb)
        self.assertEqual(status.ACCOUNT_DOES_NOT_EXIST, response)

    def test_add_valid_account_request(self):
        """
        Test a call to add a valid, existing account to the database
        """
        response = osrs.add_account_to_db('Lynx Titan', self.dynamodb)
        self.assertEqual(status.SUCCESS, response)

    def test_add_follower_to_non_existing_account(self):
        """
        Test trying to add a follower to an account that does not exist
        """
        response = osrs.add_account_follower('Non_existing_account', self.dynamodb)
        self.assertEqual(status.ACCOUNT_DOES_NOT_EXIST, response)

    def test_add_follower_to_account_already_following(self):
        """
        Test trying to add a follower to an already followed account
        """
        response = osrs.add_account_follower('Lynx Titan', 'test_follower_456', self.dynamodb)
        response = osrs.add_account_follower('Lynx Titan', 'test_follower_456', self.dynamodb)
        self.assertEqual(status.ALREADY_FOLLOWING, response)

    def test_add_follower_to_existing_account(self):
        """
        Test trying to add a follower to an account
        """
        response = osrs.add_account_follower('Lynx Titan', 'test_follower_456', self.dynamodb)
        self.assertEqual(status.SUCCESS, response)
        response = osrs.add_account_follower('Lynx Titan', 'test_follower_789', self.dynamodb)
        self.assertEqual(status.SUCCESS, response)

    def test_remove_follower_from_non_existing_account(self):
        """
        Test trying to remove a follower from an account not in the database
        """
        response = osrs.remove_account_follower('Lynx Titan', 'test_follower_456', self.dynamodb)
        self.assertEqual(status.ACCOUNT_NOT_IN_DB, response)

    def test_remove_follower_from_non_followed_account(self):
        """
        Test trying to remove a follower from an account that is not followed
        """
        response = osrs.add_account_follower('Lynx Titan', 'test_follower_456', self.dynamodb)
        self.assertEqual(status.SUCCESS, response)

        response = osrs.remove_account_follower('Lynx Titan', 'different_follower_789', self.dynamodb)
        self.assertEqual(status.NOT_FOLLOWING, response)

    def test_remove_follower_from_existing_account(self):
        """
        Test removing a follower from an account and removing the account from the db when it has no followers
        """
        response = osrs.add_account_follower('Lynx Titan', 'test_follower_456', self.dynamodb)
        self.assertEqual(status.SUCCESS, response)
        response = osrs.add_account_follower('Lynx Titan', 'test_follower_789', self.dynamodb)
        self.assertEqual(status.SUCCESS, response)

        self.assertTrue(dynamodb.in_table('Lynx Titan', self.dynamodb))
        response = dynamodb.get_account('Lynx Titan', self.dynamodb)
        followers_list = response['Item']['followers']
        self.assertTrue('test_follower_456' in followers_list)
        self.assertTrue('test_follower_789' in followers_list)

        # Remove 1 follower
        response = osrs.remove_account_follower('Lynx Titan', 'test_follower_456', self.dynamodb)
        self.assertEqual(status.SUCCESS, response)
        self.assertTrue(dynamodb.in_table('Lynx Titan', self.dynamodb))
        response = dynamodb.get_account('Lynx Titan', self.dynamodb)
        followers_list = response['Item']['followers']
        self.assertFalse('test_follower_456' in followers_list)
        self.assertTrue('test_follower_789' in followers_list)

        # Remove the other follower, this should delete the account from the db
        response = osrs.remove_account_follower('Lynx Titan', 'test_follower_789', self.dynamodb)
        self.assertEqual(status.SUCCESS, response)
        self.assertFalse(dynamodb.in_table('Lynx Titan', self.dynamodb))



if __name__ == '__main__':
    unittest.main()

import unittest
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import pyholaclient

class TestHolaClient(unittest.TestCase):
    def test_init(self):
        client = pyholaclient.HolaClient('http://localhost', '123')
        self.assertEqual(client.api_url, 'http://localhost')
        self.assertEqual(client.api_key, '123')
        # Print status of the test
        print('TestHolaClient.test_init: OK')
    def test_user(self):
        client = pyholaclient.HolaClient('http://localhost', '123')
        user = client.user_info('0000')
        self.assertEqual(user.email, 'example@gmail.com')
        print('TestHolaClient.test_user Email: OK')
        self.assertEqual(user.first_name, 'CR072')
        print('TestHolaClient.test_user First Name: OK')
        self.assertEqual(user.last_name, 'discord-auth')
        print('TestHolaClient.test_user Last Name: OK')
        self.assertEqual(user.username, 'crazymath072')
        print('TestHolaClient.test_user Username: OK')
        self.assertEqual(user.language, 'en')
        print('TestHolaClient.test_user Language: OK')
        self.assertEqual(user.id, 2)
        print('TestHolaClient.test_user ID: OK')
        self.assertEqual(user.external_id, None)
        print('TestHolaClient.test_user External ID: OK')
        self.assertEqual(user.root_admin, True)
        print('TestHolaClient.test_user Root Admin: OK')
        self.assertEqual(user.twofa_enabled, False)
        print('TestHolaClient.test_user 2FA: OK')
        self.assertEqual(user.uuid, '365153fc-xxx-xxx-xxx-xxxx')
        print('TestHolaClient.test_user UUID: OK')
        self.assertEqual(user.created_at, '2023-07-21T14:51:13+00:00')
        print('TestHolaClient.test_user Created At: OK')
        self.assertEqual(user.updated_at, '2023-07-28T08:46:27+00:00')
        print('TestHolaClient.test_user Updated At: OK')
        self.assertEqual(user.relationships, {})
        print('TestHolaClient.test_user Relationships: OK')
    def test_user_package(self):
        client = pyholaclient.HolaClient('http://localhost', '123')
        package = client.user_package(1111)
        self.assertEqual(package, 'Default')
        print('TestHolaClient.test_user_package Name: OK')
    def test_setcoins(self):
        client = pyholaclient.HolaClient('http://localhost', '123')
        status = client.set_coins('1111', 100)
        self.assertEqual(status, True)
        print('TestHolaClient.test_setcoins: OK')
    def test_addcoins(self):
        client = pyholaclient.HolaClient('http://localhost', '123')
        status = client.add_coins('1111', 100)
        self.assertEqual(status, True)
        print('TestHolaClient.test_addcoins: OK')
    def test_create_coupon(self):
        client = pyholaclient.HolaClient('http://localhost', '123')
        coupon = client.create_coupon(100, 1024, 1024, 1, 1, 1, 1, 1, 1)
        self.assertEqual(coupon.coins, 100)
        print('TestHolaClient.test_create_coupon Coins: OK')
        self.assertEqual(coupon.ram, 1024)
        print('TestHolaClient.test_create_coupon RAM: OK')
        self.assertEqual(coupon.disk, 1024)
        print('TestHolaClient.test_create_coupon Disk: OK')
        self.assertEqual(coupon.cpu, 1)
        print('TestHolaClient.test_create_coupon CPU: OK')
        self.assertEqual(coupon.servers, 1)
        print('TestHolaClient.test_create_coupon Servers: OK')
        self.assertEqual(coupon.backups, 1)
        print('TestHolaClient.test_create_coupon Backups: OK')
        self.assertEqual(coupon.allocation, 1)
        print('TestHolaClient.test_create_coupon Allocations: OK')
        self.assertEqual(coupon.database, 1)
        print('TestHolaClient.test_create_coupon Databases: OK')
        self.assertEqual(coupon.uses, 1)
        print('TestHolaClient.test_create_coupon Uses: OK')
    def get_usr_hcid(self):
        client = pyholaclient.HolaClient('http://localhost', '123')
        hcid = client.get_usr_hcid(1114012186877120643)
        self.assertEqual(hcid, 1111)
        print('TestHolaClient.test_get_usr_hcid: OK')

if __name__ == '__main__':
    unittest.main()

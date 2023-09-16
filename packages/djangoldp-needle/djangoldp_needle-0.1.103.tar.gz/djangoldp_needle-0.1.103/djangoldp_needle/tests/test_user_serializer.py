from djangoldp_account.models import LDPUser
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase

from ..models import NeedleUserContact


class TestUserSerializer(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def buildUser(self, username):
        user = LDPUser(email=username + '@test.startinblox.com', first_name='Test', last_name='Mactest',
                       username=username,
                       password='glass onion')
        user.save()

        account = user.account
        account.picture = 'picture'
        account.save()

        return user

    def test_user_serialize_self(self):
        user1 = self.buildUser('user1')

        self.client.force_authenticate(user1)
        response = self.client.get("/users/user1/")
        responseJson = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue('first_name' in responseJson)
        self.assertTrue('last_name' in responseJson)
        self.assertTrue('name' in responseJson)
        self.assertTrue('email' in responseJson)
        self.assertEqual('picture', responseJson['account']['picture'])


    def test_user_serialize_other_non_contact(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        self.client.force_authenticate(user1)
        response = self.client.get("/users/user2/")
        responseJson = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertFalse('first_name' in responseJson)
        self.assertFalse('last_name' in responseJson)
        self.assertFalse('name' in responseJson)
        self.assertFalse('email' in responseJson)
        self.assertEqual(None, responseJson['account']['picture'])

    def test_user_serialize_other_contact_not_validated(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        NeedleUserContact(contact_from=user1, contact_to=user2).save()

        self.client.force_authenticate(user1)
        response = self.client.get("/users/user2/")
        responseJson = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertFalse('first_name' in responseJson)
        self.assertFalse('last_name' in responseJson)
        self.assertFalse('name' in responseJson)
        self.assertFalse('email' in responseJson)
        self.assertEqual(None, responseJson['account']['picture'])

    def test_user_serialize_other_contact_validated(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        contact = NeedleUserContact(contact_from=user1, contact_to=user2)
        contact.save()
        contact.invitation_token = None
        contact.save()

        self.client.force_authenticate(user1)
        response = self.client.get("/users/user2/")
        responseJson = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue('first_name' in responseJson)
        self.assertTrue('last_name' in responseJson)
        self.assertTrue('name' in responseJson)
        self.assertTrue('email' in responseJson)
        self.assertEqual('picture', responseJson['account']['picture'])

    def test_account_serialize_self(self):
        user1 = self.buildUser('user1')

        self.client.force_authenticate(user1)
        response = self.client.get("/accounts/user1/")
        responseJson = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual('picture', responseJson['picture'])


    def test_account_serialize_other_non_contact(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        self.client.force_authenticate(user1)
        response = self.client.get("/accounts/user2/")
        responseJson = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(None, responseJson['picture'])

    def test_account_serialize_other_contact_not_validated(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')
        NeedleUserContact(contact_from=user1, contact_to=user2).save()

        self.client.force_authenticate(user1)
        response = self.client.get("/accounts/user2/")
        responseJson = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(None, responseJson['picture'])

    def test_account_serialize_other_contact_validated(self):
        user1 = self.buildUser('user1')
        user2 = self.buildUser('user2')

        contact = NeedleUserContact(contact_from=user1, contact_to=user2)
        contact.save()
        contact.invitation_token = None
        contact.save()

        self.client.force_authenticate(user1)
        response = self.client.get("/accounts/user2/")
        responseJson = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual('picture', responseJson['picture'])